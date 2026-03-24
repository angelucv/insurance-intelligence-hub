"""Laboratorio: KPIs + carga de archivos hacia la API (demo completa)."""

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


def _ingest_key() -> str | None:
    try:
        if "INGEST_API_KEY" in st.secrets:
            k = st.secrets["INGEST_API_KEY"]
            return str(k).strip() or None
    except FileNotFoundError:
        pass
    k = os.environ.get("INGEST_API_KEY")
    return k.strip() if k else None


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


def _post_ingest(base: str, uploaded: Any, api_key: str | None) -> requests.Response:
    headers: dict[str, str] = {}
    if api_key:
        headers["X-API-Key"] = api_key
    files = {
        "file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream"),
    }
    return requests.post(
        f"{base}/api/v1/ingest/policies",
        files=files,
        headers=headers,
        timeout=120,
    )


st.title("Insurance Intelligence Hub — Laboratorio")
st.caption(
    "Flujo demo: carga CSV/Excel → API (Pydantic) → PostgreSQL → KPIs (DuckDB). "
    "Sin BD, los KPI pueden ser sintéticos."
)

base = _api_base()
ingest_key = _ingest_key()

tab_dash, tab_ingest = st.tabs(["Dashboard KPI", "Carga de pólizas"])

with st.sidebar:
    st.subheader("Conexión")
    st.code(base, language="text")
    st.caption("Streamlit Cloud: Secrets `COMPUTE_API_URL` y, si aplica, `INGEST_API_KEY`.")
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

with tab_ingest:
    st.subheader("Subir maestro (.csv / .xlsx)")
    st.markdown(
        "Columnas requeridas: `policy_id`, `cohort_year`, `issue_age`, `annual_premium`, `status` "
        "(active/lapsed). Ver `docs/sample-policies.csv`."
    )
    up = st.file_uploader("Archivo", type=["csv", "xlsx", "xls"])
    if up and st.button("Enviar a la API"):
        try:
            resp = _post_ingest(base, up, ingest_key)
            st.code(f"HTTP {resp.status_code}\n{resp.text[:4000]}")
        except Exception as e:
            st.error(str(e))

with tab_dash:
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
