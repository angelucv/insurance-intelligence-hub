"""Agregados para gráficos de cartera (pólizas + siniestros) por cohort_year."""

from __future__ import annotations

from typing import Any

import pandas as pd
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session


def _read_policies(session: Session, cohort_year: int) -> pd.DataFrame:
    conn = session.connection()
    q = text(
        """
        SELECT
          policy_id,
          issue_age,
          annual_premium::float AS annual_premium,
          status,
          COALESCE(issue_date, make_date(cohort_year, 6, 15)) AS issue_d
        FROM policies
        WHERE cohort_year = :y
        """
    )
    try:
        return pd.read_sql(q, conn, params={"y": cohort_year})
    except Exception as e:  # noqa: BLE001
        logger.warning("Leyendo pólizas sin issue_date (¿migración 005?): {}", e)
        q2 = text(
            """
            SELECT
              policy_id,
              issue_age,
              annual_premium::float AS annual_premium,
              status,
              make_date(cohort_year, 6, 15) AS issue_d
            FROM policies
            WHERE cohort_year = :y
            """
        )
        return pd.read_sql(q2, conn, params={"y": cohort_year})


def _read_claims(session: Session, cohort_year: int) -> pd.DataFrame:
    conn = session.connection()
    q = text(
        """
        SELECT
          c.claim_id,
          c.policy_id,
          c.loss_date,
          c.paid_amount_bs::float AS paid_amount_bs,
          c.reported_amount_bs::float AS reported_amount_bs,
          c.status AS claim_status
        FROM policy_claims c
        INNER JOIN policies p ON p.policy_id = c.policy_id
        WHERE p.cohort_year = :y
        """
    )
    try:
        return pd.read_sql(q, conn, params={"y": cohort_year})
    except Exception as e:  # noqa: BLE001
        logger.warning("Sin tabla policy_claims o error de lectura: {}", e)
        return pd.DataFrame()


def cohort_portfolio_payload(session: Session, cohort_year: int) -> dict[str, Any] | None:
    df_p = _read_policies(session, cohort_year)
    if df_p.empty:
        return None

    df_c = _read_claims(session, cohort_year)

    df_p["issue_d"] = pd.to_datetime(df_p["issue_d"])
    df_p["issue_ym"] = df_p["issue_d"].dt.strftime("%Y-%m")

    issue_m = (
        df_p.groupby("issue_ym", as_index=False)
        .agg(policies=("policy_id", "count"), premium_sum=("annual_premium", "sum"))
        .sort_values("issue_ym")
    )

    status_ct = df_p.groupby("status")["policy_id"].count().to_dict()
    status_ct = {str(k): int(v) for k, v in status_ct.items()}

    # Histograma prima
    prem = df_p["annual_premium"].astype(float)
    if prem.nunique() <= 1:
        v = float(prem.iloc[0])
        prem_hist = {"bin_lo": [v], "bin_hi": [v + 1e-6], "counts": [len(prem)]}
    else:
        nb = min(20, max(8, prem.nunique()))
        try:
            cat = pd.cut(prem, bins=nb)
            hist_p = cat.value_counts().sort_index()
            prem_hist = {
                "bin_lo": [float(iv.left) for iv in hist_p.index],
                "bin_hi": [float(iv.right) for iv in hist_p.index],
                "counts": [int(x) for x in hist_p.values],
            }
        except (ValueError, TypeError):
            prem_hist = {"bin_lo": [float(prem.min())], "bin_hi": [float(prem.max())], "counts": [len(prem)]}

    # Edad al emitir
    age_ct = (
        df_p.groupby("issue_age")["policy_id"]
        .count()
        .reset_index(name="n")
        .sort_values("issue_age")
    )
    age_hist = {
        "ages": [int(x) for x in age_ct["issue_age"].tolist()],
        "counts": [int(x) for x in age_ct["n"].tolist()],
    }

    # Tramos de edad (sunburst / treemap)
    bins = [0, 35, 45, 55, 65, 120]
    labels = ["≤35", "36–45", "46–55", "56–65", "66+"]
    df_p["age_band"] = pd.cut(
        df_p["issue_age"],
        bins=bins,
        labels=labels,
        right=True,
        include_lowest=True,
    )
    _ap = df_p.dropna(subset=["age_band"])
    age_status = (
        _ap.groupby(["status", "age_band"], observed=False)["policy_id"]
        .count()
        .reset_index(name="n")
    )
    sunburst_rows: list[dict[str, Any]] = []
    for _, r in age_status.iterrows():
        sunburst_rows.append(
            {
                "status": str(r["status"]),
                "age_band": str(r["age_band"]),
                "n": int(r["n"]),
            }
        )

    total_premium = float(prem.sum())
    n_pol = int(len(df_p))

    loss_by_month: list[dict[str, Any]] = []
    cumulative_paid: list[dict[str, Any]] = []
    claim_status_ct: dict[str, int] = {}
    sev_bins: dict[str, list] = {"bin_lo": [], "bin_hi": [], "counts": []}
    total_paid = 0.0
    n_clm = 0
    scatter_policies: list[dict[str, Any]] = []
    top_policies: list[dict[str, Any]] = []

    if not df_c.empty:
        df_c["loss_date"] = pd.to_datetime(df_c["loss_date"])
        df_c["loss_ym"] = df_c["loss_date"].dt.strftime("%Y-%m")
        lm = (
            df_c.groupby("loss_ym", as_index=False)
            .agg(
                claims=("claim_id", "count"),
                paid_sum=("paid_amount_bs", "sum"),
                reported_sum=("reported_amount_bs", "sum"),
            )
            .sort_values("loss_ym")
        )
        loss_by_month = [
            {
                "month": str(r.loss_ym),
                "claims": int(r.claims),
                "paid_sum": float(r.paid_sum),
                "reported_sum": float(r.reported_sum),
            }
            for r in lm.itertuples()
        ]
        cum = 0.0
        for row in loss_by_month:
            cum += row["paid_sum"]
            cumulative_paid.append({"month": row["month"], "cumulative_paid": round(cum, 2)})

        total_paid = float(df_c["paid_amount_bs"].sum())
        n_clm = int(len(df_c))

        cst = df_c.groupby("claim_status")["claim_id"].count().to_dict()
        claim_status_ct = {str(k): int(v) for k, v in cst.items()}

        paid_vals = df_c["paid_amount_bs"].astype(float)
        if paid_vals.nunique() > 1:
            nb = min(18, max(6, min(paid_vals.nunique(), 30)))
            try:
                hc = pd.cut(paid_vals, bins=nb)
                hv = hc.value_counts().sort_index()
                sev_bins = {
                    "bin_lo": [float(iv.left) for iv in hv.index],
                    "bin_hi": [float(iv.right) for iv in hv.index],
                    "counts": [int(x) for x in hv.values],
                }
            except (ValueError, TypeError):
                sev_bins = {"bin_lo": [], "bin_hi": [], "counts": []}

        by_pol = (
            df_c.groupby("policy_id")
            .agg(claim_n=("claim_id", "count"), paid_total=("paid_amount_bs", "sum"))
            .reset_index()
        )
        by_pol = by_pol.merge(
            df_p[["policy_id", "annual_premium"]],
            on="policy_id",
            how="left",
        )
        by_pol = by_pol.sort_values("paid_total", ascending=False)
        top_policies = []
        for _, r in by_pol.head(20).iterrows():
            pid = str(r["policy_id"])
            top_policies.append(
                {
                    "policy_id": pid[:18] + ("…" if len(pid) > 18 else ""),
                    "paid_total": float(r["paid_total"]),
                    "claim_n": int(r["claim_n"]),
                }
            )

        max_pts = 1800
        samp = by_pol.sample(min(len(by_pol), max_pts), random_state=42) if len(by_pol) > max_pts else by_pol
        scatter_policies = [
            {
                "annual_premium": float(r["annual_premium"]),
                "paid_total": float(r["paid_total"]),
                "claim_n": int(r["claim_n"]),
            }
            for _, r in samp.iterrows()
        ]

    lr_op = (total_paid / total_premium * 100.0) if total_premium > 0 else None

    return {
        "cohort_year": cohort_year,
        "policies_total": n_pol,
        "claims_total": n_clm,
        "total_annual_premium": round(total_premium, 2),
        "total_paid_claims": round(total_paid, 2),
        "operational_loss_ratio_pct": round(lr_op, 3) if lr_op is not None else None,
        "issue_by_month": [
            {
                "month": str(r.issue_ym),
                "policies": int(r.policies),
                "premium_sum": float(r.premium_sum),
            }
            for r in issue_m.itertuples()
        ],
        "loss_by_month": loss_by_month,
        "cumulative_paid": cumulative_paid,
        "status_breakdown": status_ct,
        "premium_histogram": prem_hist,
        "age_histogram": age_hist,
        "sunburst_age_status": sunburst_rows,
        "claim_status_breakdown": claim_status_ct,
        "claim_severity_histogram": sev_bins,
        "scatter_premium_vs_paid": scatter_policies,
        "top_policies_by_paid": top_policies,
    }
