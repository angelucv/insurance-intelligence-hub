"""Motor de demo: datos sintéticos + agregación en DuckDB (sin archivos externos)."""

from __future__ import annotations

import random
from typing import Any

import duckdb
import pandas as pd


def _synthetic_rows(seed: int, n: int, cohort_year: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for i in range(n):
        age = rng.randint(18, 75)
        premium = round(rng.lognormvariate(8.0, 0.35), 2)
        # Persistencia decrece ligeramente con edad (demo)
        lapse_p = 0.08 + (age - 18) * 0.0012
        status = "lapsed" if rng.random() < lapse_p else "active"
        rows.append(
            {
                "policy_id": f"DEMO-{cohort_year}-{i+1:05d}",
                "cohort_year": cohort_year,
                "issue_age": age,
                "annual_premium": premium,
                "status": status,
            }
        )
    return rows


def compute_kpi_summary(*, seed: int = 42, n_policies: int = 8000, cohort_year: int = 2022) -> dict[str, Any]:
    rows = _synthetic_rows(seed, n_policies, cohort_year)
    con = duckdb.connect(database=":memory:")
    con.register("policies", pd.DataFrame(rows))
    q = """
    SELECT
      cohort_year,
      COUNT(*) AS n,
      SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_n,
      SUM(CASE WHEN status = 'lapsed' THEN 1 ELSE 0 END) AS lapsed_n,
      AVG(annual_premium) AS avg_premium
    FROM policies
    GROUP BY cohort_year
    """
    row = con.execute(q).fetchone()
    con.close()
    if not row:
        raise RuntimeError("Sin resultados agregados")
    _, total, active_n, lapsed_n, avg_premium = row
    persistency = (active_n / total) * 100.0 if total else 0.0
    # Ratio técnico demo: fijo con ligera variación por seed
    tlr = 72.0 + (seed % 17) + (persistency / 100.0) * 3.0
    return {
        "persistency_rate_pct": round(float(persistency), 2),
        "policies_active": int(active_n),
        "policies_lapsed": int(lapsed_n),
        "avg_annual_premium": round(float(avg_premium), 2),
        "cohort_year": int(cohort_year),
        "technical_loss_ratio_pct": round(float(tlr), 2),
        "data_note": "Datos 100% sintéticos para demostración; no representan cartera real.",
    }
