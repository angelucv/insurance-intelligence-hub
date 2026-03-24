"""KPIs: datos en Postgres → agregación DuckDB; fallback sintético."""

from __future__ import annotations

import io
from typing import Any

import duckdb
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.demo_engine import compute_kpi_summary


def _duckdb_aggregate(df: pd.DataFrame, cohort_year: int) -> dict[str, Any]:
    if df.empty:
        return {}
    con = duckdb.connect(database=":memory:")
    con.register("policies", df)
    q = """
    SELECT
      cohort_year,
      COUNT(*) AS n,
      SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_n,
      SUM(CASE WHEN status = 'lapsed' THEN 1 ELSE 0 END) AS lapsed_n,
      AVG(annual_premium) AS avg_premium
    FROM policies
    WHERE cohort_year = ?
    GROUP BY cohort_year
    """
    row = con.execute(q, [cohort_year]).fetchone()
    con.close()
    if not row:
        return {}
    _, total, active_n, lapsed_n, avg_premium = row
    persistency = (active_n / total) * 100.0 if total else 0.0
    tlr = min(115.0, 58.0 + (float(lapsed_n) / max(total, 1)) * 40.0)
    return {
        "persistency_rate_pct": round(float(persistency), 2),
        "policies_active": int(active_n),
        "policies_lapsed": int(lapsed_n),
        "avg_annual_premium": round(float(avg_premium), 2),
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
    df = pd.read_sql(q, session.bind, params={"y": cohort_year})
    out = _duckdb_aggregate(df, cohort_year)
    return out if out else None


def kpi_summary_payload(
    *,
    session: Session | None,
    cohort_year: int,
    seed: int,
    n_policies: int,
    prefer_db: bool,
) -> dict[str, Any]:
    if prefer_db and session is not None and session.bind is not None:
        db_payload = kpi_from_database(session, cohort_year)
        if db_payload:
            return db_payload
    raw = compute_kpi_summary(seed=seed, n_policies=n_policies, cohort_year=cohort_year)
    note = raw.get("data_note", "")
    if prefer_db and session is not None:
        note = (
            "Sin filas en BD para esta cohorte; mostrando cartera sintética. "
            + note
        )
    raw["data_note"] = note
    return raw
