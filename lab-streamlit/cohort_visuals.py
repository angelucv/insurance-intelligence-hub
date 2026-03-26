"""Gráficos Plotly para el paquete `/api/v1/kpi/cohort-portfolio` (Streamlit)."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def fetch_cohort_portfolio(base: str, cohort_year: int) -> dict[str, Any] | None:
    try:
        r = requests.get(
            f"{base}/api/v1/kpi/cohort-portfolio",
            params={"cohort_year": cohort_year},
            timeout=90,
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _brand_layout(fig: go.Figure, *, height: int | None = None) -> None:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,0.92)",
        font=dict(family="Segoe UI, system-ui, sans-serif", size=12, color="#334155"),
        margin=dict(l=48, r=32, t=48, b=40),
    )
    if height:
        fig.update_layout(height=height)


def render_portfolio_pack(
    pack: dict[str, Any],
    *,
    brand_purple: str,
    brand_deep: str,
    accent_blue: str,
) -> None:
    import streamlit as st

    cy = pack["cohort_year"]
    st.subheader("Laboratorio analítico de cartera")
    st.caption(
        f"Cohorte **{cy}**: emisión, composición, siniestralidad temporal y severidad "
        "(datos agregados vía API compute)."
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Pólizas", f"{pack['policies_total']:,}")
    m2.metric("Siniestros", f"{pack['claims_total']:,}")
    m3.metric("Prima anual total", f"{pack['total_annual_premium']:,.0f}")
    m4.metric("Pagado siniestros", f"{pack['total_paid_claims']:,.0f}")
    lr = pack.get("operational_loss_ratio_pct")
    m5.metric(
        "Ratio pagado/prima",
        f"{lr:.2f} %" if lr is not None else "—",
        help="Suma pagada en siniestros / suma primas anuales de la cohorte (proxy operativo demo).",
    )

    tab_a, tab_b, tab_c, tab_d = st.tabs(
        ["Panorama", "Emisión", "Siniestralidad", "Prima vs siniestro"],
    )

    with tab_a:
        c1, c2 = st.columns(2)
        with c1:
            sb = pack.get("sunburst_age_status") or []
            if sb:
                df_sb = pd.DataFrame(sb)
                fig_sb = px.sunburst(
                    df_sb,
                    path=["status", "age_band"],
                    values="n",
                    color="status",
                    color_discrete_map={"active": brand_purple, "lapsed": "#94a3b8"},
                )
                fig_sb.update_traces(textinfo="label+percent parent")
                _brand_layout(fig_sb, height=420)
                st.plotly_chart(fig_sb, use_container_width=True)
            else:
                st.info("Sin datos de composición.")
        with c2:
            st.markdown("**Estado de la póliza**")
            stb = pack.get("status_breakdown") or {}
            if stb:
                fig_d = go.Figure(
                    data=[
                        go.Pie(
                            labels=list(stb.keys()),
                            values=list(stb.values()),
                            hole=0.52,
                            marker=dict(colors=[brand_purple, "#c4b5fd"]),
                            textinfo="percent+label",
                        )
                    ]
                )
                _brand_layout(fig_d, height=420)
                st.plotly_chart(fig_d, use_container_width=True)
        if pack.get("claim_status_breakdown"):
            st.markdown("**Estado del siniestro (carga)**")
            cs = pack["claim_status_breakdown"]
            fig_cs = go.Figure(
                go.Bar(
                    x=list(cs.keys()),
                    y=list(cs.values()),
                    marker_color=accent_blue,
                    text=list(cs.values()),
                    textposition="outside",
                )
            )
            fig_cs.update_xaxes(title_text="Estado")
            fig_cs.update_yaxes(title_text="Cantidad")
            _brand_layout(fig_cs, height=320)
            st.plotly_chart(fig_cs, use_container_width=True)

    with tab_b:
        ibm = pack.get("issue_by_month") or []
        if ibm:
            months = [r["month"] for r in ibm]
            pols = [r["policies"] for r in ibm]
            prs = [r["premium_sum"] for r in ibm]
            fig_e = make_subplots(specs=[[{"secondary_y": True}]])
            fig_e.add_trace(
                go.Bar(x=months, y=pols, name="Pólizas emitidas", marker_color=brand_purple),
                secondary_y=False,
            )
            fig_e.add_trace(
                go.Scatter(
                    x=months,
                    y=prs,
                    name="Prima emitida (Bs.)",
                    mode="lines+markers",
                    line=dict(color=accent_blue, width=2),
                    marker=dict(size=8),
                ),
                secondary_y=True,
            )
            fig_e.update_xaxes(title_text="Mes de emisión (issue_date)")
            fig_e.update_yaxes(title_text="Número de pólizas", secondary_y=False)
            fig_e.update_yaxes(title_text="Suma prima anual (Bs.)", secondary_y=True)
            fig_e.update_layout(legend=dict(orientation="h", y=1.12))
            _brand_layout(fig_e, height=400)
            st.plotly_chart(fig_e, use_container_width=True)

        c1, c2 = st.columns(2)
        ph = pack.get("premium_histogram") or {}
        with c1:
            if ph.get("counts"):
                mids = [(ph["bin_lo"][i] + ph["bin_hi"][i]) / 2 for i in range(len(ph["counts"]))]
                fig_h = go.Figure(
                    go.Bar(
                        x=[f"{a:,.0f}" for a in mids],
                        y=ph["counts"],
                        marker=dict(color=brand_purple, opacity=0.85),
                    )
                )
                fig_h.update_xaxes(title_text="Prima anual (centro de tramo, Bs.)", tickangle=-45)
                fig_h.update_yaxes(title_text="Pólizas")
                fig_h.update_layout(title="Distribución de prima anual")
                _brand_layout(fig_h, height=360)
                st.plotly_chart(fig_h, use_container_width=True)
        ah = pack.get("age_histogram") or {}
        with c2:
            if ah.get("ages"):
                fig_a = go.Figure(
                    go.Bar(
                        x=[str(a) for a in ah["ages"]],
                        y=ah["counts"],
                        marker=dict(color="#8B5CF6", opacity=0.85),
                    )
                )
                fig_a.update_xaxes(title_text="Edad a la emisión")
                fig_a.update_yaxes(title_text="Pólizas")
                fig_a.update_layout(title="Edades al emitir")
                _brand_layout(fig_a, height=360)
                st.plotly_chart(fig_a, use_container_width=True)

    with tab_c:
        lbm = pack.get("loss_by_month") or []
        if lbm:
            months = [r["month"] for r in lbm]
            clm = [r["claims"] for r in lbm]
            paid = [r["paid_sum"] for r in lbm]
            fig_l = make_subplots(specs=[[{"secondary_y": True}]])
            fig_l.add_trace(
                go.Bar(x=months, y=clm, name="Siniestros", marker_color="#f59e0b"),
                secondary_y=False,
            )
            fig_l.add_trace(
                go.Scatter(
                    x=months,
                    y=paid,
                    name="Monto pagado (Bs.)",
                    mode="lines+markers",
                    line=dict(color=brand_deep, width=2),
                ),
                secondary_y=True,
            )
            fig_l.update_xaxes(title_text="Mes de ocurrencia (loss_date)")
            fig_l.update_yaxes(title_text="Cantidad siniestros", secondary_y=False)
            fig_l.update_yaxes(title_text="Pagado del mes (Bs.)", secondary_y=True)
            fig_l.update_layout(legend=dict(orientation="h", y=1.12))
            _brand_layout(fig_l, height=400)
            st.plotly_chart(fig_l, use_container_width=True)

        cp = pack.get("cumulative_paid") or []
        if cp:
            fig_c = go.Figure(
                go.Scatter(
                    x=[r["month"] for r in cp],
                    y=[r["cumulative_paid"] for r in cp],
                    fill="tozeroy",
                    mode="lines",
                    line=dict(color=brand_purple, width=2),
                    fillcolor="rgba(112, 41, 179, 0.15)",
                    name="Pagado acumulado",
                )
            )
            fig_c.update_xaxes(title_text="Mes (loss_date)")
            fig_c.update_yaxes(title_text="Pagado acumulado (Bs.)")
            fig_c.update_layout(title="Evolución del pagado acumulado")
            _brand_layout(fig_c, height=340)
            st.plotly_chart(fig_c, use_container_width=True)

        sev = pack.get("claim_severity_histogram") or {}
        if sev.get("counts"):
            mids = [(sev["bin_lo"][i] + sev["bin_hi"][i]) / 2 for i in range(len(sev["counts"]))]
            fig_s = go.Figure(
                go.Bar(
                    x=[f"{m:,.0f}" for m in mids],
                    y=sev["counts"],
                    marker_color=accent_blue,
                )
            )
            fig_s.update_xaxes(title_text="Monto pagado por siniestro (centro de tramo, Bs.)", tickangle=-45)
            fig_s.update_yaxes(title_text="Siniestros")
            fig_s.update_layout(title="Distribución de severidad (pagado)")
            _brand_layout(fig_s, height=340)
            st.plotly_chart(fig_s, use_container_width=True)

    with tab_d:
        sc = pack.get("scatter_premium_vs_paid") or []
        if sc:
            df_sc = pd.DataFrame(sc)
            fig_sc = px.scatter(
                df_sc,
                x="annual_premium",
                y="paid_total",
                size="claim_n",
                color="claim_n",
                size_max=28,
                color_continuous_scale=[[0, "#e9d5ff"], [1, brand_deep]],
                labels={
                    "annual_premium": "Prima anual (Bs.)",
                    "paid_total": "Pagado acum. en la póliza (Bs.)",
                    "claim_n": "Nº siniestros",
                },
                title="Dispersión: prima vs pagado por póliza (tamaño = nº siniestros)",
            )
            fig_sc.update_traces(marker=dict(line=dict(width=0.5, color="white"), opacity=0.88))
            _brand_layout(fig_sc, height=480)
            st.plotly_chart(fig_sc, use_container_width=True)

        top = pack.get("top_policies_by_paid") or []
        if top:
            fig_t = go.Figure(
                go.Bar(
                    y=[r["policy_id"] for r in reversed(top)],
                    x=[r["paid_total"] for r in reversed(top)],
                    orientation="h",
                    marker=dict(color=brand_purple),
                    text=[f"{r['claim_n']} clm" for r in reversed(top)],
                    textposition="outside",
                )
            )
            fig_t.update_xaxes(title_text="Pagado acumulado (Bs.)")
            fig_t.update_layout(title="Top pólizas por monto pagado")
            _brand_layout(fig_t, height=min(520, 80 + 22 * len(top)))
            st.plotly_chart(fig_t, use_container_width=True)
