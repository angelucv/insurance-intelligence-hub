"""App Streamlit: KPIs y mercado SUDEASEG vía API compute; carga de datos vía Django Admin."""

from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

# Streamlit Cloud suele usar la raíz del repo como cwd; el módulo vive junto a app.py.
_LAB_DIR = Path(__file__).resolve().parent
if str(_LAB_DIR) not in sys.path:
    sys.path.insert(0, str(_LAB_DIR))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st

from cohort_visuals import (
    _analitica_section_banner,
    fetch_cohort_portfolio,
    render_portfolio_pack,
    render_resumen_gauges,
    render_territorio_ve,
)

st.set_page_config(
    page_title="Insurance Intelligence Hub",
    layout="wide",
    initial_sidebar_state="expanded",
)

_LOGO_FE1 = Path(__file__).resolve().parent / "assets" / "logo-fe-1.jpg"

_BRAND_PURPLE = "#7029B3"
_BRAND_DEEP = "#5a1f94"
_MARKET_TOTAL_LINE = "#0284c7"

_MERCADO_SECTION_LABELS = (
    "Primas vs mercado",
    "Último cierre",
    "Métricas resumen",
    "Cuadro de resultados",
)
_MERCADO_SECTION_COLORS: dict[str, str] = {
    "Primas vs mercado": "#0284c7",
    "Último cierre": "#0d9488",
    "Métricas resumen": "#d97706",
    "Cuadro de resultados": "#7c3aed",
}
_MERCADO_SECTION_SUB: dict[str, str] = {
    "Primas vs mercado": "Comparación La Fe vs total mercado (rango y modo en la barra lateral)",
    "Último cierre": "Instantánea YTD al último mes con dato La Fe",
    "Métricas resumen": "Series extendidas La Fe y totales de mercado",
    "Cuadro de resultados": "Resultado técnico y operativo La Fe vs mercado",
}

# Misma familia de estilos que analítica de cartera (pills coloreadas en área principal)
_MERCADO_PILLS_CSS = """
<style>
[data-testid="stMain"] [data-testid="stPills"] {
    gap: 0.45rem !important;
    flex-wrap: wrap !important;
    padding: 0.25rem 0 0.15rem 0 !important;
}
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"] {
    border-radius: 999px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease, box-shadow 0.15s ease !important;
    background: #ffffff !important;
}
/* 1 Primas — azul mercado */
[data-testid="stMain"] [data-testid="stPills"] > div > button:nth-child(1),
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"]:nth-of-type(1) {
    border: 1px solid rgba(2, 132, 199, 0.45) !important;
    color: #0369a1 !important;
}
[data-testid="stMain"] [data-testid="stPills"] > div > button:nth-child(1)[aria-pressed="true"],
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"]:nth-of-type(1)[aria-pressed="true"] {
    background: linear-gradient(160deg, rgba(2, 132, 199, 0.2) 0%, #ffffff 72%) !important;
    border-color: #0284c7 !important;
    color: #0c4a6e !important;
    box-shadow: 0 2px 10px rgba(2, 132, 199, 0.22) !important;
}
/* 2 Último cierre — teal */
[data-testid="stMain"] [data-testid="stPills"] > div > button:nth-child(2),
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"]:nth-of-type(2) {
    border: 1px solid rgba(13, 148, 136, 0.45) !important;
    color: #0f766e !important;
}
[data-testid="stMain"] [data-testid="stPills"] > div > button:nth-child(2)[aria-pressed="true"],
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"]:nth-of-type(2)[aria-pressed="true"] {
    background: linear-gradient(160deg, rgba(13, 148, 136, 0.2) 0%, #ffffff 72%) !important;
    border-color: #0d9488 !important;
    color: #115e59 !important;
    box-shadow: 0 2px 10px rgba(13, 148, 136, 0.2) !important;
}
/* 3 Métricas — ámbar */
[data-testid="stMain"] [data-testid="stPills"] > div > button:nth-child(3),
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"]:nth-of-type(3) {
    border: 1px solid rgba(217, 119, 6, 0.45) !important;
    color: #b45309 !important;
}
[data-testid="stMain"] [data-testid="stPills"] > div > button:nth-child(3)[aria-pressed="true"],
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"]:nth-of-type(3)[aria-pressed="true"] {
    background: linear-gradient(160deg, rgba(217, 119, 6, 0.2) 0%, #ffffff 72%) !important;
    border-color: #d97706 !important;
    color: #92400e !important;
    box-shadow: 0 2px 10px rgba(217, 119, 6, 0.2) !important;
}
/* 4 Cuadro — violeta */
[data-testid="stMain"] [data-testid="stPills"] > div > button:nth-child(4),
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"]:nth-of-type(4) {
    border: 1px solid rgba(124, 58, 237, 0.42) !important;
    color: #6d28d9 !important;
}
[data-testid="stMain"] [data-testid="stPills"] > div > button:nth-child(4)[aria-pressed="true"],
[data-testid="stMain"] [data-testid="stPills"] button[kind="pill"]:nth-of-type(4)[aria-pressed="true"] {
    background: linear-gradient(160deg, rgba(124, 58, 237, 0.2) 0%, #ffffff 72%) !important;
    border-color: #7c3aed !important;
    color: #5b21b6 !important;
    box-shadow: 0 2px 10px rgba(124, 58, 237, 0.2) !important;
}
</style>
"""

# Estilos: barra lateral en paneles, pestañas principales y separación en contenido
st.markdown(
    f"""
    <style>
      [data-testid="stSidebar"] section[data-testid="stSidebarContent"] {{
        background: linear-gradient(165deg, #f8f5fc 0%, #ffffff 55%);
      }}
      [data-testid="stSidebar"] .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
      }}
      /* Pills (ámbito / vista): más legibles en sidebar */
      [data-testid="stSidebar"] [data-testid="stPills"] {{
        gap: 0.35rem;
        flex-wrap: wrap;
      }}
      [data-testid="stSidebar"] button[kind="pill"] {{
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.35rem 0.85rem !important;
      }}
      [data-testid="stSidebar"] button[kind="pill"][aria-pressed="true"] {{
        background: linear-gradient(135deg, #ede4f7 0%, #f5f0fb 100%) !important;
        border-color: {_BRAND_PURPLE} !important;
        color: {_BRAND_DEEP} !important;
      }}
      /* Pestañas del área principal */
      .stTabs [data-baseweb="tab-list"] {{
        gap: 0.25rem;
        background: #f1f5f9;
        padding: 0.35rem 0.5rem 0 0.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
      }}
      .stTabs [data-baseweb="tab"] {{
        border-radius: 10px 10px 0 0;
        font-weight: 600;
      }}
      .stTabs [aria-selected="true"] {{
        color: {_BRAND_DEEP} !important;
        border-bottom: 2px solid {_BRAND_PURPLE} !important;
      }}
      /* Bloques de página: aire entre secciones */
      .main-section-title {{
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #64748b;
        margin: 0 0 0.5rem 0;
      }}
      hr.main-sep {{
        margin: 1.25rem 0 1rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
      }}
    </style>
    """,
    unsafe_allow_html=True,
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


def _admin_upload_claims_hint() -> str:
    try:
        if "DJANGO_ADMIN_BASE_URL" in st.secrets:
            u = str(st.secrets["DJANGO_ADMIN_BASE_URL"]).rstrip("/")
            return f"{u}/admin/upload-claims/"
    except FileNotFoundError:
        pass
    env_u = os.environ.get("DJANGO_ADMIN_BASE_URL")
    if env_u:
        return f"{env_u.rstrip('/')}/admin/upload-claims/"
    return "/admin/upload-claims/"


def _portal_reflex_url() -> str | None:
    try:
        if "PORTAL_REFLEX_URL" in st.secrets:
            u = str(st.secrets["PORTAL_REFLEX_URL"]).strip().rstrip("/")
            return u or None
    except FileNotFoundError:
        pass
    env_u = os.environ.get("PORTAL_REFLEX_URL", "").strip().rstrip("/")
    return env_u or None


_CACHE_TTL_SEC = 300


def _fetch_market_series_impl(
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


@st.cache_data(ttl=_CACHE_TTL_SEC, show_spinner=False)
def _fetch_market_series_cached(
    base: str,
    path: str,
    from_year: int,
    to_year: int,
    mode: str,
) -> dict[str, Any]:
    """Un endpoint de mercado; cacheado por base + rango + modo."""
    return _fetch_market_series_impl(base, path, from_year, to_year, mode)


def _http_get_json(base: str, path: str, params: dict[str, Any] | None, timeout: int) -> dict[str, Any]:
    r = requests.get(f"{base}{path}", params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()


@st.cache_data(
    ttl=_CACHE_TTL_SEC,
    show_spinner="Cargando datos de mercado (precarga en paralelo)…",
)
def _mercado_bundle_cached(
    base: str,
    m_from: int,
    m_to: int,
    m_mode: str,
) -> dict[str, Any]:
    """Precarga en paralelo todas las series usadas en las pestañas de mercado (misma clave de caché)."""
    params = {"from_year": int(m_from), "to_year": int(m_to), "mode": str(m_mode)}
    tasks: list[tuple[str, str, dict[str, Any] | None, int]] = [
        ("la_resumen", "/api/v1/market/la-fe/resumen-series", params, 90),
        ("tot_resumen", "/api/v1/market/resumen/totals-series", params, 90),
        ("la_ext", "/api/v1/market/la-fe/resumen-extended", params, 90),
        ("tot_ext", "/api/v1/market/resumen/totals-extended", params, 90),
        ("la_cuadro", "/api/v1/market/la-fe/cuadro-series", params, 90),
        ("tot_cuadro", "/api/v1/market/cuadro/totals-series", params, 90),
        ("snapshot", "/api/v1/market/la-fe/snapshot-latest", {}, 60),
    ]
    out: dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=7) as ex:
        future_map = {
            ex.submit(_http_get_json, base, path, par, timeout): key
            for key, path, par, timeout in tasks
        }
        for fut in as_completed(future_map):
            key = future_map[fut]
            try:
                out[key] = fut.result()
            except Exception as e:
                out[key] = e
    return out


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


def _df_market_points(payload: dict[str, Any]) -> pd.DataFrame:
    pts = payload.get("points") or []
    if not pts:
        return pd.DataFrame()
    df = pd.DataFrame(pts)
    if df.empty:
        return df
    df["periodo"] = (
        df["period_year"].astype(int).astype(str)
        + "-"
        + df["period_month"].astype(int).astype(str).str.zfill(2)
    )
    return df


_RESUMEN_METRIC_LABELS: dict[str, str] = {
    "primas_netas_thousands_bs": "Primas netas",
    "siniestros_pagados_thousands_bs": "Siniestros pagados",
    "reservas_psp_brutas_thousands_bs": "Reservas PSP brutas",
    "reservas_psp_netas_reaseg_thousands_bs": "Reservas PSP netas reaseg.",
    "siniestros_totales_thousands_bs": "Siniestros totales",
    "comisiones_thousands_bs": "Comisiones",
    "gastos_adquisicion_thousands_bs": "Gastos adquisición",
    "gastos_administracion_thousands_bs": "Gastos administración",
    "loss_ratio_proxy": "Ratio siniestros/primas",
    "comision_ratio_proxy": "Ratio comisiones/primas",
    "gasto_adm_ratio_proxy": "Ratio gasto adm./primas",
}

_CUADRO_METRIC_LABELS: dict[str, str] = {
    "primas_netas_thousands_bs": "Primas (cuadro)",
    "resultado_tecnico_bruto_thousands_bs": "Resultado técnico bruto",
    "resultado_reaseguro_cedido_thousands_bs": "Resultado reaseguro cedido",
    "resultado_tecnico_neto_thousands_bs": "Resultado técnico neto",
    "resultado_gestion_general_thousands_bs": "Resultado gestión general",
    "saldo_operaciones_thousands_bs": "Saldo operaciones",
}


def _fetch_kpi_impl(
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


@st.cache_data(ttl=_CACHE_TTL_SEC, show_spinner=False)
def _fetch_kpi_cached(
    base: str,
    cohort_year: int,
    seed: int,
    n_policies: int,
    use_db: bool,
) -> dict[str, Any]:
    return _fetch_kpi_impl(base, cohort_year, seed, n_policies, use_db)


@st.cache_data(ttl=_CACHE_TTL_SEC, show_spinner=False)
def _fetch_snapshot_cached(base: str) -> dict[str, Any]:
    return _http_get_json(base, "/api/v1/market/la-fe/snapshot-latest", {}, 60)


# —— Cabecera: logo al lado del título (misma fila) ——
if _LOGO_FE1.is_file():
    _col_logo, _col_title = st.columns([1.15, 4.5], gap="small")
    with _col_logo:
        st.image(str(_LOGO_FE1), width=132, use_container_width=False)
    with _col_title:
        st.markdown(
            f'<p style="font-size:1.42rem;font-weight:700;color:{_BRAND_DEEP};margin:0.55rem 0 0.15rem 0;line-height:1.2;">'
            "Insurance Intelligence Hub</p>",
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        f'<p style="font-size:1.42rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.85rem 0;">'
        "Insurance Intelligence Hub</p>",
        unsafe_allow_html=True,
    )

base = _api_base()
upload_path = _admin_upload_hint()
upload_claims_path = _admin_upload_claims_hint()
portal = _portal_reflex_url()

# Respaldos fijos si la API no tiene datos en BD (no se exponen en la UI).
_KPI_SEED_FALLBACK = 42
_KPI_N_POLICIES_FALLBACK = 8000

_COHORT_YEAR_OPTIONS = list(range(2025, 2022, -1))  # 2025 → 2023 (reciente primero)
_MARKET_YEAR_MIN = 2023
_MARKET_YEAR_MAX = 2025

_PILL_AMBITO = ("Cartera", "Mercado SUDEASEG")
_VISTA_PILL_LABELS = (
    "Resumen + tacómetros",
    "Analítica avanzada",
    "Mapa Venezuela (demo)",
)
_VISTA_PILL_TO_KEY: dict[str, str] = {
    "Resumen + tacómetros": "resumen",
    "Analítica avanzada": "analitica",
    "Mapa Venezuela (demo)": "territorio",
}

with st.sidebar:
    with st.container(border=True):
        st.caption("PASO 1 · ÁMBITO")
        _amb = st.pills(
            "Ámbito de trabajo",
            options=list(_PILL_AMBITO),
            selection_mode="single",
            default=_PILL_AMBITO[0],
            label_visibility="collapsed",
            key="pill_ambito",
        ) or _PILL_AMBITO[0]
        lab_module = "cohorte" if _amb == "Cartera" else "mercado"
        st.caption("Cartera: KPIs y cartera por año. Mercado: series SUDEASEG (2023–2025).")

    st.divider()

    if lab_module == "cohorte":
        with st.container(border=True):
            st.caption("PASO 2 · COHORTE")
            cohort_year = st.selectbox(
                "Año de la cohorte",
                options=_COHORT_YEAR_OPTIONS,
                index=0,
                help="Del más reciente al más antiguo. Mínimo 2023.",
            )
        with st.container(border=True):
            st.caption("PASO 3 · VISTA (pantalla completa)")
            _vista = (
                st.pills(
                    "Sección de cartera",
                    options=list(_VISTA_PILL_LABELS),
                    selection_mode="single",
                    default=_VISTA_PILL_LABELS[0],
                    label_visibility="collapsed",
                    key="pill_vista_cartera",
                )
                or _VISTA_PILL_LABELS[0]
            )
            cohorte_seccion = _VISTA_PILL_TO_KEY.get(_vista, "resumen")
            st.caption("Cada opción abre una vista distinta del mismo año.")
        m_from = _MARKET_YEAR_MIN
        m_to = _MARKET_YEAR_MAX
        m_mode = "monthly_flow"
    else:
        cohort_year = _COHORT_YEAR_OPTIONS[0]
        cohorte_seccion = "resumen"
        with st.container(border=True):
            st.caption("PASO 2 · PERÍODO DE SERIES")
            st.caption("Ventana 2023–2025 · sin años futuros.")
            _m_years = list(range(_MARKET_YEAR_MIN, _MARKET_YEAR_MAX + 1))
            m_from = st.selectbox("Desde año", options=_m_years, index=0, key="sb_m_from")
            _m_to_allowed = [y for y in _m_years if y >= m_from]
            m_to = st.selectbox(
                "Hasta año",
                options=_m_to_allowed,
                index=len(_m_to_allowed) - 1,
                key="sb_m_to",
            )
            m_mode = st.selectbox(
                "Modo temporal",
                options=["monthly_flow", "ytd"],
                format_func=lambda x: "Flujo mensual" if x == "monthly_flow" else "YTD (cierre de mes)",
                key="sb_m_mode",
            )
        with st.container(border=True):
            st.caption("PASO 3 · CARGA DE DATOS")
            precarga_paralela = st.checkbox(
                "Precarga paralela (todas las series)",
                value=True,
                help="Una sola ronda en paralelo + caché. Desactive si la API limita concurrencia.",
                key="sb_mercado_prefetch",
            )

if lab_module == "cohorte":
    data: dict[str, Any] | None = None
    try:
        data = _fetch_kpi_cached(
            base,
            cohort_year,
            _KPI_SEED_FALLBACK,
            _KPI_N_POLICIES_FALLBACK,
            True,
        )
    except Exception as e:
        st.error(f"No se pudo obtener los indicadores. Comprueba la conexión o inténtalo más tarde. ({e})")
        st.stop()
    if data is None:
        st.stop()

    port_pack = fetch_cohort_portfolio(base, cohort_year)

    with st.sidebar:
        st.divider()
        with st.container(border=True):
            st.caption("CONTEXTO Y NOTAS")
            with st.expander("Notas técnicas y operativas", expanded=False):
                st.caption(
                    "KPI desde API compute (DuckDB + Postgres). Si no hay filas en BD para el año, "
                    "la API usa cartera sintética de respaldo."
                )
                if data.get("data_note"):
                    st.markdown(data["data_note"])

    if cohorte_seccion == "resumen":
        with st.container(border=True):
            st.markdown(
                f'<p style="font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.25rem 0;">'
                "Resumen de cartera</p>",
                unsafe_allow_html=True,
            )
            st.caption(
                "Métricas clave y tacómetros compactos. Cambie la vista en la barra lateral (paso 3) para otras pantallas."
            )
        st.divider()
        with st.container(border=True):
            st.subheader("Indicadores clave")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Persistencia", f"{data['persistency_rate_pct']:.2f} %")
            c2.metric("Pólizas activas", f"{data['policies_active']:,}")
            c3.metric("Lapsos", f"{data['policies_lapsed']:,}")
            c4.metric("Prima media anual", f"{data['avg_annual_premium']:,.2f}")
        st.divider()
        with st.container(border=True):
            st.subheader("Tacómetros (vista compacta)")
            fig_g = render_resumen_gauges(
                data,
                port_pack,
                brand_purple=_BRAND_PURPLE,
            )
            st.plotly_chart(fig_g, use_container_width=True)
        st.divider()
        with st.container(border=True):
            st.subheader("Exportación")
            ex1, ex2 = st.columns(2)
            with ex1:
                df = pd.DataFrame([data])
                st.download_button(
                    "Descargar KPIs (CSV)",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="kpi_summary_demo.csv",
                    mime="text/csv",
                )
            with ex2:
                if port_pack:
                    st.download_button(
                        "Descargar paquete analítico (JSON)",
                        data=json.dumps(port_pack, indent=2, ensure_ascii=False).encode("utf-8"),
                        file_name=f"cohort_portfolio_{cohort_year}.json",
                        mime="application/json",
                    )

    elif cohorte_seccion == "analitica":
        with st.container(border=True):
            st.markdown(
                f'<p style="font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.25rem 0;">'
                "Analítica avanzada</p>",
                unsafe_allow_html=True,
            )
            st.caption("Gráficos y tablas detalladas del paquete de cartera para el año elegido.")
        st.divider()
        if port_pack is None:
            st.warning(
                "No hay datos de cartera en base para este año (404 en `/api/v1/kpi/cohort-portfolio`). "
                "Cargue pólizas/siniestros o ejecute `seed_operational_aligned.py`."
            )
        else:
            with st.container(border=True):
                render_portfolio_pack(
                    port_pack,
                    brand_purple=_BRAND_PURPLE,
                    brand_deep=_BRAND_DEEP,
                    accent_blue=_MARKET_TOTAL_LINE,
                )
        st.divider()
        with st.container(border=True):
            st.subheader("Exportación")
            ex1, ex2 = st.columns(2)
            with ex1:
                st.download_button(
                    "Descargar KPIs (CSV)",
                    data=pd.DataFrame([data]).to_csv(index=False).encode("utf-8"),
                    file_name="kpi_summary_demo.csv",
                    mime="text/csv",
                    key="dl_kpi_analitica",
                )
            with ex2:
                if port_pack:
                    st.download_button(
                        "Descargar paquete analítico (JSON)",
                        data=json.dumps(port_pack, indent=2, ensure_ascii=False).encode("utf-8"),
                        file_name=f"cohort_portfolio_{cohort_year}.json",
                        mime="application/json",
                        key="dl_port_analitica",
                    )

    else:
        with st.container(border=True):
            st.markdown(
                f'<p style="font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.25rem 0;">'
                "Territorio Venezuela (demo)</p>",
                unsafe_allow_html=True,
            )
            st.caption(
                "Cada póliza se asigna a un estado con función hash determinista (solo para visualización; no es ubicación real)."
            )
        st.divider()
        if port_pack is None:
            st.warning("Sin datos de cartera en base para este año.")
        else:
            with st.container(border=True):
                render_territorio_ve(port_pack, brand_purple=_BRAND_PURPLE)
            st.divider()
            with st.container(border=True):
                st.subheader("Exportación")
                st.download_button(
                    "Descargar paquete analítico (JSON)",
                    data=json.dumps(port_pack, indent=2, ensure_ascii=False).encode("utf-8"),
                    file_name=f"cohort_portfolio_{cohort_year}.json",
                    mime="application/json",
                    key="dl_port_mapa",
                )

else:
    with st.container(border=True):
        st.markdown(
            f'<p style="font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.25rem 0;">'
            "Mercado SUDEASEG</p>",
            unsafe_allow_html=True,
        )
        st.caption(
            "SUDEASEG vía API compute (Postgres). Miles de bolívares salvo ratios. "
            "Ajuste período en la barra lateral (pasos 2–3); use las secciones inferiores para cada bloque de análisis."
        )
    st.divider()

    if m_from > m_to:
        st.warning("Ajusta el rango de años (desde ≤ hasta).")
    else:
        mb = _mercado_bundle_cached(base, int(m_from), int(m_to), str(m_mode)) if precarga_paralela else None

        st.caption(
            "**Secciones mercado:** solo se dibuja la elegida (misma lógica que analítica de cartera)."
        )
        st.markdown(_MERCADO_PILLS_CSS, unsafe_allow_html=True)
        mercado_sec = (
            st.pills(
                "Sección mercado",
                options=list(_MERCADO_SECTION_LABELS),
                selection_mode="single",
                default=_MERCADO_SECTION_LABELS[0],
                label_visibility="collapsed",
                key="mercado_section_pills",
            )
            or _MERCADO_SECTION_LABELS[0]
        )
        _mcol = _MERCADO_SECTION_COLORS.get(mercado_sec, "#64748b")
        st.markdown(
            f'<div style="height:4px;border-radius:4px;background:linear-gradient(90deg,{_mcol},#e2e8f0);margin:0.35rem 0 0.5rem 0;"></div>',
            unsafe_allow_html=True,
        )
        _analitica_section_banner(
            mercado_sec,
            _mcol,
            _MERCADO_SECTION_SUB.get(mercado_sec, ""),
        )

        if mercado_sec == "Primas vs mercado":
            st.divider()
            la_payload: dict[str, Any] | None = None
            tot_payload: dict[str, Any] | None = None
            err_prim: Exception | None = None
            if mb is not None:
                _la = mb.get("la_resumen")
                _tot = mb.get("tot_resumen")
                if isinstance(_la, Exception):
                    err_prim = _la
                elif isinstance(_tot, Exception):
                    err_prim = _tot
                else:
                    la_payload = _la
                    tot_payload = _tot
            else:
                try:
                    la_payload = _fetch_market_series_cached(
                        base,
                        "/api/v1/market/la-fe/resumen-series",
                        int(m_from),
                        int(m_to),
                        str(m_mode),
                    )
                    tot_payload = _fetch_market_series_cached(
                        base,
                        "/api/v1/market/resumen/totals-series",
                        int(m_from),
                        int(m_to),
                        str(m_mode),
                    )
                except Exception as e:
                    err_prim = e
            if err_prim is not None:
                st.error(
                    "No se pudieron obtener las series de mercado. "
                    "Comprueba DATABASE_URL y migraciones SUDEASEG. "
                    f"({err_prim})"
                )
            elif la_payload is not None and tot_payload is not None:
                merged = _merge_market_primas(la_payload, tot_payload)
                if merged.empty:
                    st.info("No hay puntos en el rango elegido o faltan datos en la tabla de mercado.")
                else:
                    fig_m = make_subplots(specs=[[{"secondary_y": True}]])
                    fig_m.add_trace(
                        go.Scatter(
                            x=merged["periodo"],
                            y=merged["primas_la_fe_thousands_bs"],
                            name="La Fe (eje izq.)",
                            mode="lines+markers",
                            line={"color": _BRAND_PURPLE},
                        ),
                        secondary_y=False,
                    )
                    fig_m.add_trace(
                        go.Scatter(
                            x=merged["periodo"],
                            y=merged["primas_mercado_thousands_bs"],
                            name="Mercado total (eje der.)",
                            mode="lines+markers",
                            line={"color": _MARKET_TOTAL_LINE},
                        ),
                        secondary_y=True,
                    )
                    fig_m.update_xaxes(title_text="Período (año-mes)")
                    fig_m.update_yaxes(title_text="La Fe · miles de Bs.", secondary_y=False)
                    fig_m.update_yaxes(title_text="Mercado total · miles de Bs.", secondary_y=True)
                    fig_m.update_layout(
                        height=420,
                        margin=dict(l=24, r=56, t=48, b=24),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        hovermode="x unified",
                    )
                    st.plotly_chart(fig_m, use_container_width=True)
                    st.dataframe(merged, use_container_width=True, hide_index=True)
                    st.download_button(
                        "Descargar tabla fusionada (CSV)",
                        data=merged.to_csv(index=False).encode("utf-8"),
                        file_name="market_la_fe_vs_totales.csv",
                        mime="text/csv",
                    )
                    with st.expander("Notas de filtro (API)"):
                        st.write(la_payload.get("empresa_filter_note", ""))
                        st.write(tot_payload.get("empresa_filter_note", ""))

        elif mercado_sec == "Último cierre":
            st.divider()
            snap: dict[str, Any] | None = None
            snap_err: Exception | None = None
            if mb is not None:
                _sn = mb.get("snapshot")
                if isinstance(_sn, Exception):
                    snap_err = _sn
                else:
                    snap = _sn
            else:
                try:
                    snap = _fetch_snapshot_cached(base)
                except Exception as e:
                    snap_err = e
            if snap_err is not None:
                st.warning(f"No hay snapshot o la API falló: {snap_err}")
            elif snap is not None:
                py, pm = snap["period_year"], snap["period_month"]
                st.markdown(f"**Cierre:** {py}-{pm:02d} · Miles de Bs. (ratios como fracción)")
                lf = snap.get("la_fe") or {}
                mk = snap.get("mercado_total") or {}
                c1, c2, c3, c4 = st.columns(4)

                def _mnum(x: Any, fmt: str = ",.2f") -> str:
                    if x is None:
                        return "—"
                    return f"{float(x):{fmt}}"

                c1.metric("Primas YTD La Fe", _mnum(lf.get("primas_ytd")))
                c2.metric("Siniestros tot. La Fe", _mnum(lf.get("siniestros_totales_ytd")))
                lr_lf = lf.get("loss_ratio_ytd")
                c3.metric(
                    "Loss ratio La Fe",
                    f"{float(lr_lf) * 100:.2f} %" if lr_lf is not None else "—",
                )
                cq = snap.get("cuota_mercado_primas_pct")
                c4.metric("Cuota primas", f"{float(cq):.3f} %" if cq is not None else "—")
                c5, c6, c7, c8 = st.columns(4)
                c5.metric("Comisiones YTD La Fe", _mnum(lf.get("comisiones_ytd")))
                c6.metric("Gasto adm. YTD La Fe", _mnum(lf.get("gastos_admin_ytd")))
                c7.metric("Primas YTD mercado", _mnum(mk.get("primas_ytd")))
                lr_mk = mk.get("loss_ratio_ytd")
                c8.metric(
                    "Loss ratio mercado",
                    f"{float(lr_mk) * 100:.2f} %" if lr_mk is not None else "—",
                )
                st.caption(snap.get("empresa_filter_note", ""))
                st.download_button(
                    "Descargar snapshot (JSON)",
                    data=json.dumps(snap, indent=2, ensure_ascii=False).encode("utf-8"),
                    file_name="market_la_fe_snapshot_latest.json",
                    mime="application/json",
                )

        elif mercado_sec == "Métricas resumen":
            st.divider()
            la_ext: dict[str, Any] | None = None
            tot_ext: dict[str, Any] | None = None
            err_ext: Exception | None = None
            if mb is not None:
                _a = mb.get("la_ext")
                _b = mb.get("tot_ext")
                if isinstance(_a, Exception):
                    err_ext = _a
                elif isinstance(_b, Exception):
                    err_ext = _b
                else:
                    la_ext = _a
                    tot_ext = _b
            else:
                try:
                    la_ext = _fetch_market_series_cached(
                        base,
                        "/api/v1/market/la-fe/resumen-extended",
                        int(m_from),
                        int(m_to),
                        str(m_mode),
                    )
                    tot_ext = _fetch_market_series_cached(
                        base,
                        "/api/v1/market/resumen/totals-extended",
                        int(m_from),
                        int(m_to),
                        str(m_mode),
                    )
                except Exception as e:
                    err_ext = e
            if err_ext is not None:
                st.error(f"No se pudieron cargar series extendidas: {err_ext}")
            elif la_ext is not None and tot_ext is not None:
                df_lf = _df_market_points(la_ext)
                df_mk = _df_market_points(tot_ext)
                if df_lf.empty:
                    st.info("Sin puntos extendidos en el rango.")
                else:
                    metric_keys = list(_RESUMEN_METRIC_LABELS.keys())
                    picked = st.multiselect(
                        "Métricas a graficar (La Fe)",
                        options=metric_keys,
                        default=["primas_netas_thousands_bs", "siniestros_totales_thousands_bs", "loss_ratio_proxy"],
                        format_func=lambda k: _RESUMEN_METRIC_LABELS.get(k, k),
                    )
                    fig_e = go.Figure()
                    for k in picked:
                        if k in df_lf.columns:
                            fig_e.add_trace(
                                go.Scatter(
                                    x=df_lf["periodo"],
                                    y=df_lf[k],
                                    name=_RESUMEN_METRIC_LABELS.get(k, k),
                                    mode="lines+markers",
                                )
                            )
                    fig_e.update_layout(
                        height=440,
                        xaxis_title="Período",
                        legend=dict(orientation="h", y=1.1),
                        hovermode="x unified",
                    )
                    st.plotly_chart(fig_e, use_container_width=True)
                    compare = st.selectbox(
                        "Superponer total mercado (misma métrica)",
                        options=["(ninguna)"] + metric_keys,
                        format_func=lambda k: "(ninguna)" if k == "(ninguna)" else _RESUMEN_METRIC_LABELS.get(k, k),
                    )
                    if compare != "(ninguna)" and not df_mk.empty and compare in df_mk.columns:
                        fig_c = go.Figure()
                        fig_c.add_trace(
                            go.Scatter(
                                x=df_lf["periodo"],
                                y=df_lf[compare],
                                name=f"La Fe — {_RESUMEN_METRIC_LABELS.get(compare, compare)}",
                                mode="lines+markers",
                                line={"color": _BRAND_PURPLE},
                            )
                        )
                        fig_c.add_trace(
                            go.Scatter(
                                x=df_mk["periodo"],
                                y=df_mk[compare],
                                name=f"Mercado — {_RESUMEN_METRIC_LABELS.get(compare, compare)}",
                                mode="lines+markers",
                                line={"color": _MARKET_TOTAL_LINE},
                            )
                        )
                        fig_c.update_layout(height=380, hovermode="x unified")
                        st.plotly_chart(fig_c, use_container_width=True)
                    st.subheader("Tablas y CSV")
                    cta, ctb = st.columns(2)
                    with cta:
                        st.markdown("**La Fe**")
                        st.dataframe(df_lf, use_container_width=True, hide_index=True)
                        st.download_button(
                            "CSV La Fe (extendido)",
                            df_lf.to_csv(index=False).encode("utf-8"),
                            "market_la_fe_resumen_extended.csv",
                            mime="text/csv",
                            key="dl_lf_ext",
                        )
                    with ctb:
                        st.markdown("**Mercado (suma)**")
                        st.dataframe(df_mk, use_container_width=True, hide_index=True)
                        st.download_button(
                            "CSV mercado (extendido)",
                            df_mk.to_csv(index=False).encode("utf-8"),
                            "market_totals_resumen_extended.csv",
                            mime="text/csv",
                            key="dl_mk_ext",
                        )

        elif mercado_sec == "Cuadro de resultados":
            st.divider()
            la_c: dict[str, Any] | None = None
            tot_c: dict[str, Any] | None = None
            err_c: Exception | None = None
            if mb is not None:
                _lc = mb.get("la_cuadro")
                _tc = mb.get("tot_cuadro")
                if isinstance(_lc, Exception):
                    err_c = _lc
                elif isinstance(_tc, Exception):
                    err_c = _tc
                else:
                    la_c = _lc
                    tot_c = _tc
            else:
                try:
                    la_c = _fetch_market_series_cached(
                        base,
                        "/api/v1/market/la-fe/cuadro-series",
                        int(m_from),
                        int(m_to),
                        str(m_mode),
                    )
                    tot_c = _fetch_market_series_cached(
                        base,
                        "/api/v1/market/cuadro/totals-series",
                        int(m_from),
                        int(m_to),
                        str(m_mode),
                    )
                except Exception as e:
                    err_c = e
            if err_c is not None:
                st.error(f"No se pudieron cargar series de cuadro: {err_c}")
            elif la_c is not None and tot_c is not None:
                df_lfc = _df_market_points(la_c)
                df_ttc = _df_market_points(tot_c)
                if df_lfc.empty:
                    st.info("Sin datos de cuadro para La Fe en el rango (¿ETL cuadro cargado?).")
                else:
                    cuad_pick = st.multiselect(
                        "Líneas (La Fe)",
                        options=list(_CUADRO_METRIC_LABELS.keys()),
                        default=["resultado_tecnico_neto_thousands_bs", "saldo_operaciones_thousands_bs"],
                        format_func=lambda k: _CUADRO_METRIC_LABELS.get(k, k),
                    )
                    fig_c2 = go.Figure()
                    for k in cuad_pick:
                        if k in df_lfc.columns:
                            fig_c2.add_trace(
                                go.Scatter(
                                    x=df_lfc["periodo"],
                                    y=df_lfc[k],
                                    name=_CUADRO_METRIC_LABELS.get(k, k),
                                    mode="lines+markers",
                                )
                            )
                    fig_c2.update_layout(height=440, hovermode="x unified")
                    st.plotly_chart(fig_c2, use_container_width=True)
                    st.dataframe(df_lfc, use_container_width=True, hide_index=True)
                    st.download_button(
                        "CSV cuadro La Fe",
                        df_lfc.to_csv(index=False).encode("utf-8"),
                        "market_la_fe_cuadro.csv",
                        mime="text/csv",
                        key="dl_cuad_lf",
                    )
                    if not df_ttc.empty:
                        st.dataframe(df_ttc, use_container_width=True, hide_index=True)
                        st.download_button(
                            "CSV cuadro mercado (suma)",
                            df_ttc.to_csv(index=False).encode("utf-8"),
                            "market_cuadro_totals.csv",
                            mime="text/csv",
                            key="dl_cuad_mk",
                        )

with st.sidebar:
    st.divider()
    with st.container(border=True):
        st.caption("ENLACES RÁPIDOS")
        st.link_button(
            "Carga de pólizas (Admin)",
            upload_path,
            use_container_width=True,
            type="primary",
        )
        st.link_button(
            "Carga de siniestros (Admin)",
            upload_claims_path,
            use_container_width=True,
        )
        if portal:
            st.link_button(
                "Portal ejecutivo (Reflex)",
                portal,
                use_container_width=True,
            )
    with st.container(border=True):
        st.caption("MARCA")
        if _LOGO_FE1.is_file():
            st.image(str(_LOGO_FE1), width=132, use_container_width=False)
        st.caption("Seguros La Fe · demo IIH")

st.caption(
    "Seguros La Fe · RIF J-000467382 · SUDEASEG N.º 62 · Insurance Intelligence Hub (demo técnico)."
)
