#!/usr/bin/env python3
"""
Genera pólizas y siniestros demo (prefijo ALIGN-) con magnitudes inspiradas en el snapshot SUDEASEG.

- Consulta `GET /api/v1/market/la-fe/snapshot-latest` para tomar primas YTD y loss ratio La Fe.
- Escala la suma objetivo de primas anuales por cohorte como fracción de `primas_ytd` (miles Bs → Bs).
- Cada póliza tiene `issue_date` dentro del año cohorte; siniestros con `loss_date` >= emisión
  y repartidos hasta ~2 años después (dimensión temporal para análisis).

Requiere migración 005 (`issue_date` en policies) y 004 (`policy_claims`).

Uso:
  set DATABASE_URL=postgresql://...
  python scripts/seed_operational_aligned.py --cohort-years 2023,2024,2025 --n-policies 8000 \\
      --primas-ytd-miles 50000 --loss-ratio-ytd 0.55

Un solo año (compatibilidad):
  python scripts/seed_operational_aligned.py --cohort-year 2022 --n-policies 12000 ...

Elimina solo filas ALIGN-* de los años de cohorte indicados (no borra otros años ALIGN).
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sys
import uuid
from datetime import date, timedelta
from urllib.parse import urlparse

import requests

try:
    import psycopg
except ImportError as e:
    raise SystemExit("Instala psycopg: pip install 'psycopg[binary]'") from e


def _normalize_url(url: str) -> str:
    if url.startswith("postgresql://") and "+psycopg" not in url.split("://", 1)[0]:
        return "postgresql://" + url.removeprefix("postgresql://")
    return url


def _prepare_and_validate_database_url(raw: str) -> str:
    s = raw.strip().strip('"').strip("'").strip()
    if not s:
        raise SystemExit("DATABASE_URL está vacío. Defina --database-url o la variable de entorno.")

    dsn = _normalize_url(s)
    parsed = urlparse(dsn)
    scheme = (parsed.scheme or "").lower().replace("+psycopg", "").replace("+asyncpg", "")
    if scheme not in ("postgres", "postgresql"):
        raise SystemExit(
            f"DATABASE_URL debe usar esquema postgresql:// (recibido: {parsed.scheme!r})."
        )

    host = parsed.hostname
    if host is None or str(host).strip() == "":
        raise SystemExit(
            "DATABASE_URL no incluye un host de PostgreSQL válido (nombre tras @).\n"
            "  Ejemplo: postgresql://usuario:clave@db.xxxxx.supabase.co:5432/postgres\n"
            "  Evite URLs del tipo postgresql://user:pass@/solo_db (host vacío)."
        )

    if ".." in host or any(part == "" for part in host.split(".")):
        raise SystemExit(
            f"El host en DATABASE_URL parece mal formado: {host!r}. "
            "Revise que no falte el servidor ni haya puntos dobles."
        )

    return dsn


def fetch_snapshot(api_base: str) -> dict:
    r = requests.get(f"{api_base.rstrip('/')}/api/v1/market/la-fe/snapshot-latest", timeout=60)
    r.raise_for_status()
    return r.json()


def _resolve_market_reference(
    api_base: str,
    primas_override: float | None,
    lr_override: float | None,
) -> tuple[float, float, str]:
    if primas_override is not None and lr_override is not None:
        lr = max(0.05, min(0.95, float(lr_override)))
        return float(primas_override), lr, "parámetros CLI (--primas-ytd-miles / --loss-ratio-ytd)"

    if primas_override is not None or lr_override is not None:
        raise SystemExit(
            "Use ambos a la vez: --primas-ytd-miles y --loss-ratio-ytd, o ninguno para leer la API."
        )

    url = f"{api_base.rstrip('/')}/api/v1/market/la-fe/snapshot-latest"
    try:
        snap = fetch_snapshot(api_base)
    except requests.exceptions.RequestException as e:
        print(
            f"Aviso: no se pudo obtener el snapshot ({url}): {e}\n"
            "  → Usando referencia por defecto (50_000 mil Bs, loss_ratio 0.55).\n"
            "  → En producción: arranque la API compute, o bien ejecute con:\n"
            "     --primas-ytd-miles 50000 --loss-ratio-ytd 0.55\n"
            "     (valores alineados a su último cierre SUDEASEG si los conoce).",
            file=sys.stderr,
        )
        return 50_000.0, 0.55, "valores por defecto (API no disponible)"

    lf = snap.get("la_fe") or {}
    primas_ytd_k = float(lf.get("primas_ytd") or 50_000.0)
    lr = float(lf.get("loss_ratio_ytd") or 0.55)
    lr = max(0.05, min(0.95, lr))
    return primas_ytd_k, lr, f"snapshot API ({url})"


def _parse_cohort_years(cohort_years: str | None, cohort_year: int | None) -> list[int]:
    if cohort_years:
        parts = [p.strip() for p in cohort_years.split(",") if p.strip()]
        out: list[int] = []
        for p in parts:
            try:
                y = int(p)
            except ValueError as e:
                raise SystemExit(f"Año inválido en --cohort-years: {p!r}") from e
            if y < 1990 or y > 2100:
                raise SystemExit(f"Año fuera de rango: {y}")
            out.append(y)
        if not out:
            raise SystemExit("--cohort-years no puede quedar vacío.")
        return sorted(set(out))
    if cohort_year is not None:
        if cohort_year < 1990 or cohort_year > 2100:
            raise SystemExit(f"Año fuera de rango: {cohort_year}")
        return [cohort_year]
    return [2022]


def _random_issue_date(rng: random.Random, cy: int) -> date:
    start = date(cy, 1, 1).toordinal()
    end = date(cy, 12, 31).toordinal()
    return date.fromordinal(rng.randint(start, end))


def _random_loss_date(rng: random.Random, issue_d: date, cy: int) -> date:
    """Siniestro entre ~1 mes después de emisión y hasta fin de año cy+2."""
    earliest = issue_d + timedelta(days=rng.randint(28, 120))
    end_cap = date(cy + 2, 12, 31)
    if earliest > end_cap:
        earliest = issue_d + timedelta(days=rng.randint(14, 45))
    span = (end_cap - earliest).days
    if span <= 0:
        return min(earliest, end_cap)
    return earliest + timedelta(days=rng.randint(0, span))


def _delete_align_for_cohorts(conn: psycopg.Connection, years: list[int]) -> None:
    for y in years:
        conn.execute(
            """
            DELETE FROM policy_claims c
            USING policies p
            WHERE c.policy_id = p.policy_id
              AND p.cohort_year = %s
              AND p.policy_id LIKE 'ALIGN-%%'
            """,
            (y,),
        )
        conn.execute(
            "DELETE FROM policies WHERE cohort_year = %s AND policy_id LIKE 'ALIGN-%%'",
            (y,),
        )


def main() -> None:
    p = argparse.ArgumentParser(description="Seed operativo alineado a snapshot SUDEASEG")
    p.add_argument("--database-url", default=os.environ.get("DATABASE_URL", ""))
    p.add_argument(
        "--compute-api-url",
        default=os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000"),
    )
    p.add_argument("--n-policies", type=int, default=12_000)
    p.add_argument(
        "--cohort-year",
        type=int,
        default=None,
        help="Una sola cohorte (alternativa a --cohort-years).",
    )
    p.add_argument(
        "--cohort-years",
        default=None,
        help="Lista separada por comas, ej. 2023,2024,2025. --n-policies aplica a cada año.",
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--premium-scale",
        type=float,
        default=0.02,
        help="Fracción de primas_ytd (miles Bs) convertidas a Bs que guía la suma de primas anuales por cohorte.",
    )
    p.add_argument("--primas-ytd-miles", type=float, default=None)
    p.add_argument("--loss-ratio-ytd", type=float, default=None)
    args = p.parse_args()
    if not args.database_url:
        raise SystemExit("Defina --database-url o DATABASE_URL")

    years = _parse_cohort_years(args.cohort_years, args.cohort_year)
    primas_ytd_k, lr, ref_src = _resolve_market_reference(
        args.compute_api_url,
        args.primas_ytd_miles,
        args.loss_ratio_ytd,
    )

    target_sum_premium = primas_ytd_k * 1000.0 * args.premium_scale
    mean_premium = target_sum_premium / max(args.n_policies, 1)

    dsn = _prepare_and_validate_database_url(args.database_url)
    all_policies: list[tuple] = []
    all_claims: list[tuple] = []

    for cy in years:
        rng = random.Random(args.seed + cy * 1_000_003)
        mu_log = math.log(max(mean_premium, 200.0))
        policies_rows: list[tuple] = []
        for i in range(args.n_policies):
            pid = f"ALIGN-{cy}-{i+1:05d}"
            age = rng.randint(22, 72)
            lapse_p = 0.1 + (age - 22) * 0.002
            status = "lapsed" if rng.random() < lapse_p else "active"
            prem = max(500.0, rng.lognormvariate(mu_log, 0.42))
            issue_d = _random_issue_date(rng, cy)
            policies_rows.append((pid, cy, age, round(prem, 2), status, issue_d))

        p_claim = min(0.35, max(0.08, lr * 0.45))
        claims_rows: list[tuple] = []
        for i, row in enumerate(policies_rows):
            pid, cyy, age, prem, status, issue_d = row
            if rng.random() > p_claim:
                continue
            n_claims = rng.randint(1, 2)
            for j in range(n_claims):
                cid = f"ALIGN-CLM-{cyy}-{i+1:05d}-{j+1}"
                loss_day = _random_loss_date(rng, issue_d, cyy)
                paid = round(min(prem * rng.uniform(0.15, 0.85), prem * 2), 2)
                reported = round(paid * rng.uniform(1.0, 1.25), 2)
                claims_rows.append((cid, pid, loss_day, reported, paid))

        all_policies.extend(policies_rows)
        all_claims.extend(claims_rows)

    try:
        conn_cm = psycopg.connect(dsn)
    except UnicodeError as e:
        raise SystemExit(
            "Fallo al resolver el host de DATABASE_URL (IDNA).\n"
            f"  Host interpretado: {urlparse(dsn).hostname!r}\n"
            f"  Detalle: {e}\n"
        ) from e

    with conn_cm as conn:
        _delete_align_for_cohorts(conn, years)
        batch_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO upload_batches (id, source, filename, row_count, error_count)
            VALUES (%s, 'seed_aligned', 'seed_operational_aligned.py', %s, 0)
            """,
            (batch_id, len(all_policies)),
        )
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO policies (batch_id, policy_id, cohort_year, issue_age, annual_premium, status, issue_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    (batch_id, pr[0], pr[1], pr[2], pr[3], pr[4], pr[5])
                    for pr in all_policies
                ],
            )
            if all_claims:
                cur.executemany(
                    """
                    INSERT INTO policy_claims (batch_id, claim_id, policy_id, loss_date, reported_amount_bs, paid_amount_bs, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    [(batch_id, c[0], c[1], c[2], c[3], c[4], "paid") for c in all_claims],
                )
        conn.commit()

    print(
        f"OK: cohortes {years}: {len(all_policies)} pólizas ALIGN-*, {len(all_claims)} siniestros. "
        f"batch_id={batch_id}. issue_date por póliza en su año cohorte; loss_date >= emisión. "
        f"Referencia ({ref_src}): primas_ytd={primas_ytd_k:,.2f} mil Bs, lr≈{lr:.3f}."
    )


if __name__ == "__main__":
    main()
