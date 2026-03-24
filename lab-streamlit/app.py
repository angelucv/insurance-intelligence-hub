"""Laboratorio: tablero demo enlazado a backend-compute (local o desplegado)."""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="Insurance Intelligence Hub — Demo",
    layout="wide",
    initial_sidebar_state="expanded",
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


def _fetch_kpi(base: str, cohort_year: int, seed: int, n_policies: int) -> dict[str, Any]:
    r = requests.get(
        f"{base}/api/v1/kpi/summary",
        params={"cohort_year": cohort_year, "seed": seed, "n_policies": n_policies},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _fetch_health(base: str) -> dict[str, Any]:
    r = requests.get(f"{base}/health", timeout=15)
    r.raise_for_status()
    return r.json()


st.title("Insurance Intelligence Hub")
st.caption("Demo funcional: API (FastAPI + DuckDB + Pydantic) + tablero. Datos sintéticos.")

base = _api_base()
with st.sidebar:
    st.subheader("Conexión")
    st.code(base, language="text")
    st.caption(
        "En Streamlit Cloud: Secrets → `COMPUTE_API_URL` = URL pública de la API (p. ej. Render)."
    )
    cohort_year = st.slider("Año cohorte (demo)", 2019, 2024, 2022)
    seed = st.number_input("Semilla aleatoria", min_value=1, max_value=9999, value=42, step=1)
    n_policies = st.select_slider("Pólizas sintéticas", options=[1000, 2000, 4000, 8000, 15000], value=8000)

if st.sidebar.button("Probar /health"):
    try:
        st.sidebar.success(_fetch_health(base))
    except Exception as e:
        st.sidebar.error(str(e))

try:
    data = _fetch_kpi(base, cohort_year, int(seed), int(n_policies))
except Exception as e:
    st.error(
        f"No se pudo obtener KPIs desde la API. Comprueba que esté en marcha y `COMPUTE_API_URL`. "
        f"Detalle: {e}"
    )
    st.stop()

st.info(data.get("data_note", ""))

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
            title={"text": "Siniestralidad / prima (sintético)"},
            gauge={
                "axis": {"range": [0, 120]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 70], "color": "lightgreen"},
                    {"range": [70, 100], "color": "khaki"},
                    {"range": [100, 120], "color": "salmon"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.8,
                    "value": 100,
                },
            },
        )
    )
    fig.update_layout(height=280)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Exportación (puente a Excel / Power BI)")
df = pd.DataFrame([data])
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Descargar KPIs como CSV",
    data=csv,
    file_name="kpi_summary_demo.csv",
    mime="text/csv",
)
