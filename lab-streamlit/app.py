"""Laboratorio: visualización rica (Plotly) + KPIs API; carga solo vía Django Admin."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="Insurance Intelligence Hub — Laboratorio",
    layout="wide",
    initial_sidebar_state="expanded",
)

_LOGO_FE1 = Path(__file__).resolve().parent / "assets" / "logo-fe-1.jpg"

_BRAND_PURPLE = "#7029B3"
_BRAND_DEEP = "#5a1f94"
_MARKET_TOTAL_LINE = "#0284c7"
_GAUGE_PRIMARY = _BRAND_PURPLE
_GAUGE_ACCENT = "#8B5CF6"

_BTN_STYLE = (
    "display:inline-block;padding:0.55rem 1.25rem;background:{bg};color:white;"
    "border-radius:10px;text-decoration:none;font-weight:600;font-size:0.95rem;"
    "border:none;cursor:pointer;box-shadow:0 2px 8px rgba(88,28,135,0.25);"
)
_BTN_SECONDARY = (
    "display:inline-block;padding:0.55rem 1.25rem;background:white;color:{c};"
    "border-radius:10px;text-decoration:none;font-weight:600;font-size:0.95rem;"
    "border:2px solid {c};cursor:pointer;"
)


def _api_base() -> str:
    default = "http://127.0.0.1:8000"
    try:
        if "COMPUTE_API_URL" in st.secrets:
            return str(st.secrets["COMPUTE_API_URL"]).rstrip("/")
    except FileNotFoundError:
        pass
    env_url = os.environ.get("COMPUTE_API_URL")
    if env_url:
        return env_url.rstrip("/")
    return default.rstrip("/")


def _admin_upload_hint() -> str:
    try:
        if "DJANGO_ADMIN_BASE_URL" in st.secrets:
            u = str(st.secrets["DJANGO_ADMIN_BASE_URL"]).rstrip("/")
            return f"{u}/admin/upload-policies/"
    except FileNotFoundError:
        pass
    env_u = os.environ.get("DJANGO_ADMIN_BASE_URL")
    if env_u:
        return f"{env_u.rstrip('/')}/admin/upload-policies/"
    return "/admin/upload-policies/"


def _portal_reflex_url() -> str | None:
    try:
        if "PORTAL_REFLEX_URL" in st.secrets:
            u = str(st.secrets["PORTAL_REFLEX_URL"]).strip().rstrip("/")
            return u or None
    except FileNotFoundError:
        pass
    env_u = os.environ.get("PORTAL_REFLEX_URL", "").strip().rstrip("/")
    return env_u or None


def _fetch_market_series(
    base: str,
    path: str,
    from_year: int,
    to_year: int,
    mode: str,
) -> dict[str, Any]:
    r = requests.get(
        f"{base}{path}",
        params={"from_year": from_year, "to_year": to_year, "mode": mode},
        timeout=90,
    )
    r.raise_for_status()
    return r.json()


def _merge_market_primas(
    la_fe_payload: dict[str, Any],
    totals_payload: dict[str, Any],
) -> pd.DataFrame:
    p1 = la_fe_payload.get("points") or []
    p2 = totals_payload.get("points") or []
    if not p1 and not p2:
        return pd.DataFrame()
    d1 = pd.DataFrame(p1)
    d2 = pd.DataFrame(p2)
    if d1.empty or d2.empty:
        return pd.DataFrame()
    d1 = d1.rename(columns={"primas_netas_thousands_bs": "primas_la_fe_thousands_bs"})
    d2 = d2.rename(columns={"primas_netas_thousands_bs": "primas_mercado_thousands_bs"})
    m = pd.merge(
        d1[["period_year", "period_month", "primas_la_fe_thousands_bs"]],
        d2[["period_year", "period_month", "primas_mercado_thousands_bs"]],
        on=["period_year", "period_month"],
        how="outer",
    ).sort_values(["period_year", "period_month"])
    m["periodo"] = (
        m["period_year"].astype(int).astype(str)
        + "-"
        + m["period_month"].astype(int).astype(str).str.zfill(2)
    )
    return m


def _fetch_kpi(
    base: str,
    cohort_year: int,
    seed: int,
    n_policies: int,
    use_db: bool,
) -> dict[str, Any]:
    r = requests.get(
        f"{base}/api/v1/kpi/summary",
        params={
            "cohort_year": cohort_year,
            "seed": seed,
            "n_policies": n_policies,
            "use_db": str(use_db).lower(),
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


# —— Cabecera: logo grande centrado (sin tarjeta “Laboratorio analítico”) ——
_, ctr, _ = st.columns([1, 2.2, 1])
with ctr:
    if _LOGO_FE1.is_file():
        st.image(str(_LOGO_FE1), use_container_width=True)
    else:
        st.markdown("### Insurance Intelligence Hub")

base = _api_base()
upload_path = _admin_upload_hint()
portal = _portal_reflex_url()

st.markdown(
    f"""
    <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:0.5rem 0 1.25rem 0;">
      <a href="{upload_path}" target="_blank" rel="noopener noreferrer"
         style="{_BTN_STYLE.format(bg=_BRAND_PURPLE)}">
        Carga de pólizas (Admin)
      </a>
      {f'<a href="{portal}" target="_blank" rel="noopener noreferrer" style="{_BTN_SECONDARY.format(c=_BRAND_PURPLE)}">Portal ejecutivo (Reflex)</a>' if portal else ""}
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Parámetros de análisis")
    use_db = st.toggle("Usar datos en base de datos", value=True)
    cohort_year = st.slider("Año cohorte", 2019, 2024, 2022)
    seed = st.number_input("Semilla (datos sintéticos de respaldo)", min_value=1, max_value=9999, value=42, step=1)
    n_policies = st.select_slider(
        "Tamaño cohorte sintética (respaldo)",
        options=[1000, 2000, 4000, 8000, 15000],
        value=8000,
    )

tab_demo, tab_mercado = st.tabs(["Cohorte demo", "Mercado SUDEASEG"])

with tab_demo:
    try:
        data = _fetch_kpi(base, cohort_year, int(seed), int(n_policies), use_db)
    except Exception as e:
        st.error(f"No se pudo obtener los indicadores. Comprueba la conexión o inténtalo más tarde. ({e})")
        st.stop()

    if data.get("data_note"):
        st.info(data["data_note"])

    st.subheader("Indicadores clave")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Persistencia", f"{data['persistency_rate_pct']:.2f} %")
    c2.metric("Pólizas activas", f"{data['policies_active']:,}")
    c3.metric("Lapsos", f"{data['policies_lapsed']:,}")
    c4.metric("Prima media anual", f"{data['avg_annual_premium']:,.2f}")

    tlr = data.get("technical_loss_ratio_pct")
    if tlr is not None:
        st.subheader("Ratio técnico (demo)")
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=float(tlr),
                title={"text": "Indicador sintético / proxy"},
                gauge={
                    "axis": {"range": [0, 120]},
                    "bar": {"color": _GAUGE_PRIMARY},
                    "steps": [
                        {"range": [0, 70], "color": "#d1fae5"},
                        {"range": [70, 100], "color": "#fef3c7"},
                        {"range": [100, 120], "color": "#fecaca"},
                    ],
                    "threshold": {
                        "line": {"color": "#b91c1c", "width": 4},
                        "thickness": 0.8,
                        "value": 100,
                    },
                },
            )
        )
        fig.update_layout(
            height=300,
            margin=dict(l=24, r=24, t=48, b=24),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Exportación")
    df = pd.DataFrame([data])
    st.download_button(
        "Descargar KPIs como CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="kpi_summary_demo.csv",
        mime="text/csv",
    )

with tab_mercado:
    st.subheader("Primas netas: La Fe vs total de mercado")
    st.caption(
        "Datos según cuadro resumen SUDEASEG cargado en el hub. Unidades: miles de bolívares. "
        "Modo mensual = flujo del mes; YTD = acumulado a cierre de mes."
    )
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        m_from = st.number_input("Desde año", min_value=2000, max_value=2100, value=2023, step=1)
    with mc2:
        m_to = st.number_input("Hasta año", min_value=2000, max_value=2100, value=2026, step=1)
    with mc3:
        m_mode = st.selectbox("Modo", options=["monthly_flow", "ytd"], format_func=lambda x: "Flujo mensual" if x == "monthly_flow" else "YTD (cierre de mes)")

    if m_from > m_to:
        st.warning("Ajusta el rango de años (desde ≤ hasta).")
    else:
        try:
            la_payload = _fetch_market_series(
                base,
                "/api/v1/market/la-fe/resumen-series",
                int(m_from),
                int(m_to),
                str(m_mode),
            )
            tot_payload = _fetch_market_series(
                base,
                "/api/v1/market/resumen/totals-series",
                int(m_from),
                int(m_to),
                str(m_mode),
            )
        except Exception as e:
            st.error(
                "No se pudieron obtener las series de mercado. "
                "Comprueba que la API compute tenga DATABASE_URL y las migraciones SUDEASEG aplicadas. "
                f"({e})"
            )
        else:
            merged = _merge_market_primas(la_payload, tot_payload)
            if merged.empty:
                st.info("No hay puntos en el rango elegido o faltan datos en la tabla de mercado.")
            else:
                fig_m = go.Figure()
                fig_m.add_trace(
                    go.Scatter(
                        x=merged["periodo"],
                        y=merged["primas_la_fe_thousands_bs"],
                        name="La Fe",
                        mode="lines+markers",
                        line={"color": _BRAND_PURPLE},
                    )
                )
                fig_m.add_trace(
                    go.Scatter(
                        x=merged["periodo"],
                        y=merged["primas_mercado_thousands_bs"],
                        name="Mercado (total)",
                        mode="lines+markers",
                        line={"color": _MARKET_TOTAL_LINE},
                    )
                )
                fig_m.update_layout(
                    height=420,
                    margin=dict(l=24, r=24, t=48, b=24),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    yaxis_title="Miles de Bs.",
                    xaxis_title="Período (año-mes)",
                    hovermode="x unified",
                )
                st.plotly_chart(fig_m, use_container_width=True)

                st.subheader("Detalle y exportación")
                st.dataframe(merged, use_container_width=True, hide_index=True)
                csv_bytes = merged.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Descargar tabla fusionada (CSV)",
                    data=csv_bytes,
                    file_name="market_la_fe_vs_totales.csv",
                    mime="text/csv",
                )
                with st.expander("Notas de filtro (API)"):
                    st.write(la_payload.get("empresa_filter_note", ""))
                    st.write(tot_payload.get("empresa_filter_note", ""))

st.caption(
    "Seguros La Fe · RIF J-000467382 · SUDEASEG N.º 62 · Insurance Intelligence Hub (demo técnico)."
)
