"""Layout global: sidebar CRM + área principal con scroll."""

import reflex as rx

from iihub_portal.components.sidebar import mobile_nav_drawer, mobile_tab_bar, sidebar


def dashboard_layout(*children: rx.Component) -> rx.Component:
    return rx.el.div(
        sidebar(),
        mobile_nav_drawer(),
        rx.el.div(
            mobile_tab_bar(),
            rx.el.main(
                rx.el.div(
                    *children,
                    class_name="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8",
                ),
                class_name="flex-1 overflow-y-auto bg-gradient-to-b from-slate-50 to-slate-100/80 min-h-0",
            ),
            class_name="flex flex-col flex-1 min-w-0 md:ml-64 min-h-screen",
        ),
        class_name="flex min-h-screen bg-slate-50 text-gray-900 antialiased",
        style={"fontFamily": "'Inter', ui-sans-serif, system-ui, sans-serif"},
    )
