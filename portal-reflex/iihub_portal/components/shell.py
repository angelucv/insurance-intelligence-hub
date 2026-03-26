"""Cabecera, franja de marca y selector Mercado / Cartera."""

import reflex as rx

from iihub_portal import copy
from iihub_portal.state import State
from iihub_portal.theme import BRAND_DEEP, BRAND_LAVENDER, BRAND_PURPLE, CONTENT_MAX_WIDTH


def shell_header() -> rx.Component:
    """Barra superior: logo + acciones operativas y enlace al análisis detallado."""
    return rx.box(
        rx.box(
            rx.hstack(
                rx.image(
                    src="/logo-fe-1.jpg",
                    alt="Seguros La Fe",
                    height="88px",
                    width="auto",
                    style={"max_width": "min(100%, 320px)", "object_fit": "contain"},
                ),
                rx.spacer(),
                rx.hstack(
                    rx.link(
                        rx.button(
                            copy.BTN_CARGA_POLIZAS,
                            size="3",
                            color_scheme="purple",
                        ),
                        href=State.admin_upload_url,
                        is_external=True,
                    ),
                    rx.link(
                        rx.button(
                            copy.BTN_CARGA_SINIESTROS,
                            size="3",
                            color_scheme="purple",
                            variant="outline",
                        ),
                        href=State.admin_claims_upload_url,
                        is_external=True,
                    ),
                    rx.link(
                        rx.button(
                            copy.LINK_ANALISIS_BI_DETALLADO,
                            size="3",
                            color_scheme="purple",
                            variant="solid",
                            style={"font_weight": "600"},
                        ),
                        href=State.streamlit_lab_url,
                        is_external=True,
                    ),
                    spacing="3",
                    align_items="center",
                    flex_wrap="wrap",
                ),
                spacing="4",
                align_items="center",
                width="100%",
                flex_wrap="wrap",
            ),
            width="100%",
            max_width=CONTENT_MAX_WIDTH,
            margin_x="auto",
            padding_x="6",
            padding_y="4",
        ),
        width="100%",
        style={
            "background": "linear-gradient(180deg, #ffffff 0%, #faf5ff 100%)",
            "border_bottom": "1px solid var(--gray-5)",
            "box_shadow": "0 4px 24px rgba(88, 28, 135, 0.08)",
        },
    )


def hero_strip() -> rx.Component:
    """Franja de título bajo el header."""
    return rx.box(
        rx.box(
            rx.vstack(
                rx.heading(
                    copy.HERO_TITLE,
                    size="7",
                    style={"color": "white", "margin": 0},
                ),
                rx.text(
                    copy.HERO_SUBTITLE,
                    size="3",
                    style={"color": "rgba(255,255,255,0.9)"},
                ),
                spacing="2",
                align_items="start",
                width="100%",
            ),
            width="100%",
            max_width=CONTENT_MAX_WIDTH,
            margin_x="auto",
            padding_x="6",
            padding_y="5",
        ),
        width="100%",
        style={
            "background": f"linear-gradient(115deg, {BRAND_DEEP} 0%, {BRAND_PURPLE} 45%, {BRAND_LAVENDER} 100%)",
        },
    )


def tab_bar() -> rx.Component:
    """Selector principal Mercado vs Cartera."""
    return rx.box(
        rx.box(
            rx.hstack(
                rx.button(
                    copy.TAB_MERCADO,
                    on_click=State.pick_tab_mercado,
                    color_scheme="purple",
                    variant=rx.cond(State.ui_main_tab == "mercado", "solid", "outline"),
                ),
                rx.button(
                    copy.TAB_COHORTE,
                    on_click=State.pick_tab_cohorte,
                    color_scheme="purple",
                    variant=rx.cond(State.ui_main_tab == "cohorte", "solid", "outline"),
                ),
                spacing="3",
                flex_wrap="wrap",
                align_items="center",
            ),
            width="100%",
            max_width=CONTENT_MAX_WIDTH,
            margin_x="auto",
            padding_x="6",
            padding_y="4",
        ),
        width="100%",
        style={"background": "white", "border_bottom": "1px solid var(--gray-5)"},
    )
