"""Laboratorio: visualización rica (Plotly) + KPIs API; carga solo vía Django Admin."""

from __future__ import annotations

import json
import os
import sys
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
    fetch_cohort_portfolio,
    render_portfolio_pack,
    render_resumen_gauges,
    render_territorio_ve,
)

st.set_page_config(
    page_title="Insurance Intelligence Hub — Laboratorio",
    layout="wide",
    initial_sidebar_state="expanded",
)

_LOGO_FE1 = Path(__file__).resolve().parent / "assets" / "logo-fe-1.jpg"

_BRAND_PURPLE = "#7029B3"
_BRAND_DEEP = "#5a1f94"
_MARKET_TOTAL_LINE = "#0284c7"


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


# —— Cabecera: logo tamaño moderado + título ——
_h_left, _h_mid, _h_right = st.columns([2.2, 1.35, 2.2])
with _h_mid:
    if _LOGO_FE1.is_file():
        st.image(str(_LOGO_FE1), use_container_width=True)
    else:
        st.markdown("### Insurance Intelligence Hub")
st.markdown(
    f'<p style="text-align:center;font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0.15rem 0 0.2rem 0;">'
    "Insurance Intelligence Hub</p>"
    '<p style="text-align:center;color:#64748b;font-size:0.92rem;margin:0 0 0.85rem 0;">Laboratorio · visualización</p>',
    unsafe_allow_html=True,
)

base = _api_base()
upload_path = _admin_upload_hint()
upload_claims_path = _admin_upload_claims_hint()
portal = _portal_reflex_url()

# Respaldos fijos si la API no tiene datos en BD (no se exponen en la UI).
_KPI_SEED_FALLBACK = 42
_KPI_N_POLICIES_FALLBACK = 8000

with st.sidebar:
    st.markdown("### Vista")
    lab_module = st.radio(
        "Seleccione",
        options=["cohorte", "mercado"],
        format_func=lambda x: "Cartera (KPIs)" if x == "cohorte" else "Mercado SUDEASEG",
        horizontal=False,
        label_visibility="collapsed",
    )
    st.caption("Cartera: datos en Supabase por año. Mercado: series SUDEASEG.")
    st.divider()
    if lab_module == "cohorte":
        cohort_year = st.slider("Año de la cohorte", 2019, 2026, 2022)
        st.markdown("**Sección cartera**")
        cohorte_seccion = st.radio(
            "Navegación",
            options=["resumen", "analitica", "territorio"],
            format_func=lambda x: {
                "resumen": "Resumen + tacómetros",
                "analitica": "Analítica avanzada",
                "territorio": "Mapa Venezuela (demo)",
            }[x],
            label_visibility="collapsed",
        )
        m_from = m_to = 2023
        m_mode = "monthly_flow"
        mercado_vista = "primas"
    else:
        cohort_year = 2022
        cohorte_seccion = "resumen"
        st.markdown("**Series de mercado**")
        m_from = st.number_input("Desde año", min_value=2000, max_value=2100, value=2023, step=1, key="sb_m_from")
        m_to = st.number_input("Hasta año", min_value=2000, max_value=2100, value=2026, step=1, key="sb_m_to")
        m_mode = st.selectbox(
            "Modo temporal",
            options=["monthly_flow", "ytd"],
            format_func=lambda x: "Flujo mensual" if x == "monthly_flow" else "YTD (cierre de mes)",
            key="sb_m_mode",
        )
        st.divider()
        st.markdown("**Vista del mercado**")
        mercado_vista = st.radio(
            "Contenido principal",
            options=["primas", "snapshot", "extendido", "cuadro"],
            format_func=lambda x: {
                "primas": "Primas vs mercado",
                "snapshot": "Último cierre",
                "extendido": "Métricas resumen",
                "cuadro": "Cuadro de resultados",
            }[x],
        )

if lab_module == "cohorte":
    data: dict[str, Any] | None = None
    try:
        data = _fetch_kpi(
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
        st.markdown("**Notas y contexto**")
        with st.expander("Ver notas técnicas y operativas", expanded=False):
            st.caption(
                "KPI desde API compute (DuckDB + Postgres). Si no hay filas en BD para el año, "
                "la API usa cartera sintética de respaldo."
            )
            if data.get("data_note"):
                st.markdown(data["data_note"])

    if cohorte_seccion == "resumen":
        st.markdown(
            f'<p style="font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.25rem 0;">'
            "Resumen de cartera</p>",
            unsafe_allow_html=True,
        )
        st.caption("Métricas clave y tacómetros compactos. Use la barra lateral para analítica avanzada o el mapa.")

        st.subheader("Indicadores clave")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Persistencia", f"{data['persistency_rate_pct']:.2f} %")
        c2.metric("Pólizas activas", f"{data['policies_active']:,}")
        c3.metric("Lapsos", f"{data['policies_lapsed']:,}")
        c4.metric("Prima media anual", f"{data['avg_annual_premium']:,.2f}")

        st.subheader("Tacómetros (vista compacta)")
        fig_g = render_resumen_gauges(
            data,
            port_pack,
            brand_purple=_BRAND_PURPLE,
        )
        st.plotly_chart(fig_g, use_container_width=True)

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
        st.markdown(
            f'<p style="font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.25rem 0;">'
            "Analítica avanzada</p>",
            unsafe_allow_html=True,
        )
        if port_pack is None:
            st.warning(
                "No hay datos de cartera en base para este año (404 en `/api/v1/kpi/cohort-portfolio`). "
                "Cargue pólizas/siniestros o ejecute `seed_operational_aligned.py`."
            )
        else:
            render_portfolio_pack(
                port_pack,
                brand_purple=_BRAND_PURPLE,
                brand_deep=_BRAND_DEEP,
                accent_blue=_MARKET_TOTAL_LINE,
            )
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
        st.markdown(
            f'<p style="font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.25rem 0;">'
            "Territorio Venezuela (demo)</p>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Cada póliza se asigna a un estado con función hash determinista (solo para visualización; no es ubicación real)."
        )
        if port_pack is None:
            st.warning("Sin datos de cartera en base para este año.")
        else:
            render_territorio_ve(port_pack, brand_purple=_BRAND_PURPLE)
            st.download_button(
                "Descargar paquete analítico (JSON)",
                data=json.dumps(port_pack, indent=2, ensure_ascii=False).encode("utf-8"),
                file_name=f"cohort_portfolio_{cohort_year}.json",
                mime="application/json",
                key="dl_port_mapa",
            )

else:
    st.markdown(
        f'<p style="font-size:1.35rem;font-weight:700;color:{_BRAND_DEEP};margin:0 0 0.25rem 0;">'
        "Mercado SUDEASEG</p>",
        unsafe_allow_html=True,
    )
    st.caption(
        "SUDEASEG en Postgres (API compute). Miles de bolívares salvo ratios. "
        "Modo mensual = flujo del mes; YTD = acumulado a cierre de mes. "
        "Ajusta rango y modo en la barra lateral; elige la vista abajo en el mismo menú."
    )

    if m_from > m_to:
        st.warning("Ajusta el rango de años (desde ≤ hasta).")
    elif mercado_vista == "primas":
            st.subheader("Primas netas: La Fe vs total de mercado")
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
                    "Comprueba DATABASE_URL y migraciones SUDEASEG. "
                    f"({e})"
                )
            else:
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

    elif mercado_vista == "snapshot":
            st.subheader("Último cierre con dato La Fe (YTD a ese mes)")
            try:
                snap_r = requests.get(f"{base}/api/v1/market/la-fe/snapshot-latest", timeout=60)
                snap_r.raise_for_status()
                snap = snap_r.json()
            except Exception as e:
                st.warning(f"No hay snapshot o la API falló: {e}")
            else:
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

    elif mercado_vista == "extendido":
            st.subheader("Serie extendida — resumen por empresa (La Fe)")
            try:
                la_ext = _fetch_market_series(
                    base,
                    "/api/v1/market/la-fe/resumen-extended",
                    int(m_from),
                    int(m_to),
                    str(m_mode),
                )
                tot_ext = _fetch_market_series(
                    base,
                    "/api/v1/market/resumen/totals-extended",
                    int(m_from),
                    int(m_to),
                    str(m_mode),
                )
            except Exception as e:
                st.error(f"No se pudieron cargar series extendidas: {e}")
            else:
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

    elif mercado_vista == "cuadro":
            st.subheader("Cuadro de resultados — La Fe vs total mercado")
            try:
                la_c = _fetch_market_series(
                    base,
                    "/api/v1/market/la-fe/cuadro-series",
                    int(m_from),
                    int(m_to),
                    str(m_mode),
                )
                tot_c = _fetch_market_series(
                    base,
                    "/api/v1/market/cuadro/totals-series",
                    int(m_from),
                    int(m_to),
                    str(m_mode),
                )
            except Exception as e:
                st.error(f"No se pudieron cargar series de cuadro: {e}")
            else:
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
    st.markdown("---")
    st.caption("Enlaces rápidos")
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
    st.markdown("")
    if _LOGO_FE1.is_file():
        st.image(str(_LOGO_FE1), width=108)
    st.caption("Seguros La Fe · demo IIH")

st.caption(
    "Seguros La Fe · RIF J-000467382 · SUDEASEG N.º 62 · Insurance Intelligence Hub (demo técnico)."
)
