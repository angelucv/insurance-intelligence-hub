"""PyGWalker: exploración visual tipo BI sobre tablas de cartera y mercado."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def _df_from_list(rows: list | None, *, cohort_year: int | None = None) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if cohort_year is not None:
        df.insert(0, "cohort_year", int(cohort_year))
    return df


def cohort_pack_to_tables(pack: dict[str, Any], cohort_year: int) -> dict[str, pd.DataFrame]:
    """Tablas derivadas del JSON `/api/v1/kpi/cohort-portfolio` para arrastrar dimensiones en PyGWalker."""
    out: dict[str, pd.DataFrame] = {}
    if pack.get("issue_by_month"):
        out["Emisión por mes"] = _df_from_list(pack["issue_by_month"], cohort_year=cohort_year)
    if pack.get("loss_by_month"):
        out["Siniestralidad por mes"] = _df_from_list(pack["loss_by_month"], cohort_year=cohort_year)
    if pack.get("cumulative_paid"):
        out["Pagado acumulado"] = _df_from_list(pack["cumulative_paid"], cohort_year=cohort_year)
    if pack.get("scatter_premium_vs_paid"):
        out["Prima vs pagado (pólizas)"] = _df_from_list(
            pack["scatter_premium_vs_paid"],
            cohort_year=cohort_year,
        )
    if pack.get("top_policies_by_paid"):
        out["Top pólizas por pagado"] = _df_from_list(
            pack["top_policies_by_paid"],
            cohort_year=cohort_year,
        )
    if pack.get("sunburst_age_status"):
        out["Composición edad × estado"] = _df_from_list(
            pack["sunburst_age_status"],
            cohort_year=cohort_year,
        )
    if pack.get("rolling_lr_monthly"):
        out["Burn / ratio mensual"] = _df_from_list(
            pack["rolling_lr_monthly"],
            cohort_year=cohort_year,
        )
    return out


def mercado_bundle_to_tables(
    mb: dict[str, Any] | None,
    merged_primas: pd.DataFrame | None,
    *,
    m_from: int,
    m_to: int,
) -> dict[str, pd.DataFrame]:
    """Series ya cargadas (bundle o caché) como DataFrames para PyGWalker."""
    out: dict[str, pd.DataFrame] = {}

    if merged_primas is not None and not merged_primas.empty:
        dfm = merged_primas.copy()
        dfm.insert(0, "ventana_desde", m_from)
        dfm.insert(1, "ventana_hasta", m_to)
        out["Primas La Fe vs mercado (fusionado)"] = dfm

    if mb is None:
        return out

    def _add(name: str, payload: Any) -> None:
        if isinstance(payload, Exception) or not isinstance(payload, dict):
            return
        pts = payload.get("points") or []
        if not pts:
            return
        dfp = pd.DataFrame(pts)
        dfp.insert(0, "ventana_desde", m_from)
        dfp.insert(1, "ventana_hasta", m_to)
        out[name] = dfp

    _add("La Fe — resumen", mb.get("la_resumen"))
    _add("Mercado — totales", mb.get("tot_resumen"))
    _add("La Fe — extendido", mb.get("la_ext"))
    _add("Mercado — extendido", mb.get("tot_ext"))
    _add("La Fe — cuadro", mb.get("la_cuadro"))
    _add("Mercado — cuadro", mb.get("tot_cuadro"))

    snap = mb.get("snapshot")
    if not isinstance(snap, Exception) and isinstance(snap, dict) and snap:
        try:
            out["Snapshot último cierre (JSON aplanado)"] = pd.json_normalize(snap)
        except Exception:
            pass

    return out


def _init_pygwalker_streamlit_comm() -> None:
    """PyGWalker en Streamlit suele requerir init una vez por sesión."""
    if st.session_state.get("_pygwalker_comm_ready"):
        return
    try:
        from pygwalker.api.streamlit import init_streamlit_comm

        init_streamlit_comm()
    except Exception:
        pass
    st.session_state["_pygwalker_comm_ready"] = True


def render_pygwalker_streamlit(df: pd.DataFrame, *, key: str) -> None:
    """Embeds PyGWalker en Streamlit; si falla el import, muestra vista tabular."""
    if df is None or df.empty:
        st.info("Sin filas para explorar con PyGWalker.")
        return

    try:
        import pygwalker as pyg
    except ImportError:
        st.warning(
            "PyGWalker no está instalado en este entorno. "
            "Añada `pygwalker` al entorno (p. ej. `pip install pygwalker`). "
            "Python 3.10–3.12 suele ser el más compatible."
        )
        st.dataframe(df.head(2000), use_container_width=True, hide_index=True)
        st.caption(f"Vista previa (primeras filas). Total filas: {len(df):,}.")
        return

    _init_pygwalker_streamlit_comm()
    try:
        with st.spinner("Iniciando lienzo PyGWalker…"):
            try:
                pyg.walk(df, env="Streamlit")
            except TypeError:
                pyg.walk(df, env="streamlit")
    except Exception as e:
        st.error(f"No se pudo iniciar PyGWalker: {e}")
        with st.expander("Detalle técnico"):
            st.exception(e)
        st.dataframe(df.head(500), use_container_width=True, hide_index=True)


def render_table_picker_and_walker(
    tables: dict[str, pd.DataFrame],
    *,
    select_key: str,
    walker_key: str,
) -> None:
    if not tables:
        st.warning("No hay tablas derivadas disponibles para esta vista.")
        return
    names = list(tables.keys())
    pick = st.selectbox(
        "Tabla fuente para explorar",
        options=names,
        index=0,
        key=select_key,
    )
    df = tables.get(pick)
    if df is None:
        df = pd.DataFrame()
    st.caption(
        f"**{pick}** · {len(df):,} filas × {len(df.columns)} columnas. "
        "Arrastre dimensiones y medidas en el lienzo PyGWalker."
    )
    render_pygwalker_streamlit(df, key=walker_key)
