#!/usr/bin/env python3
"""
Carga tablas market_sudeaseg_* desde Excel SUDEASEG (12 hojas mensuales por archivo).

- Columnas sin sufijo _mes: valores **acumulados YTD** tal como publica cada hoja
  («AL 31 DE …» / acumulado a esa fecha).
- Columnas *_mes: **incremento** respecto al acumulado del **último mes anterior
  del mismo año** con dato para esa empresa (si no hay mes previo en el año, el
  incremento = YTD de ese mes, p. ej. primera aparición en el año).

Uso:
  set DATABASE_URL=postgresql+psycopg://...
  python scripts/etl_sudeaseg.py --data-dir Info/data-sudeaseg/xlsx
  python scripts/etl_sudeaseg.py --data-dir ... --dry-run
  python scripts/etl_sudeaseg.py --data-dir ... --december-only   # solo 1 mes (sin *_mes útil)

Migraciones: 002_market_sudeaseg.sql y 003_market_sudeaseg_monthly.sql
Requisitos: scripts/requirements-etl.txt
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

MANIFEST: list[dict[str, Any]] = [
    {"file": "resumen-por-empresa-2023.xlsx", "kind": "resumen", "year": 2023},
    {"file": "Dic%20resumen-por-empresa-2024.xlsx", "kind": "resumen", "year": 2024},
    {"file": "2_Resumen_por_Empresa_Dic.xlsx", "kind": "resumen", "year": 2025},
    {"file": "cuadros-de-resultados-2023.xlsx", "kind": "cuadro", "year": 2023},
    {"file": "Dic%20cuadro-de-resultados-2024.xlsx", "kind": "cuadro", "year": 2024},
    {"file": "1_Cuadro_de_Resultados_Dic.xlsx", "kind": "cuadro", "year": 2025},
]

# Orden calendario (Enero → Diciembre); nombres como en el xlsx.
MONTH_SHEETS: list[tuple[str, int]] = [
    ("Enero", 1),
    ("Febrero", 2),
    ("Marzo", 3),
    ("Abril", 4),
    ("Mayo", 5),
    ("Junio", 6),
    ("Julio", 7),
    ("Agosto", 8),
    ("Septiembre", 9),
    ("Octubre", 10),
    ("Noviembre", 11),
    ("Diciembre", 12),
]

RESUMEN_YTD_KEYS: tuple[str, ...] = (
    "primas_netas_cobradas",
    "siniestros_pagados",
    "reservas_psp_brutas",
    "reservas_psp_netas_reaseg",
    "siniestros_totales",
    "comisiones",
    "gastos_adquisicion",
    "gastos_administracion",
)

CUADRO_YTD_KEYS: tuple[str, ...] = (
    "primas_netas_cobradas",
    "resultado_tecnico_bruto",
    "resultado_reaseguro_cedido",
    "resultado_tecnico_neto",
    "resultado_gestion_general",
    "saldo_operaciones",
)

_MESES_HINT = (
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
    "ACUMULADA",
    "AL 31",
    "AL 30",
    "AL 28",
    "AL 29",
)


def _norm_pg_url(url: str) -> str:
    u = url.strip()
    if u.startswith("postgresql://") and "+psycopg" not in u.split("://", 1)[0]:
        return "postgresql+psycopg://" + u.removeprefix("postgresql://")
    return u


def _sanitize_database_url(url: str) -> str:
    u = url.strip().strip("\ufeff")
    u = u.replace("\r", "").replace("\n", "")
    return u.strip()


def _norm_empresa_name(name: str) -> str:
    """Clave estable entre hojas (comas, espacios dobles, etc. varían en SUDEASEG). Conserva ñ/acentos."""
    t = str(name).lower().strip()
    t = re.sub(r"[,;]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _to_decimal(v: Any) -> Decimal | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, Decimal):
        return v
    try:
        if pd.isna(v):
            return None
    except TypeError:
        pass
    try:
        return Decimal(str(v))
    except Exception:
        return None


def _year_from_sheet(df: pd.DataFrame, fallback: int) -> int:
    pat = re.compile(r"(20\d{2})")
    for r in range(min(14, len(df))):
        for c in range(min(df.shape[1], 8)):
            val = df.iloc[r, c]
            if pd.isna(val):
                continue
            s = (
                str(val)
                .upper()
                .replace("Á", "A")
                .replace("É", "E")
                .replace("Í", "I")
                .replace("Ó", "O")
                .replace("Ú", "U")
            )
            if not any(h in s for h in _MESES_HINT):
                continue
            m = pat.search(s)
            if m:
                return int(m.group(1))
    return fallback


def _is_resumen_data_row(rank: Any, name: Any) -> bool:
    if pd.isna(name):
        return False
    nm = str(name).strip()
    if len(nm) < 4:
        return False
    low = nm.lower()
    if "consignaron" in low or low.startswith("(1)") or "aportaciones econ" in low:
        return False
    try:
        r = int(float(rank))
        return r >= 1
    except (TypeError, ValueError):
        return False


def _parse_resumen_sheet(
    df: pd.DataFrame, source_file: str, year_fallback: int, period_month: int
) -> list[dict[str, Any]]:
    y = _year_from_sheet(df, year_fallback)
    rows_out: list[dict[str, Any]] = []
    header_row = 8
    for i in range(header_row + 1, len(df)):
        rank = df.iloc[i, 1]
        name = df.iloc[i, 2]
        if not _is_resumen_data_row(rank, name):
            continue
        rows_out.append(
            {
                "source_file": source_file,
                "period_year": y,
                "period_month": period_month,
                "empresa_rank": int(float(rank)),
                "empresa_nombre": str(name).strip(),
                "empresa_nombre_norm": _norm_empresa_name(str(name)),
                "primas_netas_cobradas": _to_decimal(df.iloc[i, 3]),
                "siniestros_pagados": _to_decimal(df.iloc[i, 4]),
                "reservas_psp_brutas": _to_decimal(df.iloc[i, 5]),
                "reservas_psp_netas_reaseg": _to_decimal(df.iloc[i, 6]),
                "siniestros_totales": _to_decimal(df.iloc[i, 7]),
                "comisiones": _to_decimal(df.iloc[i, 8]),
                "gastos_adquisicion": _to_decimal(df.iloc[i, 9]),
                "gastos_administracion": _to_decimal(df.iloc[i, 10])
                if df.shape[1] > 10
                else None,
            }
        )
    return rows_out


def _cuadro_data_start_row(df: pd.DataFrame) -> int:
    for i in range(8, min(len(df), 75)):
        rank = df.iloc[i, 1]
        name = df.iloc[i, 2]
        if _is_resumen_data_row(rank, name):
            return i
    return 12


def _parse_cuadro_sheet(
    df: pd.DataFrame, source_file: str, year_fallback: int, period_month: int
) -> list[dict[str, Any]]:
    y = _year_from_sheet(df, year_fallback)
    ncols = df.shape[1]
    start = _cuadro_data_start_row(df)
    wide = ncols >= 9
    rows_out: list[dict[str, Any]] = []
    for i in range(start, len(df)):
        rank = df.iloc[i, 1]
        name = df.iloc[i, 2]
        if not _is_resumen_data_row(rank, name):
            continue
        if wide:
            primas = _to_decimal(df.iloc[i, 3])
            rtb = _to_decimal(df.iloc[i, 4])
            reaseg = _to_decimal(df.iloc[i, 5])
            rtn = _to_decimal(df.iloc[i, 6])
            gest = _to_decimal(df.iloc[i, 7])
            saldo = _to_decimal(df.iloc[i, 8])
        else:
            primas = None
            rtb = _to_decimal(df.iloc[i, 3])
            reaseg = _to_decimal(df.iloc[i, 4])
            rtn = _to_decimal(df.iloc[i, 5])
            gest = _to_decimal(df.iloc[i, 6])
            saldo = _to_decimal(df.iloc[i, 7])
        rows_out.append(
            {
                "source_file": source_file,
                "period_year": y,
                "period_month": period_month,
                "empresa_rank": int(float(rank)),
                "empresa_nombre": str(name).strip(),
                "empresa_nombre_norm": _norm_empresa_name(str(name)),
                "primas_netas_cobradas": primas,
                "resultado_tecnico_bruto": rtb,
                "resultado_reaseguro_cedido": reaseg,
                "resultado_tecnico_neto": rtn,
                "resultado_gestion_general": gest,
                "saldo_operaciones": saldo,
            }
        )
    return rows_out


def _latest_month_before(by_month: dict[int, Any], m: int) -> int | None:
    for p in range(m - 1, 0, -1):
        if p in by_month:
            return p
    return None


def _dec_sub(a: Decimal | None, b: Decimal | None) -> Decimal | None:
    aa = Decimal(0) if a is None else a
    bb = Decimal(0) if b is None else b
    return aa - bb


def _apply_mes_from_ytd(
    by_month: dict[int, dict[str, Any]], ytd_keys: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Añade claves *_mes a cada fila almacenada por mes."""
    out: list[dict[str, Any]] = []
    for m in sorted(by_month.keys()):
        row = dict(by_month[m])
        prev_m = _latest_month_before(by_month, m)
        for k in ytd_keys:
            cur = row.get(k)
            if prev_m is None:
                row[f"{k}_mes"] = cur
            else:
                pv = by_month[prev_m].get(k)
                row[f"{k}_mes"] = _dec_sub(
                    cur if isinstance(cur, Decimal) or cur is None else _to_decimal(cur),
                    pv if isinstance(pv, Decimal) or pv is None else _to_decimal(pv),
                )
        out.append(row)
    return out


def _load_resumen_workbook(path: Path, source_file: str, year_fallback: int, december_only: bool) -> list[dict[str, Any]]:
    xl = pd.ExcelFile(path, engine="openpyxl")
    if december_only:
        if "Diciembre" not in xl.sheet_names:
            print(f"  AVISO: sin hoja Diciembre en {source_file}", file=sys.stderr)
            return []
        df = pd.read_excel(path, sheet_name="Diciembre", header=None, engine="openpyxl")
        flat: list[dict[str, Any]] = []
        for row in _parse_resumen_sheet(df, source_file, year_fallback, 12):
            for k in RESUMEN_YTD_KEYS:
                row[f"{k}_mes"] = None
            flat.append(row)
        return flat

    acc: dict[str, dict[int, dict[str, Any]]] = {}
    for sheet_name, mnum in MONTH_SHEETS:
        if sheet_name not in xl.sheet_names:
            print(f"  AVISO: sin hoja {sheet_name!r} en {source_file}", file=sys.stderr)
            continue
        df = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="openpyxl")
        for row in _parse_resumen_sheet(df, source_file, year_fallback, mnum):
            norm = row["empresa_nombre_norm"]
            acc.setdefault(norm, {})
            slim = {k: row[k] for k in RESUMEN_YTD_KEYS if k in row}
            acc[norm][mnum] = {
                "source_file": row["source_file"],
                "period_year": row["period_year"],
                "period_month": mnum,
                "empresa_rank": row["empresa_rank"],
                "empresa_nombre": row["empresa_nombre"],
                "empresa_nombre_norm": norm,
                **slim,
            }
    out: list[dict[str, Any]] = []
    for _norm, by_m in acc.items():
        out.extend(_apply_mes_from_ytd(by_m, RESUMEN_YTD_KEYS))
    return out


def _load_cuadro_workbook(path: Path, source_file: str, year_fallback: int, december_only: bool) -> list[dict[str, Any]]:
    xl = pd.ExcelFile(path, engine="openpyxl")
    if december_only:
        if "Diciembre" not in xl.sheet_names:
            print(f"  AVISO: sin hoja Diciembre en {source_file}", file=sys.stderr)
            return []
        df = pd.read_excel(path, sheet_name="Diciembre", header=None, engine="openpyxl")
        flat: list[dict[str, Any]] = []
        for row in _parse_cuadro_sheet(df, source_file, year_fallback, 12):
            for k in CUADRO_YTD_KEYS:
                row[f"{k}_mes"] = None
            flat.append(row)
        return flat

    acc: dict[str, dict[int, dict[str, Any]]] = {}
    for sheet_name, mnum in MONTH_SHEETS:
        if sheet_name not in xl.sheet_names:
            print(f"  AVISO: sin hoja {sheet_name!r} en {source_file}", file=sys.stderr)
            continue
        df = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="openpyxl")
        for row in _parse_cuadro_sheet(df, source_file, year_fallback, mnum):
            norm = row["empresa_nombre_norm"]
            acc.setdefault(norm, {})
            slim = {k: row[k] for k in CUADRO_YTD_KEYS if k in row}
            acc[norm][mnum] = {
                "source_file": row["source_file"],
                "period_year": row["period_year"],
                "period_month": mnum,
                "empresa_rank": row["empresa_rank"],
                "empresa_nombre": row["empresa_nombre"],
                "empresa_nombre_norm": norm,
                **slim,
            }
    out: list[dict[str, Any]] = []
    for _norm, by_m in acc.items():
        out.extend(_apply_mes_from_ytd(by_m, CUADRO_YTD_KEYS))
    return out


def load_workbook_rows(
    data_dir: Path, entry: dict[str, Any], december_only: bool
) -> list[dict[str, Any]]:
    path = data_dir / entry["file"]
    if not path.is_file():
        raise FileNotFoundError(f"No existe: {path}")
    yf = int(entry["year"])
    if entry["kind"] == "resumen":
        return _load_resumen_workbook(path, entry["file"], yf, december_only)
    if entry["kind"] == "cuadro":
        return _load_cuadro_workbook(path, entry["file"], yf, december_only)
    raise ValueError(entry["kind"])


SQL_DELETE_RESUMEN = text("delete from public.market_sudeaseg_resumen_empresa where source_file = :sf")
SQL_DELETE_CUADRO = text("delete from public.market_sudeaseg_cuadro_resultados where source_file = :sf")

SQL_INSERT_RESUMEN = text(
    """
    insert into public.market_sudeaseg_resumen_empresa (
      source_file, period_year, period_month, empresa_rank, empresa_nombre, empresa_nombre_norm,
      primas_netas_cobradas, siniestros_pagados, reservas_psp_brutas, reservas_psp_netas_reaseg,
      siniestros_totales, comisiones, gastos_adquisicion, gastos_administracion,
      primas_netas_cobradas_mes, siniestros_pagados_mes, reservas_psp_brutas_mes, reservas_psp_netas_reaseg_mes,
      siniestros_totales_mes, comisiones_mes, gastos_adquisicion_mes, gastos_administracion_mes
    ) values (
      :source_file, :period_year, :period_month, :empresa_rank, :empresa_nombre, :empresa_nombre_norm,
      :primas_netas_cobradas, :siniestros_pagados, :reservas_psp_brutas, :reservas_psp_netas_reaseg,
      :siniestros_totales, :comisiones, :gastos_adquisicion, :gastos_administracion,
      :primas_netas_cobradas_mes, :siniestros_pagados_mes, :reservas_psp_brutas_mes, :reservas_psp_netas_reaseg_mes,
      :siniestros_totales_mes, :comisiones_mes, :gastos_adquisicion_mes, :gastos_administracion_mes
    )
    """
)

SQL_INSERT_CUADRO = text(
    """
    insert into public.market_sudeaseg_cuadro_resultados (
      source_file, period_year, period_month, empresa_rank, empresa_nombre, empresa_nombre_norm,
      primas_netas_cobradas, resultado_tecnico_bruto, resultado_reaseguro_cedido,
      resultado_tecnico_neto, resultado_gestion_general, saldo_operaciones,
      primas_netas_cobradas_mes, resultado_tecnico_bruto_mes, resultado_reaseguro_cedido_mes,
      resultado_tecnico_neto_mes, resultado_gestion_general_mes, saldo_operaciones_mes
    ) values (
      :source_file, :period_year, :period_month, :empresa_rank, :empresa_nombre, :empresa_nombre_norm,
      :primas_netas_cobradas, :resultado_tecnico_bruto, :resultado_reaseguro_cedido,
      :resultado_tecnico_neto, :resultado_gestion_general, :saldo_operaciones,
      :primas_netas_cobradas_mes, :resultado_tecnico_bruto_mes, :resultado_reaseguro_cedido_mes,
      :resultado_tecnico_neto_mes, :resultado_gestion_general_mes, :saldo_operaciones_mes
    )
    """
)


def upsert_engine(
    engine: Engine | None, rows: list[dict[str, Any]], kind: str, dry_run: bool
) -> int:
    if not rows:
        return 0
    sf = rows[0]["source_file"]
    if dry_run:
        print(f"  [dry-run] {kind} {sf!r}: {len(rows)} filas")
        return len(rows)
    assert engine is not None
    del_sql = SQL_DELETE_RESUMEN if kind == "resumen" else SQL_DELETE_CUADRO
    ins_sql = SQL_INSERT_RESUMEN if kind == "resumen" else SQL_INSERT_CUADRO
    with engine.begin() as conn:
        conn.execute(del_sql, {"sf": sf})
        for r in rows:
            conn.execute(ins_sql, r)
    print(f"  {kind} {sf!r}: {len(rows)} filas cargadas")
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="ETL SUDEASEG → Postgres (market_sudeaseg_*).")
    ap.add_argument(
        "--data-dir",
        type=Path,
        default=Path("Info/data-sudeaseg/xlsx"),
        help="Carpeta con los xlsx",
    )
    ap.add_argument("--dry-run", action="store_true", help="Solo parsear e imprimir conteos")
    ap.add_argument(
        "--december-only",
        action="store_true",
        help="Solo hoja Diciembre (comportamiento antiguo; *_mes = YTD de ese mes)",
    )
    ap.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL", ""),
        help="Postgres URL (o variable DATABASE_URL)",
    )
    args = ap.parse_args()
    data_dir = args.data_dir.resolve()
    if not data_dir.is_dir():
        print(f"ERROR: data-dir no es carpeta: {data_dir}", file=sys.stderr)
        return 1

    engine: Engine | None = None
    if not args.dry_run:
        raw_url = _sanitize_database_url(args.database_url)
        if not raw_url:
            print("ERROR: defina DATABASE_URL o --database-url", file=sys.stderr)
            return 1
        url_n = _norm_pg_url(raw_url)
        engine = create_engine(
            url_n,
            pool_pre_ping=True,
            connect_args={"prepare_threshold": None} if "psycopg" in url_n else {},
        )
        try:
            with engine.connect() as conn:
                conn.execute(text("select 1"))
        except UnicodeError as e:
            print(
                "ERROR: la URL de base de datos tiene caracteres inválidos o invisibles en el host.\n"
                f"  Detalle: {e}",
                file=sys.stderr,
            )
            return 1
        except Exception as e:  # noqa: BLE001
            print(f"ERROR: no se pudo conectar a Postgres: {e}", file=sys.stderr)
            return 1

    total = 0
    for entry in MANIFEST:
        try:
            rows = load_workbook_rows(data_dir, entry, args.december_only)
        except FileNotFoundError as e:
            print(f"AVISO: {e}", file=sys.stderr)
            continue
        kind = entry["kind"]
        upsert_engine(engine, rows, kind, args.dry_run)
        total += len(rows)

    print(f"Listo. Total filas procesadas: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
