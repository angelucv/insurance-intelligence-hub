"""Enlaces a otros orígenes (Django Admin, Streamlit).

Reflex 0.8 sustituye ``rx.el.a`` por React Router (navegación SPA con ``to=``), lo que
rompe URLs absolutas (p. ej. ``http://127.0.0.1:8080/admin/...``). Aquí usamos el
elemento HTML ``<a>`` real (``BaseHTML`` con tag ``a``).
"""

from __future__ import annotations

from typing import Any

import reflex as rx
from reflex.components.el.elements.inline import A as HtmlAnchor


def external_anchor(
    *children: rx.Component,
    href: rx.Var,
    class_name: str = "",
    on_click: Any = None,
) -> rx.Component:
    """Abre en pestaña nueva; ``href`` puede ser Var (URLs desde State)."""
    return HtmlAnchor.create(
        *children,
        href=href,
        target="_blank",
        rel="noopener noreferrer",
        on_click=on_click,
        class_name=class_name,
    )
