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
_GAUGE_PRIMARY = _BRAND_PURPLE
_GAUGE_ACCENT = "#8B5CF6"


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


def _fetch_health(base: str) -> dict[str, Any]:
    r = requests.get(f"{base}/health", timeout=15)
    r.raise_for_status()
    return r.json()


# —— Cabecera visual (marca Seguros La Fe: morado / violeta) ——
_hdr_l, _hdr_r = st.columns([1, 4])
with _hdr_l:
    if _LOGO_FE1.is_file():
        st.image(str(_LOGO_FE1), use_container_width=True)
with _hdr_r:
    st.markdown(
        f"""
        <div style="
            padding: 1.35rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.25rem;
            background: linear-gradient(125deg, {_BRAND_DEEP} 0%, {_GAUGE_PRIMARY} 45%, {_GAUGE_ACCENT} 100%);
            box-shadow: 0 10px 28px rgba(88, 28, 135, 0.25);
        ">
            <h1 style="color: white; margin: 0; font-size: 1.65rem; font-weight: 700;">
                Laboratorio analítico
            </h1>
            <p style="color: rgba(255,255,255,0.92); margin: 0.5rem 0 0 0; font-size: 1rem;">
                Gráficos, indicadores y exportación CSV. Datos desde la API; carga del maestro en Django Admin.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

base = _api_base()
upload_path = _admin_upload_hint()
portal = _portal_reflex_url()

nav_cols = st.columns([3, 1])
with nav_cols[0]:
    st.caption(
        f"[Carga de pólizas (Admin)]({upload_path}) · línea gráfica Seguros La Fe (demo)."
    )
with nav_cols[1]:
    if portal:
        st.markdown(
            f'<a href="{portal}" target="_blank" rel="noopener noreferrer" '
            f'style="display:inline-block;padding:0.45rem 1rem;background:{_BRAND_PURPLE};'
            'color:white;border-radius:8px;text-decoration:none;font-weight:600;">'
            "Portal ejecutivo (Reflex)</a>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("Secret `PORTAL_REFLEX_URL` para enlace al portal.")

with st.sidebar:
    st.subheader("Conexión API")
    st.code(base, language="text")
    st.caption("`COMPUTE_API_URL` en Streamlit Cloud.")
    use_db = st.toggle("Preferir datos en base de datos", value=True)
    cohort_year = st.slider("Año cohorte", 2019, 2024, 2022)
    seed = st.number_input("Semilla (modo sintético)", min_value=1, max_value=9999, value=42, step=1)
    n_policies = st.select_slider(
        "Pólizas sintéticas (fallback)",
        options=[1000, 2000, 4000, 8000, 15000],
        value=8000,
    )
    if st.button("Probar /health"):
        try:
            st.success(_fetch_health(base))
        except Exception as e:
            st.error(str(e))
    try:
        hb = requests.get(f"{base}/api/v1/health/db", timeout=15)
        if hb.ok:
            st.caption(f"BD en API: {'sí' if hb.json().get('database_configured') else 'no'}")
    except Exception:
        pass

try:
    data = _fetch_kpi(base, cohort_year, int(seed), int(n_policies), use_db)
except Exception as e:
    st.error(f"No se pudo obtener KPIs: {e}")
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

st.subheader("Exportación (Excel / Power BI)")
df = pd.DataFrame([data])
st.download_button(
    "Descargar KPIs como CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="kpi_summary_demo.csv",
    mime="text/csv",
)

st.caption(
    "Seguros La Fe · RIF J-000467382 · SUDEASEG N.º 62 · Insurance Intelligence Hub (demo técnico)."
)
