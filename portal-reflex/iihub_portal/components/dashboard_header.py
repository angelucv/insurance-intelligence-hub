"""Cabecera del área principal (título contextual por vista)."""

import reflex as rx

from iihub_portal import copy
from iihub_portal.state import State


def dashboard_header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.p(
                copy.HEADER_GREETING,
                class_name="text-xs font-semibold text-violet-600 uppercase tracking-wider",
            ),
            rx.cond(
                State.ui_main_tab == "mercado",
                rx.heading(
                    copy.TAB_MERCADO,
                    size="8",
                    class_name="font-bold text-gray-900 tracking-tight mt-1",
                ),
                rx.heading(
                    copy.COHORT_PAGE_HEADING,
                    size="8",
                    class_name="font-bold text-gray-900 tracking-tight mt-1",
                ),
            ),
            rx.cond(
                State.ui_main_tab == "mercado",
                rx.el.p(
                    copy.HEADER_SUB_MERCADO,
                    class_name="text-sm text-gray-500 mt-2 max-w-2xl leading-relaxed",
                ),
                rx.el.p(
                    copy.HEADER_SUB_COHORTE,
                    class_name="text-sm text-gray-500 mt-2 max-w-2xl leading-relaxed",
                ),
            ),
        ),
        class_name="mb-2 pb-6 border-b border-gray-200/80",
    )
