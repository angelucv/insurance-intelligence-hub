"""Portal ejecutivo: layout CRM + cartera / mercado."""

from __future__ import annotations

import reflex as rx

from iihub_portal import copy
from iihub_portal.components.dashboard_header import dashboard_header
from iihub_portal.components.layout import dashboard_layout
from iihub_portal.components.panels import cartera_panel, mercado_panel
from iihub_portal.state import State


def index() -> rx.Component:
    return dashboard_layout(
        dashboard_header(),
        rx.cond(
            State.ui_main_tab == "cartera",
            cartera_panel(),
            mercado_panel(),
        ),
        rx.el.footer(
            rx.el.p(
                copy.FOOTER_LEGAL,
                class_name="text-center text-xs text-gray-400 pt-10 pb-4 max-w-3xl mx-auto leading-relaxed",
            ),
            class_name="mt-auto border-t border-gray-200/80 bg-transparent",
        ),
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=State.portal_on_load)
