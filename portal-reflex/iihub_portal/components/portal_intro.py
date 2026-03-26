"""Bloque introductorio: qué es el portal y cómo se relacionan cartera, mercado y Admin."""

import reflex as rx

from iihub_portal import copy
from iihub_portal.state import State


def portal_intro_banner() -> rx.Component:
    return rx.cond(
        State.show_portal_guide,
        rx.el.div(
            rx.hstack(
                rx.el.h3(
                    copy.PORTAL_INTRO_TITLE,
                    class_name="text-sm font-semibold text-gray-900 m-0",
                ),
                rx.button(
                    copy.PORTAL_INTRO_DISMISS,
                    on_click=State.dismiss_portal_guide,
                    size="1",
                    variant="outline",
                    color_scheme="purple",
                    class_name="shrink-0 rounded-lg text-xs",
                ),
                align_items="center",
                justify_content="space-between",
                width="100%",
                spacing="3",
            ),
            rx.markdown(
                copy.PORTAL_INTRO_MD,
                class_name="text-sm text-gray-600 mt-3 leading-relaxed [&_strong]:text-gray-800 [&_strong]:font-semibold",
            ),
            class_name="rounded-2xl border border-violet-100 bg-white/95 shadow-sm p-4 sm:p-5 mb-6 max-w-4xl",
        ),
    )
