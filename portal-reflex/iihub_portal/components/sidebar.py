"""Barra lateral fija estilo dashboard CRM (Broker-CRM-Dashboard)."""

import reflex as rx

from iihub_portal import copy
from iihub_portal.state import State


def _nav_main(
    label: str,
    icon: str,
    tab: str,
    on_click,
) -> rx.Component:
    active = State.ui_main_tab == tab
    return rx.el.button(
        rx.icon(
            icon,
            size=20,
            class_name=rx.cond(active, "text-violet-600", "text-gray-400 group-hover:text-gray-500"),
        ),
        rx.el.span(label, class_name="ml-3 text-sm font-medium text-left"),
        on_click=on_click,
        class_name=rx.cond(
            active,
            "group flex items-center w-full px-3 py-2.5 rounded-xl bg-violet-50 text-violet-800 "
            "border border-violet-100 shadow-sm transition-all",
            "group flex items-center w-full px-3 py-2.5 rounded-xl text-gray-700 hover:bg-gray-50 "
            "border border-transparent transition-colors",
        ),
    )


def _nav_link(label: str, icon: str, href: rx.Var) -> rx.Component:
    return rx.link(
        rx.el.div(
            rx.icon(icon, size=18, class_name="text-gray-400 shrink-0"),
            rx.el.span(label, class_name="ml-3 text-sm text-gray-700"),
            class_name="flex items-center w-full px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors",
        ),
        href=href,
        is_external=True,
        class_name="w-full no-underline",
    )


def _nav_link_primary(label: str, icon: str, href: rx.Var) -> rx.Component:
    return rx.link(
        rx.el.div(
            rx.icon(icon, size=18, class_name="text-white shrink-0"),
            rx.el.span(label, class_name="ml-3 text-sm font-semibold text-white"),
            class_name="flex items-center w-full px-3 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 "
            "shadow-md shadow-violet-500/25 hover:from-violet-500 hover:to-purple-500 transition-all",
        ),
        href=href,
        is_external=True,
        class_name="w-full no-underline",
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.image(
                src="/logo-fe-1.jpg",
                alt="Seguros La Fe",
                class_name="h-9 w-auto object-contain max-w-[140px]",
            ),
            rx.el.div(
                rx.el.span(copy.SIDEBAR_BRAND_SHORT, class_name="text-lg font-bold text-gray-900 tracking-tight"),
                rx.el.span(
                    " · La Fe",
                    class_name="text-xs font-medium text-violet-600 ml-1",
                ),
                class_name="flex items-baseline flex-wrap mt-2",
            ),
            class_name="px-4 py-5 border-b border-gray-100",
        ),
        rx.el.div(
            rx.el.p(copy.SIDEBAR_SECTION_VIEWS, class_name="px-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2"),
            rx.el.div(
                _nav_main(copy.TAB_MERCADO, "line-chart", "mercado", State.pick_tab_mercado),
                _nav_main(copy.TAB_COHORTE, "layers", "cohorte", State.pick_tab_cohorte),
                class_name="space-y-1",
            ),
            rx.el.p(
                copy.SIDEBAR_SECTION_OPS,
                class_name="px-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-8",
            ),
            rx.el.div(
                _nav_link(copy.BTN_CARGA_POLIZAS, "upload", State.admin_upload_url),
                _nav_link(copy.BTN_CARGA_SINIESTROS, "file-text", State.admin_claims_upload_url),
                _nav_link_primary(copy.LINK_ANALISIS_BI_DETALLADO, "bar-chart-3", State.streamlit_lab_url),
                class_name="space-y-1",
            ),
            class_name="flex-1 px-2 py-4 overflow-y-auto",
        ),
        rx.el.div(
            rx.color_mode.button(),
            rx.el.p(
                copy.FOOTER_LEGAL,
                class_name="text-[10px] text-gray-400 leading-snug mt-3",
            ),
            class_name="p-4 border-t border-gray-100 bg-gray-50/80",
        ),
        class_name="hidden md:flex flex-col w-64 min-h-screen fixed left-0 top-0 z-30 "
        "bg-white border-r border-gray-200 shadow-[4px_0_24px_-8px_rgba(15,23,42,0.08)]",
    )


def mobile_tab_bar() -> rx.Component:
    """Selector compacto en móvil (sidebar oculto)."""
    return rx.el.div(
        rx.hstack(
            rx.button(
                copy.TAB_MERCADO,
                on_click=State.pick_tab_mercado,
                size="2",
                variant=rx.cond(State.ui_main_tab == "mercado", "solid", "outline"),
                color_scheme="purple",
                class_name="flex-1 rounded-xl",
            ),
            rx.button(
                copy.TAB_COHORTE,
                on_click=State.pick_tab_cohorte,
                size="2",
                variant=rx.cond(State.ui_main_tab == "cohorte", "solid", "outline"),
                color_scheme="purple",
                class_name="flex-1 rounded-xl",
            ),
            spacing="2",
            width="100%",
            padding_x="4",
            padding_y="3",
        ),
        class_name="md:hidden sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-gray-200 shadow-sm",
    )
