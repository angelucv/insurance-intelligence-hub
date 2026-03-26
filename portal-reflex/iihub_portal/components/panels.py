"""Paneles Mercado SUDEASEG y Cartera cohorte."""

import reflex as rx

from iihub_portal import copy
from iihub_portal.state import State
from iihub_portal.theme import BRAND_DEEP, BRAND_PURPLE, BRAND_MUTED, CONTENT_MAX_WIDTH


def snap_hero_cell(label: str, value: rx.Var) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                label,
                size="2",
                style={"color": "rgba(255,255,255,0.88)", "font_weight": "600"},
            ),
            rx.heading(value, size="7", style={"color": "white", "margin": 0, "line_height": "1.1"}),
            spacing="1",
            align_items="start",
            width="100%",
        ),
        padding="1.1rem",
        border_radius="14px",
        width="100%",
        style={
            "background": "rgba(255,255,255,0.12)",
            "border": "1px solid rgba(255,255,255,0.28)",
            "backdrop_filter": "blur(10px)",
        },
    )


def kpi_card(title: str, value: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(title, size="2", weight="bold", color="gray"),
            rx.heading(value, size="6", style={"color": BRAND_DEEP}),
            spacing="1",
            align_items="start",
            width="100%",
        ),
        style={
            "border": "1px solid var(--gray-6)",
            "box_shadow": "0 4px 16px rgba(15, 23, 42, 0.06)",
            "min_height": "118px",
        },
        width="100%",
    )


def mercado_panel() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.box(
                rx.vstack(
                    rx.text(
                        "Último cierre con dato La Fe · YTD (miles Bs.; ratios como fracción)",
                        size="2",
                        style={"color": "rgba(255,255,255,0.9)", "font_weight": "600"},
                    ),
                    rx.cond(
                        State.snap_ok,
                        rx.grid(
                            snap_hero_cell("Período", State.snap_period),
                            snap_hero_cell("Primas YTD La Fe", State.snap_primas),
                            snap_hero_cell("Loss ratio La Fe", State.snap_lr),
                            snap_hero_cell("Cuota primas", State.snap_cuota),
                            columns="4",
                            spacing="3",
                            width="100%",
                        ),
                        rx.text("Sin snapshot disponible.", color="white"),
                    ),
                    rx.button(
                        rx.cond(State.show_snap_more, "Ocultar detalle del cierre", "Ver más indicadores del cierre"),
                        on_click=State.toggle_snap_more,
                        variant="outline",
                        style={
                            "color": "white",
                            "border_color": "rgba(255,255,255,0.55)",
                            "margin_top": "0.5rem",
                        },
                    ),
                    rx.cond(
                        State.show_snap_more,
                        rx.cond(
                            State.snap_ok,
                            rx.box(
                                rx.grid(
                                    snap_hero_cell("Siniestros tot. La Fe", State.snap_sini),
                                    snap_hero_cell("Comisiones YTD", State.snap_comisiones),
                                    snap_hero_cell("Gasto adm. YTD", State.snap_gadm),
                                    snap_hero_cell("Loss ratio mercado", State.snap_mk_lr),
                                    columns="4",
                                    spacing="3",
                                    width="100%",
                                ),
                                margin_top="0.75rem",
                                width="100%",
                            ),
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                max_width=CONTENT_MAX_WIDTH,
                margin_x="auto",
                padding_x="6",
                padding_y="6",
            ),
            width="100%",
            style={
                "background": f"linear-gradient(120deg, {BRAND_DEEP} 0%, {BRAND_PURPLE} 50%, #4c1d95 100%)",
            },
        ),
        rx.box(
            rx.card(
                rx.vstack(
                    rx.text(copy.MERCADO_PARAMS_TITLE, weight="bold", size="3", color=BRAND_DEEP),
                    rx.text(
                        copy.MERCADO_PARAMS_BODY,
                        size="2",
                        color="gray",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.text("Desde", size="1", color="gray"),
                            rx.input(
                                value=State.market_fy,
                                on_change=State.set_market_fy,
                                width="90px",
                            ),
                            spacing="1",
                            align_items="start",
                        ),
                        rx.vstack(
                            rx.text("Hasta", size="1", color="gray"),
                            rx.input(
                                value=State.market_ty,
                                on_change=State.set_market_ty,
                                width="90px",
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
                            style={"align_self": "flex-end"},
                        ),
                        spacing="4",
                        align_items="end",
                        flex_wrap="wrap",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                style={"border": f"1px solid {BRAND_PURPLE}22", "box_shadow": "0 8px 28px rgba(88,28,135,0.08)"},
                width="100%",
            ),
            width="100%",
            max_width=CONTENT_MAX_WIDTH,
            margin_x="auto",
            padding_x="6",
            padding_top="5",
        ),
        rx.box(
            rx.text(
                "Primas netas (miles Bs.): La Fe vs total sector. Abajo: evolución del loss ratio proxy.",
                size="2",
                color="gray",
            ),
            rx.cond(
                State.market_plot_ok,
                rx.plotly(data=State.market_plot_figure),
            ),
            rx.cond(
                State.market_ratio_ok,
                rx.plotly(data=State.market_ratio_figure),
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
            spacing="4",
            width="100%",
            max_width=CONTENT_MAX_WIDTH,
            margin_x="auto",
            padding_x="6",
            padding_bottom="8",
            align_items="stretch",
        ),
        spacing="0",
        width="100%",
    )


def cohorte_panel() -> rx.Component:
    return rx.vstack(
        rx.heading(copy.COHORT_TITLE, size="5", style={"color": BRAND_DEEP}),
        rx.text(
            copy.COHORT_LEAD,
            size="2",
            color="gray",
        ),
        rx.hstack(
            rx.text("Año cohorte:", weight="medium", color=BRAND_MUTED),
            rx.input(
                value=State.input_year,
                on_change=State.set_input_year,
                width="100px",
            ),
            rx.button(
                "Actualizar indicadores",
                on_click=State.load_kpi,
                loading=State.busy,
                color_scheme="purple",
            ),
            spacing="3",
            align_items="center",
            flex_wrap="wrap",
        ),
        rx.grid(
            kpi_card("Persistencia", State.persistency),
            kpi_card("Pólizas activas", State.active_n),
            kpi_card("Prima media anual", State.avg_premium),
            columns="3",
            spacing="3",
            width="100%",
        ),
        rx.grid(
            kpi_card("Lapsos", State.lapsed_n),
            kpi_card("Ratio técnico (demo)", State.tlr),
            columns="2",
            spacing="3",
            width="100%",
            max_width="720px",
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
        spacing="5",
        width="100%",
        max_width=CONTENT_MAX_WIDTH,
        margin_x="auto",
        padding_x="6",
        padding_y="8",
        align_items="stretch",
    )
