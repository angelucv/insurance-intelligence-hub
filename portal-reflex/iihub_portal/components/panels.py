"""Paneles Mercado y Cartera — tarjetas redondeadas estilo dashboard CRM."""

import reflex as rx

from iihub_portal import copy
from iihub_portal.state import State
from iihub_portal.theme import BRAND_DEEP, BRAND_PURPLE


def plotly_chart_wrap(figure: rx.Var) -> rx.Component:
    """Contenedor ancho completo + scroll suave si Plotly aún desborda en móvil."""
    return rx.el.div(
        rx.plotly(data=figure),
        class_name=(
            "w-full min-w-0 max-w-full overflow-x-auto overscroll-x-contain "
            "[scrollbar-width:thin] -mx-0.5 px-0.5 sm:mx-0 sm:px-0"
        ),
    )


def snap_hero_cell(label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-[10px] font-semibold text-white/75 uppercase tracking-wide"),
        rx.el.p(value, class_name="text-base sm:text-lg font-bold text-white mt-0.5 tabular-nums"),
        class_name="rounded-lg px-3 py-2 bg-white/10 border border-white/20 backdrop-blur-md",
    )


def portfolio_chart_card(
    title: str,
    subtitle: str,
    figure: rx.Var,
    *,
    compact: bool = False,
) -> rx.Component:
    pad = "p-3 sm:p-4" if compact else "p-4 sm:p-5"
    sub_cls = "text-[10px] text-gray-500 mt-0.5 mb-2 leading-snug" if compact else "text-xs text-gray-500 mt-0.5 mb-3 leading-relaxed"
    return rx.el.div(
        rx.el.h4(title, class_name="text-xs font-semibold text-gray-900"),
        rx.el.p(subtitle, class_name=sub_cls),
        plotly_chart_wrap(figure),
        class_name=f"rounded-2xl border border-gray-100 bg-white shadow-sm min-w-0 {pad}",
    )


def metric_strip_cell(label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-[11px] font-semibold text-gray-500 uppercase tracking-wide"),
        rx.el.p(value, class_name="text-lg font-bold text-gray-900 mt-1 tabular-nums"),
        class_name="rounded-xl bg-gradient-to-br from-gray-50 to-white px-4 py-3 border border-gray-100/80 shadow-sm",
    )


def mercado_panel() -> rx.Component:
    snap_grid = rx.el.div(
        snap_hero_cell("Período", State.snap_period),
        snap_hero_cell("Primas YTD La Fe", State.snap_primas),
        snap_hero_cell("Loss ratio La Fe", State.snap_lr),
        snap_hero_cell("Cuota primas", State.snap_cuota),
        class_name="grid grid-cols-2 lg:grid-cols-4 gap-2 w-full",
    )
    snap_more = rx.el.div(
        snap_hero_cell("Siniestros tot. La Fe", State.snap_sini),
        snap_hero_cell("Comisiones YTD", State.snap_comisiones),
        snap_hero_cell("Gasto adm. YTD", State.snap_gadm),
        snap_hero_cell("Loss ratio mercado", State.snap_mk_lr),
        class_name="grid grid-cols-2 lg:grid-cols-4 gap-2 w-full mt-3",
    )
    chart_busy = rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Cargando…", size="2", color="gray"),
            spacing="2",
            align_items="center",
        ),
        width="100%",
        padding_y="8",
    )
    return rx.el.div(
        rx.el.section(
            rx.el.div(
                rx.el.h2(
                    copy.MERCADO_SNAPSHOT_TITLE,
                    class_name="text-base font-semibold text-white",
                ),
                rx.el.p(
                    copy.MERCADO_SNAPSHOT_HINT,
                    class_name="text-[10px] text-white/70 mt-0.5",
                ),
                rx.cond(
                    State.mercado_loading,
                    rx.el.p(copy.MERCADO_SNAPSHOT_LOADING, class_name="text-white/90 text-xs mt-3"),
                    rx.cond(
                        State.snap_ok,
                        snap_grid,
                        rx.el.p("Sin snapshot.", class_name="text-white/90 text-xs mt-3"),
                    ),
                ),
                rx.button(
                    rx.cond(State.show_snap_more, "Menos", "Más"),
                    on_click=State.toggle_snap_more,
                    variant="outline",
                    size="1",
                    class_name="mt-3 text-white border-white/35 hover:bg-white/10 text-xs",
                ),
                rx.cond(
                    State.show_snap_more,
                    rx.cond(State.snap_ok, snap_more),
                ),
                class_name="p-4 sm:p-5",
            ),
            class_name="rounded-2xl overflow-hidden shadow-lg shadow-violet-900/15 border border-violet-500/20",
            style={
                "background": f"linear-gradient(135deg, {BRAND_DEEP} 0%, {BRAND_PURPLE} 48%, #4c1d95 100%)",
            },
        ),
        rx.el.section(
            rx.el.div(
                rx.el.h3(
                    copy.MERCADO_PARAMS_TITLE,
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    copy.MERCADO_PARAMS_BODY,
                    class_name="text-xs text-gray-500 mt-0.5 mb-3",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Desde", size="1", color="gray"),
                        rx.select(
                            copy.MERCADO_YEAR_OPTIONS,
                            value=State.market_fy,
                            on_change=State.set_market_fy,
                            size="2",
                            width="88px",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text("Hasta", size="1", color="gray"),
                        rx.select(
                            copy.MERCADO_YEAR_OPTIONS,
                            value=State.market_ty,
                            on_change=State.set_market_ty,
                            size="2",
                            width="88px",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text("Modo", size="1", color="gray"),
                        rx.select(
                            ["monthly_flow", "ytd"],
                            value=State.market_mode,
                            on_change=State.set_market_mode,
                            size="2",
                            width="140px",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text(copy.MERCADO_YOY_A, size="1", color="gray"),
                        rx.select(
                            copy.MERCADO_YEAR_OPTIONS,
                            value=State.market_yoy_a,
                            on_change=State.set_market_yoy_a,
                            size="2",
                            width="88px",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text(copy.MERCADO_YOY_B, size="1", color="gray"),
                        rx.select(
                            copy.MERCADO_YEAR_OPTIONS,
                            value=State.market_yoy_b,
                            on_change=State.set_market_yoy_b,
                            size="2",
                            width="88px",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.button(
                        "Actualizar",
                        on_click=State.load_sudeaseg_preview,
                        loading=State.market_charts_busy,
                        color_scheme="purple",
                        size="2",
                        class_name="rounded-lg",
                        style={"align_self": "flex-end"},
                    ),
                    spacing="3",
                    align_items="end",
                    flex_wrap="wrap",
                    width="100%",
                ),
                class_name="p-4 sm:p-5",
            ),
            class_name="mt-5 rounded-2xl bg-white border border-gray-100 shadow-sm",
        ),
        rx.el.section(
            rx.el.details(
                rx.el.summary(
                    copy.VISUAL_SUGGESTIONS_TITLE,
                    class_name="cursor-pointer text-xs font-medium text-violet-700 list-none",
                ),
                rx.markdown(copy.VISUAL_SUGGESTIONS_MD),
                class_name="mt-4 p-3 rounded-xl bg-violet-50/60 border border-violet-100 text-sm [&_summary::-webkit-details-marker]:hidden",
            ),
            class_name="mt-4 w-full",
        ),
        rx.el.div(
            rx.el.section(
                rx.el.div(
                    rx.el.h3(
                        copy.MERCADO_CHART_PRIM_TITLE,
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        copy.MERCADO_CHART_PRIM_SUB,
                        class_name="text-[10px] text-gray-500 mt-0.5 mb-2",
                    ),
                    rx.cond(
                        State.market_charts_busy,
                        chart_busy,
                        rx.cond(
                            State.market_plot_ok,
                            plotly_chart_wrap(State.market_plot_figure),
                            rx.el.p(
                                "Sin datos de primas.",
                                class_name="text-xs text-gray-400",
                            ),
                        ),
                    ),
                    class_name="p-4",
                ),
                class_name="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden h-full",
            ),
            rx.el.section(
                rx.el.div(
                    rx.el.h3(
                        copy.MERCADO_CHART_LR_TITLE,
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        copy.MERCADO_CHART_LR_SUB,
                        class_name="text-[10px] text-gray-500 mt-0.5 mb-2",
                    ),
                    rx.cond(
                        State.market_charts_busy,
                        chart_busy,
                        rx.cond(
                            State.market_ratio_ok,
                            plotly_chart_wrap(State.market_ratio_figure),
                            rx.el.p(
                                "Sin datos de loss ratio.",
                                class_name="text-xs text-gray-400",
                            ),
                        ),
                    ),
                    class_name="p-4",
                ),
                class_name="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden h-full",
            ),
            class_name="mt-5 grid grid-cols-1 xl:grid-cols-2 gap-4 w-full",
        ),
        rx.el.div(
            rx.el.section(
                rx.el.div(
                    rx.el.h4(
                        "YoY · primas La Fe",
                        class_name="text-xs font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        "Eje izq. = año A · eje der. = año B (miles Bs.)",
                        class_name="text-[10px] text-gray-500 mb-2",
                    ),
                    rx.cond(
                        State.market_charts_busy,
                        chart_busy,
                        rx.cond(
                            State.market_yoy_la_ok,
                            plotly_chart_wrap(State.market_yoy_la_figure),
                            rx.el.p(
                                "Elija dos años distintos o espere datos.",
                                class_name="text-xs text-gray-400",
                            ),
                        ),
                    ),
                    class_name="p-4",
                ),
                class_name="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden h-full",
            ),
            rx.el.section(
                rx.el.div(
                    rx.el.h4(
                        "YoY · primas mercado total",
                        class_name="text-xs font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        "Misma lógica de ejes por año",
                        class_name="text-[10px] text-gray-500 mb-2",
                    ),
                    rx.cond(
                        State.market_charts_busy,
                        chart_busy,
                        rx.cond(
                            State.market_yoy_mk_ok,
                            plotly_chart_wrap(State.market_yoy_mk_figure),
                            rx.el.p(
                                "—",
                                class_name="text-xs text-gray-400",
                            ),
                        ),
                    ),
                    class_name="p-4",
                ),
                class_name="rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden h-full",
            ),
            class_name="mt-4 grid grid-cols-1 xl:grid-cols-2 gap-4 w-full",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.h4(
                    "YoY · loss ratio La Fe",
                    class_name="text-xs font-semibold text-gray-900",
                ),
                rx.el.p(
                    "Ratio proxy por mes · un año por eje",
                    class_name="text-[10px] text-gray-500 mb-2",
                ),
                rx.cond(
                    State.market_charts_busy,
                    chart_busy,
                    rx.cond(
                        State.market_yoy_lr_ok,
                        plotly_chart_wrap(State.market_yoy_lr_figure),
                        rx.el.p("—", class_name="text-xs text-gray-400"),
                    ),
                ),
                class_name="p-4",
            ),
            class_name="mt-4 rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.h3(
                    copy.MERCADO_HEATMAP_TITLE,
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    copy.MERCADO_HEATMAP_SUB,
                    class_name="text-[10px] text-gray-500 mt-0.5 mb-2",
                ),
                rx.cond(
                    State.market_charts_busy,
                    chart_busy,
                    rx.cond(
                        State.market_heatmap_ok,
                        plotly_chart_wrap(State.market_heatmap_figure),
                        rx.el.p(
                            "Sin mapa de calor.",
                            class_name="text-xs text-gray-400",
                        ),
                    ),
                ),
                class_name="p-4",
            ),
            class_name="mt-4 rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden",
        ),
        rx.cond(
            State.market_plot_error != "",
            rx.vstack(
                rx.callout(
                    State.market_plot_error,
                    icon="triangle_alert",
                    color_scheme="red",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        copy.MERCADO_API_ERROR_ACTION,
                        on_click=State.load_sudeaseg_preview,
                        loading=State.market_charts_busy,
                        size="2",
                        color_scheme="purple",
                        class_name="rounded-lg",
                    ),
                    rx.link(
                        copy.MERCADO_API_ERROR_LINK,
                        href=State.admin_upload_url,
                        is_external=True,
                        class_name="text-sm text-violet-700 underline underline-offset-2 hover:text-violet-900",
                    ),
                    spacing="4",
                    align_items="center",
                    flex_wrap="wrap",
                ),
                spacing="2",
                align_items="start",
                width="100%",
            ),
        ),
        class_name="w-full space-y-0 pb-8",
    )


def cartera_panel() -> rx.Component:
    busy_kpi = rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Cargando…", size="2", color="gray"),
            spacing="2",
            align_items="center",
        ),
        width="100%",
        padding_y="8",
    )
    return rx.el.div(
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.span(copy.CARTERA_HERO_TITLE, class_name="text-[10px] font-semibold text-white/70 uppercase"),
                    rx.el.span(
                        State.cartera_period_label,
                        class_name="text-lg font-bold text-white ml-2 tabular-nums",
                    ),
                    class_name="flex flex-wrap items-baseline gap-1",
                ),
                rx.el.p(copy.CARTERA_LEAD, class_name="text-[11px] text-white/75 mt-1.5 max-w-2xl"),
                class_name="px-4 py-3",
            ),
            class_name="rounded-xl overflow-hidden shadow-md border border-violet-500/25",
            style={
                "background": f"linear-gradient(125deg, {BRAND_DEEP} 0%, {BRAND_PURPLE} 45%, #5b21b6 100%)",
            },
        ),
        rx.el.section(
            rx.el.div(
                rx.el.p(copy.CARTERA_PARAMS_BODY, class_name="text-[10px] text-gray-500 mb-2"),
                rx.hstack(
                    rx.vstack(
                        rx.text("Año", size="1", color="gray"),
                        rx.select(
                            copy.CARTERA_YEAR_OPTIONS,
                            value=State.input_year,
                            on_change=State.set_input_year,
                            size="2",
                            width="100px",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text("Mes", size="1", color="gray"),
                        rx.select(
                            copy.CARTERA_MONTH_OPTIONS,
                            value=State.input_month,
                            on_change=State.set_input_month,
                            size="2",
                            width="88px",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.button(
                        "Actualizar",
                        on_click=State.load_kpi,
                        loading=State.kpi_refresh_busy,
                        color_scheme="purple",
                        size="2",
                        class_name="rounded-lg",
                        style={"align_self": "flex-end"},
                    ),
                    spacing="3",
                    align_items="end",
                    flex_wrap="wrap",
                    width="100%",
                ),
                class_name="p-3 sm:p-4",
            ),
            class_name="mt-4 rounded-xl bg-white border border-gray-100 shadow-sm",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.p(copy.CARTERA_GAUGE_TITLE, class_name="text-xs font-semibold text-gray-900"),
                rx.el.p(copy.CARTERA_GAUGE_SUB, class_name="text-[10px] text-gray-500 mb-2"),
                rx.cond(
                    State.busy,
                    busy_kpi,
                    rx.cond(
                        State.kpi_gauge_ok,
                        plotly_chart_wrap(State.kpi_gauge_figure),
                        rx.el.p("Sin tacómetros.", class_name="text-xs text-gray-400"),
                    ),
                ),
                class_name="p-3 sm:p-4",
            ),
            class_name="mt-4 rounded-xl bg-white border border-gray-100 shadow-sm min-w-0 overflow-x-auto",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.p(copy.CARTERA_METRICS_TITLE, class_name="text-xs font-semibold text-gray-800 mb-2"),
                rx.cond(
                    State.busy,
                    busy_kpi,
                    rx.el.div(
                        metric_strip_cell("Persistencia", State.persistency),
                        metric_strip_cell("Ratio técnico", State.tlr),
                        metric_strip_cell("Prima media", State.avg_premium),
                        metric_strip_cell("Activas", State.active_n),
                        metric_strip_cell("Lapsos", State.lapsed_n),
                        class_name="grid grid-cols-2 sm:grid-cols-3 gap-2 w-full",
                    ),
                ),
                class_name="p-3 sm:p-4",
            ),
            class_name="mt-4 rounded-xl bg-white border border-gray-100 shadow-sm",
        ),
        rx.el.div(
            rx.cond(
                State.portfolio_viz_ok,
                rx.el.div(
                    portfolio_chart_card(
                        copy.PORTFOLIO_WATERFALL_T,
                        copy.PORTFOLIO_WATERFALL_S,
                        State.portfolio_waterfall_figure,
                    ),
                    portfolio_chart_card(
                        copy.PORTFOLIO_VIOLIN_T,
                        copy.PORTFOLIO_VIOLIN_S,
                        State.portfolio_violin_age_figure,
                    ),
                    class_name="flex flex-col gap-4",
                ),
                rx.cond(
                    State.portfolio_charts_busy,
                    busy_kpi,
                    rx.fragment(),
                ),
            ),
            class_name="mt-4",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.h3(
                    copy.PORTFOLIO_SECTION_TITLE,
                    class_name="text-sm font-semibold text-gray-900",
                ),
                rx.el.p(
                    copy.PORTFOLIO_SECTION_LEAD,
                    class_name="text-[10px] text-gray-500 mt-0.5 mb-3",
                ),
                rx.cond(
                    State.portfolio_viz_ok,
                    rx.el.div(
                        portfolio_chart_card(
                            copy.PORTFOLIO_SUNBURST_T,
                            copy.PORTFOLIO_SUNBURST_S,
                            State.portfolio_sunburst_figure,
                        ),
                        portfolio_chart_card(
                            copy.PORTFOLIO_TREEMAP_T,
                            copy.PORTFOLIO_TREEMAP_S,
                            State.portfolio_treemap_figure,
                        ),
                        portfolio_chart_card(
                            copy.PORTFOLIO_SANKEY_T,
                            copy.PORTFOLIO_SANKEY_S,
                            State.portfolio_sankey_figure,
                        ),
                        portfolio_chart_card(
                            copy.PORTFOLIO_STACKED_T,
                            copy.PORTFOLIO_STACKED_S,
                            State.portfolio_stacked_figure,
                        ),
                        portfolio_chart_card(
                            copy.PORTFOLIO_BOX_T,
                            copy.PORTFOLIO_BOX_S,
                            State.portfolio_box_status_figure,
                        ),
                        class_name="flex flex-col gap-4",
                    ),
                    rx.cond(
                        State.portfolio_charts_busy,
                        busy_kpi,
                        rx.el.p(
                            "Cargue el resumen KPI para ver el análisis avanzado de cartera.",
                            class_name="text-xs text-gray-400",
                        ),
                    ),
                ),
                rx.cond(
                    State.portfolio_note != "",
                    rx.el.div(
                        rx.callout(
                            State.portfolio_note,
                            icon="info",
                            color_scheme="blue",
                            width="100%",
                        ),
                        class_name="mt-3",
                    ),
                ),
                class_name="p-3 sm:p-4",
            ),
            class_name="mt-4 rounded-xl bg-white border border-gray-100 shadow-sm",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.p(copy.CARTERA_DONUT_TITLE, class_name="text-xs font-semibold text-gray-900"),
                rx.el.p(copy.CARTERA_DONUT_SUB, class_name="text-[10px] text-gray-500 mb-2"),
                rx.cond(
                    State.busy,
                    busy_kpi,
                    rx.cond(
                        State.cartera_donut_ok,
                        plotly_chart_wrap(State.cartera_donut_figure),
                        rx.el.p("—", class_name="text-xs text-gray-400"),
                    ),
                ),
                class_name="p-3 sm:p-4",
            ),
            class_name="mt-4 rounded-xl bg-white border border-gray-100 shadow-sm overflow-hidden min-h-0",
        ),
        rx.cond(
            State.kpi_load_failed,
            rx.vstack(
                rx.callout(
                    State.note,
                    icon="triangle_alert",
                    color_scheme="red",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        copy.CARTERA_API_ERROR_ACTION,
                        on_click=State.load_kpi,
                        loading=State.kpi_refresh_busy,
                        size="2",
                        color_scheme="purple",
                        class_name="rounded-lg",
                    ),
                    rx.link(
                        copy.CARTERA_API_ERROR_LINK,
                        href=State.admin_upload_url,
                        is_external=True,
                        class_name="text-sm text-violet-700 underline underline-offset-2 hover:text-violet-900",
                    ),
                    spacing="4",
                    align_items="center",
                    flex_wrap="wrap",
                ),
                spacing="2",
                align_items="start",
                width="100%",
            ),
            rx.cond(
                State.note != "",
                rx.callout(
                    State.note,
                    icon="info",
                    color_scheme="blue",
                    width="100%",
                ),
            ),
        ),
        class_name="w-full pb-8 space-y-0",
    )
