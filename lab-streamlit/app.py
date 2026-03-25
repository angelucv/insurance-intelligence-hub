"""Laboratorio: KPIs (API); la carga de maestros es solo vía Django Admin."""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="Insurance Intelligence Hub — Lab",
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


st.title("Insurance Intelligence Hub — Laboratorio")
st.caption(
    "KPIs vía API (DuckDB / Postgres). La carga de CSV/XLSX es interna en Django Admin (usuarios y trazabilidad)."
)

base = _api_base()
upload_path = _admin_upload_hint()

st.info(
    f"**Carga de pólizas:** usa Django Admin → [ruta de carga]({upload_path}) "
    f"(inicia sesión con staff). Opcional: define el secreto `DJANGO_ADMIN_BASE_URL` "
    f"(p. ej. `https://tu-admin.onrender.com`) para un enlace absoluto."
)

with st.sidebar:
    st.subheader("Conexión API")
    st.code(base, language="text")
    st.caption("Streamlit Cloud: Secret `COMPUTE_API_URL`.")
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
            title={"text": "Indicador sintético / proxy"},
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

st.subheader("Exportación (Excel / Power BI)")
df = pd.DataFrame([data])
st.download_button(
    "Descargar KPIs como CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="kpi_summary_demo.csv",
    mime="text/csv",
)
