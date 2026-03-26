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
        on_click=State.close_mobile_nav,
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
        on_click=State.close_mobile_nav,
        class_name="w-full no-underline",
    )


def _sidebar_brand_block() -> rx.Component:
    return rx.el.div(
        rx.image(
            src="/logo-fe-1.jpg",
            alt="Seguros La Fe",
            class_name="h-14 w-auto object-contain max-w-[200px] sm:max-w-[220px]",
        ),
        rx.el.p(
            copy.SIDEBAR_BRAND_TITLE,
            class_name="mt-2 text-sm font-semibold text-gray-900 tracking-tight leading-snug",
        ),
        class_name="px-4 py-5 border-b border-gray-100",
    )


def _sidebar_scroll_block() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            copy.SIDEBAR_SECTION_VIEWS,
            class_name="px-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2",
        ),
        rx.el.div(
            _nav_main(copy.TAB_CARTERA, "layout-dashboard", "cartera", State.pick_tab_cartera),
            _nav_main(copy.TAB_MERCADO, "line-chart", "mercado", State.pick_tab_mercado),
            _nav_main(copy.TAB_SUITE, "layers", "suite", State.pick_tab_suite),
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
    )


def _sidebar_footer_block() -> rx.Component:
    return rx.el.div(
        rx.color_mode.button(),
        rx.el.div(
            rx.el.p(
                copy.SIDEBAR_AUTHOR_LABEL,
                class_name="text-[10px] font-semibold text-gray-400 uppercase tracking-wider",
            ),
            rx.el.p(copy.AUTHOR_NAME, class_name="text-sm font-medium text-gray-800 mt-1"),
            rx.link(
                copy.AUTHOR_EMAIL,
                href=f"mailto:{copy.AUTHOR_EMAIL}",
                class_name="text-xs text-violet-600 hover:underline mt-0.5 inline-block",
            ),
            class_name="mt-4 pt-3 border-t border-gray-200/80",
        ),
        rx.el.p(
            copy.FOOTER_LEGAL,
            class_name="text-[10px] text-gray-400 leading-snug mt-3",
        ),
        class_name="p-4 border-t border-gray-100 bg-gray-50/80",
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        _sidebar_brand_block(),
        _sidebar_scroll_block(),
        _sidebar_footer_block(),
        class_name="hidden md:flex flex-col w-64 min-h-screen fixed left-0 top-0 z-30 "
        "bg-white border-r border-gray-200 shadow-[4px_0_24px_-8px_rgba(15,23,42,0.08)]",
    )


def mobile_nav_drawer() -> rx.Component:
    """Panel lateral en móvil: logo, mismos enlaces que el sidebar, Streamlit incluido."""
    panel = rx.el.aside(
        rx.el.button(
            rx.icon("x", size=22, class_name="text-gray-600"),
            type="button",
            on_click=State.close_mobile_nav,
            aria_label=copy.MOBILE_MENU_CLOSE_ARIA,
            class_name="absolute right-2 top-2 z-10 rounded-lg p-2 hover:bg-gray-100 active:bg-gray-200",
        ),
        _sidebar_brand_block(),
        _sidebar_scroll_block(),
        _sidebar_footer_block(),
        class_name=(
            "relative flex h-full w-[min(20rem,90vw)] max-w-[90vw] flex-col "
            "border-r border-gray-200 bg-white shadow-xl"
        ),
    )
    return rx.cond(
        State.mobile_nav_open,
        rx.el.div(
            rx.el.button(
                type="button",
                on_click=State.close_mobile_nav,
                aria_label=copy.MOBILE_MENU_CLOSE_ARIA,
                class_name="fixed inset-0 z-40 bg-black/40 backdrop-blur-[1px] md:hidden",
            ),
            rx.el.div(
                panel,
                class_name="fixed left-0 top-0 z-50 h-full md:hidden",
            ),
            class_name="md:hidden",
        ),
    )


def mobile_tab_bar() -> rx.Component:
    """Móvil: fila con menú (cajón) + logo + pestañas de vista."""
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon("menu", size=22, class_name="text-gray-700"),
                type="button",
                on_click=State.toggle_mobile_nav,
                aria_label=copy.MOBILE_MENU_OPEN_ARIA,
                class_name="shrink-0 rounded-xl p-2 hover:bg-violet-50 active:bg-violet-100/80",
            ),
            rx.image(
                src="/logo-fe-1.jpg",
                alt="Seguros La Fe",
                class_name="h-9 w-auto max-h-10 object-contain max-w-[min(140px,38vw)]",
            ),
            rx.el.div(
                rx.el.p(copy.SIDEBAR_BRAND_SHORT, class_name="text-[11px] font-bold text-gray-700 leading-tight"),
                rx.el.p("Portal BI", class_name="text-[10px] text-gray-500 leading-tight"),
                class_name="min-w-0 flex-1",
            ),
            class_name="flex items-center gap-2 px-3 pt-2 pb-1 border-b border-gray-100/90",
        ),
        rx.hstack(
            rx.button(
                copy.TAB_CARTERA,
                on_click=State.pick_tab_cartera,
                size="2",
                variant=rx.cond(State.ui_main_tab == "cartera", "solid", "outline"),
                color_scheme="purple",
                class_name="flex-1 rounded-xl min-w-0 text-xs sm:text-sm",
            ),
            rx.button(
                copy.TAB_MERCADO,
                on_click=State.pick_tab_mercado,
                size="2",
                variant=rx.cond(State.ui_main_tab == "mercado", "solid", "outline"),
                color_scheme="purple",
                class_name="flex-1 rounded-xl min-w-0 text-xs sm:text-sm",
            ),
            rx.button(
                copy.TAB_SUITE,
                on_click=State.pick_tab_suite,
                size="2",
                variant=rx.cond(State.ui_main_tab == "suite", "solid", "outline"),
                color_scheme="purple",
                class_name="flex-1 rounded-xl min-w-0 text-xs sm:text-sm",
            ),
            spacing="2",
            width="100%",
            padding_x="4",
            padding_y="3",
            flex_wrap="wrap",
        ),
        class_name="md:hidden sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-gray-200 shadow-sm",
    )
