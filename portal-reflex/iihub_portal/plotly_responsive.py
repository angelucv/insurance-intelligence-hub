"""Normaliza layouts Plotly para que encajen en el ancho del contenedor (móvil)."""

from __future__ import annotations

from typing import Any


def merge_responsive_layout(layout: dict[str, Any] | None) -> dict[str, Any]:
    """autosize + sin ancho fijo en píxeles para que el gráfico use el contenedor."""
    m = dict(layout or {})
    m["autosize"] = True
    m.pop("width", None)
    return m
