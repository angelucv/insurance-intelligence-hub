"""Enlaces a otros orígenes (Django Admin, Streamlit): usar <a href>, no React Router."""

from __future__ import annotations

from typing import Any

import reflex as rx


def external_anchor(
    *children: rx.Component,
    href: rx.Var,
    class_name: str = "",
    on_click: Any = None,
) -> rx.Component:
    """Abre en pestaña nueva; evita que rutas absolutas se interpreten como path interno."""
    return rx.el.a(
        *children,
        href=href,
        target="_blank",
        rel="noopener noreferrer",
        on_click=on_click,
        class_name=class_name,
    )
