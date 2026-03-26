"""KPIs: datos en Postgres → agregación DuckDB; fallback sintético."""

from __future__ import annotations

from typing import Any

import duckdb
import pandas as pd
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.demo_engine import compute_kpi_summary


def _duckdb_aggregate(df: pd.DataFrame, cohort_year: int) -> dict[str, Any]:
    if df.empty:
        return {}
    con = duckdb.connect(database=":memory:")
    con.register("policies", df)
    # Sin segundo WHERE: el DataFrame ya viene filtrado por cohort_year en SQL.
    q = """
    SELECT
      COUNT(*) AS n,
      SUM(CASE WHEN LOWER(TRIM(CAST(status AS VARCHAR))) = 'active' THEN 1 ELSE 0 END) AS active_n,
      SUM(CASE WHEN LOWER(TRIM(CAST(status AS VARCHAR))) = 'lapsed' THEN 1 ELSE 0 END) AS lapsed_n,
      AVG(CAST(annual_premium AS DOUBLE)) AS avg_premium
    FROM policies
    """
    row = con.execute(q).fetchone()
    con.close()
    if not row:
        return {}
    total, active_n, lapsed_n, avg_premium = row
    total = int(total or 0)
    if total == 0:
        return {}
    active_n = int(active_n or 0)
    lapsed_n = int(lapsed_n or 0)
    if avg_premium is None or (isinstance(avg_premium, float) and pd.isna(avg_premium)):
        return {}
    ap = float(avg_premium)
    if ap <= 0:
        return {}
    persistency = (active_n / total) * 100.0
    tlr = min(115.0, 58.0 + (float(lapsed_n) / max(total, 1)) * 40.0)
    return {
        "persistency_rate_pct": round(float(persistency), 2),
        "policies_active": active_n,
        "policies_lapsed": lapsed_n,
        "avg_annual_premium": round(ap, 2),
        "cohort_year": int(cohort_year),
        "technical_loss_ratio_pct": round(float(tlr), 2),
        "data_note": "KPIs calculados en DuckDB sobre pólizas persistidas en PostgreSQL (demo).",
    }


def kpi_from_database(session: Session, cohort_year: int) -> dict[str, Any] | None:
    q = text(
        """
        SELECT policy_id, cohort_year, issue_age, annual_premium, status
        FROM policies
        WHERE cohort_year = :y
        """
    )
    try:
        conn = session.connection()
        df = pd.read_sql(q, conn, params={"y": cohort_year})
    except Exception as e:  # noqa: BLE001
        logger.exception("No se pudieron leer pólizas para KPI: {}", e)
        return None

    if not df.empty:
        df = df.copy()
        df["annual_premium"] = pd.to_numeric(df["annual_premium"], errors="coerce")
        df = df.dropna(subset=["annual_premium"])
        df = df[df["annual_premium"] > 0]

    out = _duckdb_aggregate(df, cohort_year)
    if not out:
        return None
    bridge = _operational_claims_note(session, cohort_year)
    if bridge:
        prev = str(out.get("data_note", "")).strip()
        out["data_note"] = (prev + " " + bridge).strip() if prev else bridge
    return out


def _operational_claims_note(session: Session, cohort_year: int) -> str:
    """Si existe `policy_claims`, resume siniestros enlazados a la cohorte (puente operativo ↔ financiero)."""
    try:
        q = text(
            """
            SELECT COUNT(*)::int, COALESCE(SUM(c.paid_amount_bs), 0)::float
            FROM policy_claims c
            INNER JOIN policies p ON p.policy_id = c.policy_id
            WHERE p.cohort_year = :y
            """
        )
        row = session.execute(q, {"y": cohort_year}).first()
        if not row:
            return ""
        n_claims, paid_sum = int(row[0] or 0), float(row[1] or 0)
        if n_claims == 0:
            return ""
        return (
            f"Operativo: {n_claims:,} siniestros en BD para cohorte {cohort_year} "
            f"(pagado acum. demo {paid_sum:,.2f} Bs.). "
            "Las cifras SUDEASEG del laboratorio son referencia de mercado (no consolidación de esta cartera)."
        )
    except Exception:  # noqa: BLE001
        return ""


def kpi_summary_payload(
    *,
    session: Session | None,
    cohort_year: int,
    seed: int,
    n_policies: int,
    prefer_db: bool,
) -> dict[str, Any]:
    if prefer_db and session is not None and session.bind is not None:
        try:
            db_payload = kpi_from_database(session, cohort_year)
            if db_payload:
                return db_payload
        except Exception as e:  # noqa: BLE001
            logger.exception("KPI desde BD falló, usando sintético: {}", e)

    raw = compute_kpi_summary(seed=seed, n_policies=n_policies, cohort_year=cohort_year)
    note = raw.get("data_note", "")
    if prefer_db and session is not None:
        note = (
            "Sin filas en BD para esta cohorte (o error al leer); mostrando cartera sintética. "
            + note
        )
    raw["data_note"] = note
    return raw
