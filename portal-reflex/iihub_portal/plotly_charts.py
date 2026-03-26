"""Estilo Plotly unificado para gráficos del portal (legible y consistente con la marca)."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
from plotly.graph_objs import Figure

from iihub_portal.theme import BRAND_PURPLE, MARKET_BLUE

_FONT = dict(family="Inter, system-ui, sans-serif", size=12, color="#334155")
_GRID = "#e2e8f0"
_PLOT_BG = "#f8fafc"


def polish_market_subplots(fig: Figure, *, height: int) -> None:
    """Tema claro, rejilla suave, márgenes para leyendas."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor=_PLOT_BG,
        font=_FONT,
        height=height,
        margin=dict(l=56, r=64, t=20, b=52),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.85)",
            font=dict(size=11, color="#475569"),
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter, system-ui, sans-serif"),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=_GRID,
        gridwidth=1,
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor="#cbd5e1",
        tickfont=dict(size=11, color="#64748b"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=_GRID,
        gridwidth=1,
        zeroline=False,
        tickfont=dict(size=11, color="#64748b"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=_GRID,
        zeroline=False,
        tickfont=dict(size=11, color="#64748b"),
        secondary_y=True,
    )


def polish_ratio_figure(fig: Figure, *, height: int) -> None:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor=_PLOT_BG,
        font=_FONT,
        height=height,
        margin=dict(l=56, r=48, t=20, b=52),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.85)",
            font=dict(size=11, color="#475569"),
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter, system-ui, sans-serif"),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=_GRID,
        zeroline=False,
        showline=True,
        linecolor="#cbd5e1",
        tickfont=dict(size=11, color="#64748b"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=_GRID,
        zeroline=False,
        tickfont=dict(size=11, color="#64748b"),
    )


def trace_primas_la_fe(xs: list[str], y: list[Any]) -> go.Scatter:
    return go.Scatter(
        x=xs,
        y=y,
        name="La Fe (eje izq.)",
        mode="lines",
        line=dict(color=BRAND_PURPLE, width=2.8, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(112, 41, 179, 0.12)",
        hovertemplate="%{x}<br>La Fe: %{y:,.2f} mil Bs.<extra></extra>",
    )


def trace_primas_mercado(xs: list[str], y: list[Any]) -> go.Scatter:
    return go.Scatter(
        x=xs,
        y=y,
        name="Mercado total (eje der.)",
        mode="lines",
        line=dict(color=MARKET_BLUE, width=2.8, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(2, 132, 199, 0.1)",
        hovertemplate="%{x}<br>Mercado: %{y:,.2f} mil Bs.<extra></extra>",
    )


def trace_lr_la_fe(xs: list[str], y: list[Any]) -> go.Scatter:
    return go.Scatter(
        x=xs,
        y=y,
        name="Loss ratio La Fe",
        mode="lines+markers",
        line=dict(color=BRAND_PURPLE, width=2.5, shape="spline"),
        marker=dict(size=4, color=BRAND_PURPLE, line=dict(width=0)),
        hovertemplate="%{x}<br>La Fe: %{y:.4f}<extra></extra>",
    )


def trace_lr_mercado(xs: list[str], y: list[Any]) -> go.Scatter:
    return go.Scatter(
        x=xs,
        y=y,
        name="Loss ratio mercado",
        mode="lines+markers",
        line=dict(color=MARKET_BLUE, width=2.5, shape="spline"),
        marker=dict(size=4, color=MARKET_BLUE, line=dict(width=0)),
        hovertemplate="%{x}<br>Mercado: %{y:.4f}<extra></extra>",
    )
