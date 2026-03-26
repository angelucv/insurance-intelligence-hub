#!/usr/bin/env python3
"""
Genera pólizas y siniestros demo (prefijo ALIGN-) con magnitudes inspiradas en el snapshot SUDEASEG.

- Consulta `GET /api/v1/market/la-fe/snapshot-latest` para tomar primas YTD y loss ratio La Fe.
- Escala la suma objetivo de primas anuales de la cohorte como fracción de `primas_ytd` (miles Bs → Bs con factor de escala).
- Inserta en `upload_batches`, `policies`, `policy_claims` (requiere migración 004 y tablas previas).

Uso:
  set DATABASE_URL=postgresql://...
  set COMPUTE_API_URL=https://tu-api   (opcional si la API está arriba)
  pip install psycopg[binary] requests
  python scripts/seed_operational_aligned.py --n-policies 12000 --cohort-year 2022

Si la API no está en marcha (p. ej. producción solo DB), fije referencia manual:
  python scripts/seed_operational_aligned.py ... --primas-ytd-miles 50000 --loss-ratio-ytd 0.55
Sin parámetros y sin API, el script usa 50_000 / 0.55 y muestra un aviso en stderr.

Elimina filas previas con policy_id LIKE 'ALIGN-%' y claim_id LIKE 'ALIGN-%'.
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
    """
    Evita fallos crípticos de psycopg/IDNA (p. ej. host vacío) y guía al usuario.
    """
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
    """
    Devuelve (primas_ytd_miles_bs, loss_ratio_ytd, origen_descripcion).
    Si hay overrides, no llama a la API.
    """
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


def main() -> None:
    p = argparse.ArgumentParser(description="Seed operativo alineado a snapshot SUDEASEG")
    p.add_argument("--database-url", default=os.environ.get("DATABASE_URL", ""))
    p.add_argument(
        "--compute-api-url",
        default=os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000"),
    )
    p.add_argument("--n-policies", type=int, default=12_000)
    p.add_argument("--cohort-year", type=int, default=2022)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--premium-scale",
        type=float,
        default=0.02,
        help="Fracción de primas_ytd (miles Bs) convertidas a Bs que guía la suma de primas anuales de la cohorte.",
    )
    p.add_argument(
        "--primas-ytd-miles",
        type=float,
        default=None,
        help="Sin API: primas YTD La Fe en miles de Bs. (usar junto con --loss-ratio-ytd).",
    )
    p.add_argument(
        "--loss-ratio-ytd",
        type=float,
        default=None,
        help="Sin API: loss ratio YTD La Fe como fracción 0–1 (ej. 0.55).",
    )
    args = p.parse_args()
    if not args.database_url:
        raise SystemExit("Defina --database-url o DATABASE_URL")

    rng = random.Random(args.seed)
    primas_ytd_k, lr, ref_src = _resolve_market_reference(
        args.compute_api_url,
        args.primas_ytd_miles,
        args.loss_ratio_ytd,
    )

    # Objetivo: sum(annual_premium) ~ primas_ytd_k * 1000 * premium_scale (demo de coherencia de orden de magnitud)
    target_sum_premium = primas_ytd_k * 1000.0 * args.premium_scale
    mean_premium = target_sum_premium / max(args.n_policies, 1)

    dsn = _prepare_and_validate_database_url(args.database_url)
    policies_rows: list[tuple] = []
    claims_rows: list[tuple] = []

    mu_log = math.log(max(mean_premium, 200.0))
    for i in range(args.n_policies):
        pid = f"ALIGN-{args.cohort_year}-{i+1:05d}"
        age = rng.randint(22, 72)
        lapse_p = 0.1 + (age - 22) * 0.002
        status = "lapsed" if rng.random() < lapse_p else "active"
        prem = max(500.0, rng.lognormvariate(mu_log, 0.42))
        policies_rows.append((pid, args.cohort_year, age, round(prem, 2), status))

    # Siniestros: subconjunto con probabilidad ligada al loss ratio de mercado
    p_claim = min(0.35, max(0.08, lr * 0.45))
    for i, row in enumerate(policies_rows):
        pid, cy, age, prem, status = row
        if rng.random() > p_claim:
            continue
        n_claims = rng.randint(1, 2)
        for j in range(n_claims):
            cid = f"ALIGN-CLM-{args.cohort_year}-{i+1:05d}-{j+1}"
            loss_day = date(args.cohort_year, 6, 1) + timedelta(days=rng.randint(0, 300))
            paid = round(min(prem * rng.uniform(0.15, 0.85), prem * 2), 2)
            reported = round(paid * rng.uniform(1.0, 1.25), 2)
            claims_rows.append((cid, pid, loss_day, reported, paid, "paid"))

    try:
        conn_cm = psycopg.connect(dsn)
    except UnicodeError as e:
        raise SystemExit(
            "Fallo al resolver el host de DATABASE_URL (IDNA). Suele deberse a un host vacío, "
            "demasiado largo o caracteres inválidos al copiar la URL.\n"
            f"  Host interpretado: {urlparse(dsn).hostname!r}\n"
            f"  Detalle: {e}\n"
            "  Compruebe la cadena en el panel de Supabase / Neon y vuelva a pegarla sin saltos de línea."
        ) from e

    with conn_cm as conn:
        conn.execute("DELETE FROM policy_claims WHERE claim_id LIKE 'ALIGN-%'")
        conn.execute("DELETE FROM policies WHERE policy_id LIKE 'ALIGN-%'")
        batch_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO upload_batches (id, source, filename, row_count, error_count)
            VALUES (%s, 'seed_aligned', 'seed_operational_aligned.py', %s, 0)
            """,
            (batch_id, len(policies_rows)),
        )
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO policies (batch_id, policy_id, cohort_year, issue_age, annual_premium, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [(batch_id,) + pr for pr in policies_rows],
            )
            if claims_rows:
                cur.executemany(
                    """
                    INSERT INTO policy_claims (batch_id, claim_id, policy_id, loss_date, reported_amount_bs, paid_amount_bs, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    [(batch_id, c[0], c[1], c[2], c[3], c[4], "paid") for c in claims_rows],
                )
        conn.commit()

    print(
        f"OK: {len(policies_rows)} pólizas ALIGN-* cohorte {args.cohort_year}, "
        f"{len(claims_rows)} siniestros. batch_id={batch_id}. "
        f"Referencia ({ref_src}): primas_ytd={primas_ytd_k:,.2f} mil Bs, lr≈{lr:.3f}."
    )


if __name__ == "__main__":
    main()
