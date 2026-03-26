"""Agregados para gráficos de cartera (pólizas + siniestros) por cohort_year."""

from __future__ import annotations

import random
import zlib
from typing import Any

import pandas as pd
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

# Estados para reparto demo estable (no geolocalización real).
_VE_ESTADOS: tuple[str, ...] = (
    "Amazonas",
    "Anzoátegui",
    "Apure",
    "Aragua",
    "Barinas",
    "Bolívar",
    "Carabobo",
    "Cojedes",
    "Delta Amacuro",
    "Distrito Capital",
    "Falcón",
    "Guárico",
    "La Guaira",
    "Lara",
    "Mérida",
    "Miranda",
    "Monagas",
    "Nueva Esparta",
    "Portuguesa",
    "Sucre",
    "Táchira",
    "Trujillo",
    "Yaracuy",
    "Zulia",
)


def _estado_demo(policy_id: str) -> str:
    h = zlib.crc32(str(policy_id).encode("utf-8")) & 0xFFFFFFFF
    return _VE_ESTADOS[h % len(_VE_ESTADOS)]


def _rng_policy(policy_id: str) -> int:
    return zlib.crc32(str(policy_id).encode("utf-8")) & 0xFFFFFFFF


def _km_step_function(times: list[int], events: list[int]) -> list[dict[str, float]]:
    """Kaplan-Meier simplificado (tiempo en días desde emisión, evento=1 lapse sintético)."""
    pairs = sorted(zip(times, events))
    if not pairs:
        return []
    death_times = sorted({t for t, e in pairs if e == 1})
    if not death_times:
        return [{"t_days": 0.0, "survival": 1.0}, {"t_days": float(max(times)), "survival": 1.0}]
    curve: list[dict[str, float]] = [{"t_days": 0.0, "survival": 1.0}]
    surv = 1.0
    for t in death_times:
        at_risk = sum(1 for ti, _ in pairs if ti >= t)
        deaths = sum(1 for ti, ei in pairs if ti == t and ei == 1)
        if at_risk <= 0 or deaths <= 0:
            continue
        surv *= 1.0 - deaths / at_risk
        curve.append({"t_days": float(t), "survival": round(float(surv), 6)})
    return curve


def _box_stats(s: pd.Series) -> dict[str, float | int]:
    s = s.dropna().astype(float)
    if s.empty:
        return {}
    q1, q2, q3 = s.quantile(0.25), s.quantile(0.5), s.quantile(0.75)
    iqr = float(q3 - q1)
    lo = float(max(s.min(), q1 - 1.5 * iqr))
    hi = float(min(s.max(), q3 + 1.5 * iqr))
    return {
        "q25": round(float(q1), 2),
        "q50": round(float(q2), 2),
        "q75": round(float(q3), 2),
        "mean": round(float(s.mean()), 2),
        "whisker_low": round(lo, 2),
        "whisker_high": round(hi, 2),
        "n": int(len(s)),
    }


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

    # --- Mapa calor: mes emisión (eje Y) × mes ocurrencia (eje X), conteo de siniestros ---
    heatmap_issue_loss: dict[str, Any] = {
        "x_labels": [str(m) for m in range(1, 13)],
        "y_labels": [str(m) for m in range(1, 13)],
        "z": [[0] * 12 for _ in range(12)],
        "note": "Mes calendario de issue_date (filas) vs mes de loss_date (columnas).",
    }
    if not df_c.empty:
        jn = df_c.merge(df_p[["policy_id", "issue_d"]], on="policy_id", how="left")
        jn["issue_month"] = pd.to_datetime(jn["issue_d"]).dt.month
        jn["loss_month"] = pd.to_datetime(jn["loss_date"]).dt.month
        ct = (
            jn.groupby(["issue_month", "loss_month"])
            .size()
            .unstack(fill_value=0)
            .reindex(index=range(1, 13), columns=range(1, 13), fill_value=0)
        )
        heatmap_issue_loss["z"] = [[int(ct.loc[r, c]) for c in range(1, 13)] for r in range(1, 13)]

    # --- Kaplan-Meier demo: lapsos con tiempo sintético estable; activas censuradas al fin de observación ---
    end_obs = pd.Timestamp(year=cohort_year + 3, month=12, day=31)
    km_times: list[int] = []
    km_events: list[int] = []
    for _, row in df_p.iterrows():
        issue = pd.Timestamp(row.issue_d)
        pid = str(row.policy_id)
        span_days = int(min(900, max(1, (end_obs - issue).days)))
        rng = random.Random(_rng_policy(pid))
        st_l = str(row.status).lower()
        if st_l == "lapsed":
            dur = rng.randint(max(15, min(60, span_days // 4)), span_days)
            km_times.append(dur)
            km_events.append(1)
        else:
            km_times.append(span_days)
            km_events.append(0)
    km_curve = _km_step_function(km_times, km_events)

    # --- Boxplot-friendly stats ---
    box_premium_by_age_band: list[dict[str, Any]] = []
    for band in ["≤35", "36–45", "46–55", "56–65", "66+"]:
        sub = df_p.loc[df_p["age_band"].astype(str) == band, "annual_premium"]
        stt = _box_stats(sub)
        if stt:
            box_premium_by_age_band.append({"label": band, **stt})
    box_premium_by_status: list[dict[str, Any]] = []
    for stv in sorted(df_p["status"].astype(str).unique()):
        sub = df_p.loc[df_p["status"].astype(str) == stv, "annual_premium"]
        stt = _box_stats(sub)
        if stt:
            box_premium_by_status.append({"label": stv, **stt})

    box_samples_age_band: dict[str, list[float]] = {}
    for band in ["≤35", "36–45", "46–55", "56–65", "66+"]:
        sub = df_p.loc[df_p["age_band"].astype(str) == band, "annual_premium"]
        if len(sub) > 0:
            box_samples_age_band[band] = (
                sub.sample(min(500, len(sub)), random_state=42).astype(float).round(2).tolist()
            )
    box_samples_status: dict[str, list[float]] = {}
    for stv in sorted(df_p["status"].astype(str).unique()):
        sub = df_p.loc[df_p["status"].astype(str) == stv, "annual_premium"]
        if len(sub) > 0:
            box_samples_status[str(stv)] = (
                sub.sample(min(500, len(sub)), random_state=42).astype(float).round(2).tolist()
            )

    # --- Rolling “burn” mensual: pagado del mes / exposición acumulada (prima emitida hasta ese mes) ---
    rolling_lr_monthly: list[dict[str, Any]] = []
    all_ym = sorted(set(df_p["issue_ym"].unique()) | (set(df_c["loss_ym"].unique()) if not df_c.empty else set()))
    paid_by_ym = (
        df_c.groupby("loss_ym")["paid_amount_bs"].sum()
        if not df_c.empty
        else pd.Series(dtype=float)
    )
    for ym in all_ym:
        exp_cum = float(df_p.loc[df_p["issue_ym"] <= ym, "annual_premium"].sum())
        p_m = float(paid_by_ym.loc[ym]) if ym in paid_by_ym.index else 0.0
        burn = (p_m / exp_cum * 100.0) if exp_cum > 0 else 0.0
        rolling_lr_monthly.append(
            {
                "month": str(ym),
                "paid_month": round(p_m, 2),
                "exposure_premium_cum": round(exp_cum, 2),
                "burn_pct": round(burn, 4),
            }
        )
    if rolling_lr_monthly:
        rb = pd.DataFrame(rolling_lr_monthly)
        rb["rolling_burn_3m_avg"] = rb["burn_pct"].rolling(3, min_periods=1).mean().round(4)
        rolling_lr_monthly = rb.to_dict("records")

    # --- Territorio demo (asignación por hash de policy_id) ---
    df_p["estado_demo"] = df_p["policy_id"].astype(str).map(_estado_demo)
    geo_base = (
        df_p.groupby("estado_demo", as_index=False)
        .agg(prima_total=("annual_premium", "sum"), n_policies=("policy_id", "count"))
    )
    if not df_c.empty:
        cg = (
            df_c.merge(df_p[["policy_id", "estado_demo"]], on="policy_id", how="left")
            .groupby("estado_demo", as_index=False)
            .agg(n_claims=("claim_id", "count"), paid_total=("paid_amount_bs", "sum"))
        )
        geo_base = geo_base.merge(cg, on="estado_demo", how="left")
    else:
        geo_base["n_claims"] = 0
        geo_base["paid_total"] = 0.0
    geo_base = geo_base.fillna({"n_claims": 0, "paid_total": 0.0})
    geo_by_estado = [
        {
            "estado": str(r.estado_demo),
            "prima_total": round(float(r.prima_total), 2),
            "n_policies": int(r.n_policies),
            "n_claims": int(r.n_claims),
            "paid_total": round(float(r.paid_total), 2),
        }
        for r in geo_base.itertuples()
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
        "heatmap_issue_loss_month": heatmap_issue_loss,
        "km_survival_lapsed_demo": {
            "points": km_curve,
            "note": "Demo: tiempo a ‘lapse’ sintético para estados lapsados; activas censuradas al fin de ventana (+3 años).",
        },
        "box_premium_by_age_band": box_premium_by_age_band,
        "box_premium_by_status": box_premium_by_status,
        "box_samples_age_band": box_samples_age_band,
        "box_samples_status": box_samples_status,
        "rolling_lr_monthly": rolling_lr_monthly,
        "geo_estado_demo": {
            "rows": geo_by_estado,
            "note": "Estado VE asignado por hash de policy_id (demo visual, no geocodificación real).",
        },
    }
