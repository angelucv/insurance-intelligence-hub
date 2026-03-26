"""Portal ejecutivo: panorama API (mercado + cohorte) y acciones operativas."""

from __future__ import annotations

import reflex as rx

from iihub_portal import copy
from iihub_portal.components.panels import cohorte_panel, mercado_panel
from iihub_portal.components.shell import hero_strip, shell_header, tab_bar
from iihub_portal.state import State


def index() -> rx.Component:
    return rx.fragment(
        rx.box(
            rx.color_mode.button(position="top-right"),
            shell_header(),
            hero_strip(),
            tab_bar(),
            rx.box(
                rx.cond(
                    State.ui_main_tab == "mercado",
                    mercado_panel(),
                    cohorte_panel(),
                ),
                width="100%",
                min_height="50vh",
                style={"background": "var(--gray-2)"},
            ),
            rx.box(
                rx.text(
                    copy.FOOTER_LEGAL,
                    size="1",
                    color="gray",
                    text_align="center",
                    width="100%",
                ),
                padding_y="4",
                width="100%",
                style={"background": "var(--gray-2)"},
            ),
            min_height="100vh",
        ),
    )


app = rx.App()
app.add_page(index, on_load=State.portal_on_load)
