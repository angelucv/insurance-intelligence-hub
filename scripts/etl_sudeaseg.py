#!/usr/bin/env python3
"""
Carga tablas market_sudeaseg_* desde los Excel SUDEASEG (hoja Diciembre).

Uso:
  set DATABASE_URL=postgresql+psycopg://...
  python scripts/etl_sudeaseg.py --data-dir Info/data-sudeaseg/xlsx

  python scripts/etl_sudeaseg.py --data-dir ... --dry-run

Requisitos: pandas, openpyxl, sqlalchemy, psycopg (ver scripts/requirements-etl.txt).
Aplicar antes en Postgres: supabase/migrations/002_market_sudeaseg.sql
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

# Archivos acordados (ventana 2023–2025); nombres literales en disco (incl. Dic%20...).
MANIFEST: list[dict[str, Any]] = [
    {"file": "resumen-por-empresa-2023.xlsx", "kind": "resumen", "year": 2023},
    {"file": "Dic%20resumen-por-empresa-2024.xlsx", "kind": "resumen", "year": 2024},
    {"file": "2_Resumen_por_Empresa_Dic.xlsx", "kind": "resumen", "year": 2025},
    {"file": "cuadros-de-resultados-2023.xlsx", "kind": "cuadro", "year": 2023},
    {"file": "Dic%20cuadro-de-resultados-2024.xlsx", "kind": "cuadro", "year": 2024},
    {"file": "1_Cuadro_de_Resultados_Dic.xlsx", "kind": "cuadro", "year": 2025},
]

SHEET = "Diciembre"
MONTH = 12


def _norm_pg_url(url: str) -> str:
    u = url.strip()
    if u.startswith("postgresql://") and "+psycopg" not in u.split("://", 1)[0]:
        return "postgresql+psycopg://" + u.removeprefix("postgresql://")
    return u


def _sanitize_database_url(url: str) -> str:
    """Quita BOM, saltos de línea y espacios que rompen getaddrinfo / IDNA (UnicodeError)."""
    u = url.strip().strip("\ufeff")
    u = u.replace("\r", "").replace("\n", "")
    return u.strip()


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
            s = str(val).upper()
            if "DICIEMBRE" in s or "ACUMULADA" in s or "AL 31" in s:
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


def parse_resumen(df: pd.DataFrame, source_file: str, year: int) -> list[dict[str, Any]]:
    y = _year_from_sheet(df, year)
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
                "period_month": MONTH,
                "empresa_rank": int(float(rank)),
                "empresa_nombre": str(name).strip(),
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
    """Primera fila de empresa: # en col 1, nombre en col 2, numéricos a la derecha."""
    for i in range(8, min(len(df), 75)):
        rank = df.iloc[i, 1]
        name = df.iloc[i, 2]
        if _is_resumen_data_row(rank, name):
            return i
    return 12


def parse_cuadro(df: pd.DataFrame, source_file: str, year: int) -> list[dict[str, Any]]:
    y = _year_from_sheet(df, year)
    ncols = df.shape[1]
    start = _cuadro_data_start_row(df)
    # 2023: 9 columnas, col 3 = primas del cuadro; 2024/2025: 8 columnas, cols 3-7 = resultados.
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
                "period_month": MONTH,
                "empresa_rank": int(float(rank)),
                "empresa_nombre": str(name).strip(),
                "primas_netas_cobradas": primas,
                "resultado_tecnico_bruto": rtb,
                "resultado_reaseguro_cedido": reaseg,
                "resultado_tecnico_neto": rtn,
                "resultado_gestion_general": gest,
                "saldo_operaciones": saldo,
            }
        )
    return rows_out


def load_workbook_rows(data_dir: Path, entry: dict[str, Any]) -> list[dict[str, Any]]:
    path = data_dir / entry["file"]
    if not path.is_file():
        raise FileNotFoundError(f"No existe: {path}")
    df = pd.read_excel(path, sheet_name=SHEET, header=None, engine="openpyxl")
    kind = entry["kind"]
    year = int(entry["year"])
    if kind == "resumen":
        return parse_resumen(df, entry["file"], year)
    if kind == "cuadro":
        return parse_cuadro(df, entry["file"], year)
    raise ValueError(kind)


SQL_DELETE_RESUMEN = text("delete from public.market_sudeaseg_resumen_empresa where source_file = :sf")
SQL_DELETE_CUADRO = text("delete from public.market_sudeaseg_cuadro_resultados where source_file = :sf")

SQL_INSERT_RESUMEN = text(
    """
    insert into public.market_sudeaseg_resumen_empresa (
      source_file, period_year, period_month, empresa_rank, empresa_nombre,
      primas_netas_cobradas, siniestros_pagados, reservas_psp_brutas, reservas_psp_netas_reaseg,
      siniestros_totales, comisiones, gastos_adquisicion, gastos_administracion
    ) values (
      :source_file, :period_year, :period_month, :empresa_rank, :empresa_nombre,
      :primas_netas_cobradas, :siniestros_pagados, :reservas_psp_brutas, :reservas_psp_netas_reaseg,
      :siniestros_totales, :comisiones, :gastos_adquisicion, :gastos_administracion
    )
    """
)

SQL_INSERT_CUADRO = text(
    """
    insert into public.market_sudeaseg_cuadro_resultados (
      source_file, period_year, period_month, empresa_rank, empresa_nombre,
      primas_netas_cobradas, resultado_tecnico_bruto, resultado_reaseguro_cedido,
      resultado_tecnico_neto, resultado_gestion_general, saldo_operaciones
    ) values (
      :source_file, :period_year, :period_month, :empresa_rank, :empresa_nombre,
      :primas_netas_cobradas, :resultado_tecnico_bruto, :resultado_reaseguro_cedido,
      :resultado_tecnico_neto, :resultado_gestion_general, :saldo_operaciones
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
        help="Carpeta con los xlsx (por defecto Info/data-sudeaseg/xlsx)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Solo parsear e imprimir conteos")
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
                "  · Vuelve a escribir la URI a mano (sin pegar desde PDF).\n"
                "  · Si la contraseña tiene @ # : / ? debe codificarse: "
                "https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls\n"
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
            rows = load_workbook_rows(data_dir, entry)
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
