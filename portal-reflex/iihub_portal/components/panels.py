"""Paneles Mercado y Cartera — tarjetas redondeadas estilo dashboard CRM."""

import reflex as rx

from iihub_portal import copy
from iihub_portal.state import State
from iihub_portal.theme import BRAND_DEEP, BRAND_PURPLE


def snap_hero_cell(label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-xs font-semibold text-white/80 uppercase tracking-wide"),
        rx.el.p(value, class_name="text-xl sm:text-2xl font-bold text-white mt-1 tabular-nums"),
        class_name="rounded-xl px-4 py-3 bg-white/10 border border-white/20 backdrop-blur-md",
    )


def kpi_stat_card(title: str, value: rx.Var, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(title, class_name="text-sm font-medium text-gray-500"),
            rx.el.span(
                rx.icon(icon, size=18, class_name="text-violet-600"),
                class_name="p-2 bg-violet-50 rounded-xl",
            ),
            class_name="flex justify-between items-start gap-2",
        ),
        rx.el.p(value, class_name="text-2xl sm:text-3xl font-bold text-gray-900 mt-3 tabular-nums tracking-tight"),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow duration-200",
    )


def mercado_panel() -> rx.Component:
    snap_grid = rx.el.div(
        snap_hero_cell("Período", State.snap_period),
        snap_hero_cell("Primas YTD La Fe", State.snap_primas),
        snap_hero_cell("Loss ratio La Fe", State.snap_lr),
        snap_hero_cell("Cuota primas", State.snap_cuota),
        class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 w-full",
    )
    snap_more = rx.el.div(
        snap_hero_cell("Siniestros tot. La Fe", State.snap_sini),
        snap_hero_cell("Comisiones YTD", State.snap_comisiones),
        snap_hero_cell("Gasto adm. YTD", State.snap_gadm),
        snap_hero_cell("Loss ratio mercado", State.snap_mk_lr),
        class_name="grid grid-cols-2 lg:grid-cols-4 gap-3 w-full mt-4",
    )
    return rx.el.div(
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        copy.MERCADO_SNAPSHOT_TITLE,
                        class_name="text-lg font-semibold text-white",
                    ),
                    rx.el.p(
                        copy.MERCADO_SNAPSHOT_HINT,
                        class_name="text-xs text-white/75 mt-1",
                    ),
                    class_name="mb-5",
                ),
                rx.cond(
                    State.snap_ok,
                    snap_grid,
                    rx.el.p("Sin snapshot disponible.", class_name="text-white/90 text-sm"),
                ),
                rx.button(
                    rx.cond(State.show_snap_more, "Ocultar detalle", "Ver más indicadores"),
                    on_click=State.toggle_snap_more,
                    variant="outline",
                    size="2",
                    class_name="mt-4 text-white border-white/40 hover:bg-white/10",
                ),
                rx.cond(
                    State.show_snap_more,
                    rx.cond(State.snap_ok, snap_more),
                ),
                class_name="p-6 sm:p-8",
            ),
            class_name="rounded-2xl overflow-hidden shadow-xl shadow-violet-900/20 border border-violet-500/20",
            style={
                "background": f"linear-gradient(135deg, {BRAND_DEEP} 0%, {BRAND_PURPLE} 48%, #4c1d95 100%)",
            },
        ),
        rx.el.section(
            rx.el.div(
                rx.el.h3(
                    copy.MERCADO_PARAMS_TITLE,
                    class_name="text-base font-semibold text-gray-900",
                ),
                rx.el.p(
                    copy.MERCADO_PARAMS_BODY,
                    class_name="text-sm text-gray-500 mt-1 mb-6 leading-relaxed",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Desde", size="1", color="gray"),
                        rx.input(value=State.market_fy, on_change=State.set_market_fy, width="90px", size="2"),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text("Hasta", size="1", color="gray"),
                        rx.input(value=State.market_ty, on_change=State.set_market_ty, width="90px", size="2"),
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
                            width="160px",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.button(
                        "Actualizar gráficos",
                        on_click=State.load_sudeaseg_preview,
                        loading=State.market_charts_busy,
                        color_scheme="purple",
                        size="3",
                        class_name="rounded-xl",
                        style={"align_self": "flex-end"},
                    ),
                    spacing="4",
                    align_items="end",
                    flex_wrap="wrap",
                    width="100%",
                ),
                class_name="p-6 sm:p-8",
            ),
                    class_name="mt-8 rounded-2xl bg-white border border-gray-100 shadow-sm",
        ),
        rx.el.section(
            rx.el.details(
                rx.el.summary(
                    copy.VISUAL_SUGGESTIONS_TITLE,
                    class_name="cursor-pointer text-sm font-medium text-violet-700 list-none",
                ),
                rx.markdown(copy.VISUAL_SUGGESTIONS_MD),
                class_name="mt-6 p-4 sm:p-5 rounded-2xl bg-violet-50/60 border border-violet-100 [&_summary::-webkit-details-marker]:hidden",
            ),
            class_name="mt-6 w-full",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.h3(
                    copy.MERCADO_CHART_PRIM_TITLE,
                    class_name="text-base font-semibold text-gray-900",
                ),
                rx.el.p(
                    copy.MERCADO_CHART_PRIM_SUB,
                    class_name="text-xs text-gray-500 mt-1 mb-4",
                ),
                rx.cond(
                    State.market_charts_busy,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando series de mercado…", size="2", color="gray"),
                            spacing="2",
                            align_items="center",
                        ),
                        width="100%",
                        padding_y="10",
                    ),
                    rx.cond(
                        State.market_plot_ok,
                        rx.plotly(data=State.market_plot_figure),
                        rx.el.p(
                            "Sin datos de primas para el rango indicado.",
                            class_name="text-sm text-gray-400",
                        ),
                    ),
                ),
                class_name="p-5 sm:p-6",
            ),
            class_name="mt-8 rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.h3(
                    copy.MERCADO_CHART_LR_TITLE,
                    class_name="text-base font-semibold text-gray-900",
                ),
                rx.el.p(
                    copy.MERCADO_CHART_LR_SUB,
                    class_name="text-xs text-gray-500 mt-1 mb-4",
                ),
                rx.cond(
                    State.market_charts_busy,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando loss ratio…", size="2", color="gray"),
                            spacing="2",
                            align_items="center",
                        ),
                        width="100%",
                        padding_y="10",
                    ),
                    rx.cond(
                        State.market_ratio_ok,
                        rx.plotly(data=State.market_ratio_figure),
                        rx.el.p(
                            "Sin datos de loss ratio.",
                            class_name="text-sm text-gray-400",
                        ),
                    ),
                ),
                class_name="p-5 sm:p-6",
            ),
            class_name="mt-6 rounded-2xl bg-white border border-gray-100 shadow-sm overflow-hidden",
        ),
        rx.cond(
            State.market_plot_error != "",
            rx.callout(
                State.market_plot_error,
                icon="triangle_alert",
                color_scheme="red",
                width="100%",
            ),
        ),
        class_name="w-full space-y-0 pb-8",
    )


def cohorte_panel() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            copy.COHORT_LEAD,
            class_name="text-sm text-gray-500 mb-6 leading-relaxed",
        ),
        rx.el.section(
            rx.el.div(
                rx.hstack(
                    rx.vstack(
                        rx.text("Año de cohorte", size="2", weight="medium", color="gray"),
                        rx.input(
                            value=State.input_year,
                            on_change=State.set_input_year,
                            width="110px",
                            size="3",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.button(
                        "Actualizar KPIs",
                        on_click=State.load_kpi,
                        loading=State.busy,
                        color_scheme="purple",
                        size="3",
                        class_name="rounded-xl mt-5",
                    ),
                    spacing="4",
                    align_items="end",
                    flex_wrap="wrap",
                ),
                class_name="p-6 sm:p-8",
            ),
            class_name="rounded-2xl bg-white border border-gray-100 shadow-sm mb-8",
        ),
        rx.el.div(
            kpi_stat_card("Persistencia", State.persistency, "percent"),
            kpi_stat_card("Pólizas activas", State.active_n, "users"),
            kpi_stat_card("Prima media anual", State.avg_premium, "wallet"),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4 w-full",
        ),
        rx.el.div(
            kpi_stat_card("Lapsos", State.lapsed_n, "user-minus"),
            kpi_stat_card("Ratio técnico (demo)", State.tlr, "gauge"),
            class_name="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-[900px] mt-4",
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
        class_name="w-full pb-8 space-y-4",
    )
