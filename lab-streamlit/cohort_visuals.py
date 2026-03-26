"""Gráficos Plotly para el paquete `/api/v1/kpi/cohort-portfolio` (Streamlit)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from plotly.subplots import make_subplots

# Centroides aproximados (demo visual) — nombres alineados a `portfolio_analytics._VE_ESTADOS`
VE_CENTROIDS: dict[str, tuple[float, float]] = {
    "Amazonas": (2.85, -63.9),
    "Anzoátegui": (9.2, -64.35),
    "Apure": (6.92, -68.77),
    "Aragua": (9.94, -67.19),
    "Barinas": (8.21, -69.95),
    "Bolívar": (6.25, -62.85),
    "Carabobo": (10.25, -68.0),
    "Cojedes": (9.2, -68.25),
    "Delta Amacuro": (9.27, -61.2),
    "Distrito Capital": (10.49, -66.88),
    "Falcón": (11.4, -69.6),
    "Guárico": (8.75, -66.25),
    "La Guaira": (10.6, -66.93),
    "Lara": (10.31, -69.8),
    "Mérida": (8.6, -71.16),
    "Miranda": (10.25, -66.33),
    "Monagas": (9.74, -63.18),
    "Nueva Esparta": (10.96, -63.93),
    "Portuguesa": (9.1, -69.2),
    "Sucre": (10.4, -63.3),
    "Táchira": (7.9, -72.14),
    "Trujillo": (9.4, -70.5),
    "Yaracuy": (10.34, -68.74),
    "Zulia": (9.0, -71.5),
}

# Natural Earth (ne_10m) usa "Vargas" para el estado hoy conocido como La Guaira.
VE_ESTADO_TO_NE_CHOROPLETH: dict[str, str] = {"La Guaira": "Vargas"}

# GeoJSON recortado (solo estados VE, propiedades mínimas) — ver `assets/venezuela_admin1.geojson`.
_VE_ADMIN1_GEOJSON_PATH = Path(__file__).resolve().parent / "assets" / "venezuela_admin1.geojson"


@st.cache_data(ttl=7 * 24 * 3600, show_spinner="Cargando mapa de estados (Venezuela)…")
def _ve_admin1_geojson() -> dict[str, Any] | None:
    try:
        if not _VE_ADMIN1_GEOJSON_PATH.is_file():
            return None
        raw = _VE_ADMIN1_GEOJSON_PATH.read_text(encoding="utf-8")
        g = json.loads(raw)
    except Exception:
        return None
    feats = [f for f in g.get("features", []) if f.get("properties", {}).get("name")]
    if not feats:
        return None
    return {"type": "FeatureCollection", "features": feats}


def _paid_by_ne_choropleth_name(rows: list[dict[str, Any]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for r in rows:
        en = r.get("estado") or ""
        if en not in VE_CENTROIDS:
            continue
        ne = VE_ESTADO_TO_NE_CHOROPLETH.get(en, en)
        val = float(r.get("paid_total") or r.get("prima_total") or 0)
        out[ne] = out.get(ne, 0.0) + val
    return out


def _gauge(title: str, value: float, rng: tuple[float, float], color: str) -> go.Indicator:
    return go.Indicator(
        mode="gauge+number",
        value=float(value),
        title={"text": title, "font": {"size": 11}},
        number={"font": {"size": 16}},
        gauge={
            "axis": {"range": list(rng)},
            "bar": {"color": color},
            "bgcolor": "white",
            "steps": [
                {"range": [rng[0], rng[0] + (rng[1] - rng[0]) * 0.5], "color": "#ecfdf5"},
                {"range": [rng[0] + (rng[1] - rng[0]) * 0.5, rng[1]], "color": "#fef3c7"},
            ],
            "threshold": {
                "line": {"color": "#b91c1c", "width": 2},
                "thickness": 0.75,
                "value": rng[1] * 0.92,
            },
        },
    )


def render_resumen_gauges(
    data_kpi: dict[str, Any],
    port_pack: dict[str, Any] | None,
    *,
    brand_purple: str,
) -> go.Figure:
    """Cuatro tacómetros compactos en una fila."""
    per = float(data_kpi.get("persistency_rate_pct") or 0)
    tlr = float(data_kpi.get("technical_loss_ratio_pct") or 0)
    lr_op = float(port_pack["operational_loss_ratio_pct"]) if port_pack and port_pack.get("operational_loss_ratio_pct") is not None else None
    n_pol = int(port_pack["policies_total"]) if port_pack else int(
        data_kpi.get("policies_active", 0) + data_kpi.get("policies_lapsed", 0)
    )
    n_clm = int(port_pack["claims_total"]) if port_pack else 0
    clm_rate = (n_clm / max(n_pol, 1)) * 100.0

    fig = make_subplots(
        rows=1,
        cols=4,
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
        horizontal_spacing=0.08,
    )
    fig.add_trace(_gauge("Persistencia %", min(per, 100), (0, 100), brand_purple), row=1, col=1)
    fig.add_trace(_gauge("Ratio técnico (demo)", min(tlr, 120), (0, 120), "#8B5CF6"), row=1, col=2)
    if lr_op is not None:
        fig.add_trace(_gauge("Pagado / prima %", min(lr_op, 100), (0, 100), "#0284c7"), row=1, col=3)
    else:
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=0,
                title={"text": "Pagado / prima %", "font": {"size": 11}},
                number={"prefix": "—"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#cbd5e1"},
                    "bgcolor": "white",
                },
            ),
            row=1,
            col=3,
        )
    fig.add_trace(_gauge("Siniestros / 100 pól.", min(clm_rate, 80), (0, 80), "#f59e0b"), row=1, col=4)
    fig.update_layout(height=240, margin=dict(l=16, r=16, t=28, b=8), paper_bgcolor="rgba(0,0,0,0)")
    return fig


def render_territorio_ve(
    pack: dict[str, Any],
    *,
    brand_purple: str,
) -> None:
    geo = pack.get("geo_estado_demo") or {}
    rows = geo.get("rows") or []
    if geo.get("note"):
        st.caption(geo["note"])
    if not rows:
        st.info("Sin filas territoriales.")
        return

    modo = st.radio(
        "Visualización del mapa",
        options=["estados", "pines", "calor"],
        format_func=lambda x: {
            "estados": "Estados completos (relleno)",
            "pines": "Pines por estado",
            "calor": "Mapa tipo calor",
        }[x],
        horizontal=True,
        key="ve_map_mode",
    )

    _geo_common = dict(
        scope="south america",
        lonaxis_range=[-74.5, -58.5],
        lataxis_range=[0.5, 13.5],
        showland=True,
        landcolor="#f1f5f9",
        countrycolor="#cbd5e1",
        oceancolor="#e0f2fe",
        showocean=True,
        projection_type="natural earth",
    )

    if modo in ("estados", "calor"):
        fc = _ve_admin1_geojson()
        if not fc:
            st.warning("No se pudo cargar el mapa de estados; se muestran pines.")
            modo = "pines"
        else:
            val_by = _paid_by_ne_choropleth_name(rows)
            locations: list[str] = []
            zvals: list[float] = []
            hover_texts: list[str] = []
            for f in fc["features"]:
                nm = f["properties"]["name"]
                locations.append(nm)
                zv = float(val_by.get(nm, 0.0))
                zvals.append(zv)
                row_hint = next((r for r in rows if VE_ESTADO_TO_NE_CHOROPLETH.get(r["estado"], r["estado"]) == nm), None)
                if row_hint:
                    hover_texts.append(
                        f"{row_hint['estado']}<br>Pólizas: {row_hint['n_policies']:,}<br>"
                        f"Siniestros: {row_hint['n_claims']:,}<br>Pagado: {row_hint['paid_total']:,.0f} Bs."
                    )
                else:
                    hover_texts.append(f"{nm}<br>Pagado agregado: {zv:,.0f} Bs.")

            if modo == "calor":
                cscale = "YlOrRd"
                title = "Venezuela — intensidad (escala tipo calor, pagado Bs. por estado)"
            else:
                cscale = [[0, "#f5f3ff"], [0.45, "#c4b5fd"], [1, brand_purple]]
                title = "Venezuela — pagado por estado (relleno regional)"

            fig = go.Figure(
                go.Choropleth(
                    geojson=fc,
                    locations=locations,
                    z=zvals,
                    featureidkey="properties.name",
                    colorscale=cscale,
                    marker_line_color="#ffffff",
                    marker_line_width=0.6,
                    colorbar=dict(title="Pagado (Bs.)"),
                    text=hover_texts,
                    hoverinfo="text",
                )
            )
            fig.update_geos(**_geo_common)
            fig.update_layout(
                title=title,
                height=520,
                margin=dict(l=0, r=0, t=48, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

    if modo == "pines":
        lats, lons, sizes, colors, texts = [], [], [], [], []
        for r in rows:
            en = r["estado"]
            if en not in VE_CENTROIDS:
                continue
            lat, lon = VE_CENTROIDS[en]
            lats.append(lat)
            lons.append(lon)
            npol = max(1, int(r["n_policies"]))
            sizes.append(10 + min(36, npol**0.5 * 1.6))
            colors.append(float(r.get("paid_total") or r.get("prima_total") or 0))
            texts.append(
                f"{en}<br>Pólizas: {r['n_policies']:,}<br>Siniestros: {r['n_claims']:,}<br>Pagado: {r['paid_total']:,.0f} Bs."
            )
        fig = go.Figure(
            go.Scattergeo(
                lat=lats,
                lon=lons,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=colors,
                    colorscale=[[0, "#e9d5ff"], [0.5, "#a78bfa"], [1, brand_purple]],
                    colorbar=dict(title="Pagado (Bs.)"),
                    line=dict(width=1.5, color="white"),
                    sizemode="diameter",
                    symbol="circle",
                ),
                text=texts,
                hoverinfo="text",
            )
        )
        fig.update_geos(**_geo_common)
        fig.update_layout(
            title="Venezuela — pines por estado (tamaño ≈ pólizas, color ≈ pagado)",
            height=520,
            margin=dict(l=0, r=0, t=48, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    df_b = pd.DataFrame(rows)
    if not df_b.empty and "paid_total" in df_b.columns:
        df_b = df_b.sort_values("paid_total", ascending=False)
    st.dataframe(df_b, use_container_width=True, hide_index=True)


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
    cy = pack["cohort_year"]
    st.subheader("Laboratorio analítico de cartera")
    lr = pack.get("operational_loss_ratio_pct")
    st.caption(
        f"Cohorte **{cy}** · {pack['policies_total']:,} pólizas · {pack['claims_total']:,} siniestros · "
        f"prima total {pack['total_annual_premium']:,.0f} Bs. · pagado {pack['total_paid_claims']:,.0f} Bs."
        + (f" · ratio pagado/prima **{lr:.2f} %**" if lr is not None else "")
    )

    tab_a, tab_b, tab_c, tab_d, tab_e = st.tabs(
        ["Panorama", "Emisión", "Siniestralidad", "Prima vs siniestro", "Riesgo avanzado"],
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
            n_cat = len(cs)
            if n_cat <= 1:
                if n_cat == 1:
                    label, qty = next(iter(cs.items()))
                    st.metric(label=f"Siniestros en estado «{label}»", value=f"{int(qty):,}")
                    st.caption("Un solo estado en la carga: se muestra como métrica en lugar de barras.")
                else:
                    st.info("Sin categorías de estado de siniestro.")
            elif n_cat <= 6:
                labels = list(cs.keys())
                vals = [int(cs[k]) for k in labels]
                fig_cs = go.Figure(
                    go.Bar(
                        y=labels,
                        x=vals,
                        orientation="h",
                        marker_color=accent_blue,
                        text=vals,
                        textposition="outside",
                    )
                )
                fig_cs.update_yaxes(title_text="Estado")
                fig_cs.update_xaxes(title_text="Cantidad")
                fig_cs.update_layout(title="Distribución por estado de carga")
                _brand_layout(fig_cs, height=max(280, 56 * n_cat))
                st.plotly_chart(fig_cs, use_container_width=True)
            else:
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
            if len(ibm) == 1:
                r0 = ibm[0]
                c_m1, c_m2 = st.columns(2)
                with c_m1:
                    st.metric("Pólizas emitidas", f"{int(r0['policies']):,}", help=f"Mes {r0['month']}")
                with c_m2:
                    st.metric("Prima emitida (Bs.)", f"{float(r0['premium_sum']):,.0f}", help="Suma prima anual en el mes")
                st.caption(
                    f"Mes de emisión (issue_date): **{r0['month']}** · Solo hay un período en los datos; "
                    "el combo barras+línea no aporta, así que se muestran métricas."
                )
            else:
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

    with tab_e:
        st.markdown("#### Mapa de calor: mes de emisión × mes de siniestro")
        hm = pack.get("heatmap_issue_loss_month") or {}
        if hm.get("note"):
            st.caption(hm["note"])
        z = hm.get("z") or []
        if z and any(any(row) for row in z):
            fig_hm = go.Figure(
                go.Heatmap(
                    z=z,
                    x=[f"M{m}" for m in hm.get("x_labels", [])],
                    y=[f"Emisión M{m}" for m in hm.get("y_labels", [])],
                    colorscale=[[0, "#f5f3ff"], [0.5, "#a78bfa"], [1, brand_deep]],
                    hovertemplate="Emisión mes %{y}<br>Ocurrencia mes %{x}<br>Casos: %{z}<extra></extra>",
                )
            )
            fig_hm.update_layout(xaxis_title="Mes calendario (loss_date)", yaxis_title="Mes calendario (issue_date)")
            _brand_layout(fig_hm, height=440)
            st.plotly_chart(fig_hm, use_container_width=True)
        else:
            st.info("Sin siniestros para armar el mapa de calor.")

        st.markdown("#### Supervivencia (Kaplan–Meier demo)")
        km = pack.get("km_survival_lapsed_demo") or {}
        if km.get("note"):
            st.caption(km["note"])
        pts = km.get("points") or []
        if len(pts) > 1:
            fig_km = go.Figure(
                go.Scatter(
                    x=[p["t_days"] for p in pts],
                    y=[p["survival"] for p in pts],
                    mode="lines+markers",
                    line=dict(color=brand_purple, width=2),
                    fill="tozeroy",
                    fillcolor="rgba(112, 41, 179, 0.12)",
                    name="S(t)",
                )
            )
            fig_km.update_xaxes(title_text="Días desde emisión")
            fig_km.update_yaxes(title_text="Prob. supervivencia (persistencia) estimada", range=[0, 1.05])
            _brand_layout(fig_km, height=360)
            st.plotly_chart(fig_km, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Boxplot: prima por tramo de edad")
            samp = pack.get("box_samples_age_band") or {}
            rows = [{"tramo": k, "prima": v} for k, vals in samp.items() for v in vals]
            if rows:
                df_bx = pd.DataFrame(rows)
                fig_bx = px.box(
                    df_bx,
                    x="tramo",
                    y="prima",
                    color="tramo",
                    color_discrete_sequence=px.colors.sequential.Purples_r,
                )
                fig_bx.update_layout(showlegend=False, yaxis_title="Prima anual (Bs.)")
                _brand_layout(fig_bx, height=380)
                st.plotly_chart(fig_bx, use_container_width=True)
        with c2:
            st.markdown("#### Boxplot: prima por estado de póliza")
            samp_s = pack.get("box_samples_status") or {}
            rows_s = [{"estado": k, "prima": v} for k, vals in samp_s.items() for v in vals]
            if rows_s:
                df_s = pd.DataFrame(rows_s)
                fig_s = px.box(df_s, x="estado", y="prima", color="estado", color_discrete_map={"active": brand_purple, "lapsed": "#94a3b8"})
                fig_s.update_layout(showlegend=False, yaxis_title="Prima anual (Bs.)")
                _brand_layout(fig_s, height=380)
                st.plotly_chart(fig_s, use_container_width=True)

        st.markdown("#### Ratio de “burn” mensual y media móvil (3 meses)")
        st.caption(
            "Burn % = pagado del mes ÷ prima acumulada emitida hasta ese mes. "
            "Proxy demo; no sustituye un LR técnico contable."
        )
        rl = pack.get("rolling_lr_monthly") or []
        if rl:
            months = [r["month"] for r in rl]
            fig_r = go.Figure()
            fig_r.add_trace(
                go.Bar(x=months, y=[r["burn_pct"] for r in rl], name="Burn % mensual", marker_color="#c4b5fd"),
            )
            fig_r.add_trace(
                go.Scatter(
                    x=months,
                    y=[r.get("rolling_burn_3m_avg") for r in rl],
                    name="Media móvil 3m (burn %)",
                    mode="lines+markers",
                    line=dict(color=accent_blue, width=3),
                ),
            )
            fig_r.update_yaxes(title_text="Porcentaje (%)")
            fig_r.update_xaxes(title_text="Mes")
            fig_r.update_layout(legend=dict(orientation="h", y=1.12))
            _brand_layout(fig_r, height=400)
            st.plotly_chart(fig_r, use_container_width=True)
