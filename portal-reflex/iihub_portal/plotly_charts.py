"""Estilo Plotly unificado para gráficos del portal (legible y consistente con la marca)."""

from __future__ import annotations

import math
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


MONTH_NAMES_ES = (
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
)


def _month_series_primas(rows: list[dict[str, Any]]) -> list[Any]:
    m: dict[int, Any] = {}
    for row in rows:
        mo = int(row["period_month"])
        m[mo] = row.get("primas_netas_thousands_bs")
    return [m.get(i) for i in range(1, 13)]


def _month_series_lr(rows: list[dict[str, Any]]) -> list[Any]:
    m: dict[int, Any] = {}
    for row in rows:
        mo = int(row["period_month"])
        vlr = row.get("loss_ratio_proxy")
        m[mo] = float(vlr) if vlr is not None else None
    return [m.get(i) for i in range(1, 13)]


def build_yoy_primas_figure(
    year_left: int,
    year_right: int,
    la_points_left: list[dict[str, Any]],
    la_points_right: list[dict[str, Any]],
    *,
    height: int = 340,
) -> Figure:
    """Misma métrica (primas La Fe), un año por eje Y, meses alineados."""
    from plotly.subplots import make_subplots

    xs = list(MONTH_NAMES_ES)
    y_l = _month_series_primas(la_points_left)
    y_r = _month_series_primas(la_points_right)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=y_l,
            name=f"La Fe {year_left}",
            mode="lines+markers",
            line=dict(color=BRAND_PURPLE, width=2.8, shape="spline"),
            hovertemplate=f"%{{x}} {year_left}<br>%{{y:,.2f}} mil Bs.<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=y_r,
            name=f"La Fe {year_right}",
            mode="lines+markers",
            line=dict(color="#a855f7", width=2.8, shape="spline", dash="dot"),
            hovertemplate=f"%{{x}} {year_right}<br>%{{y:,.2f}} mil Bs.<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_xaxes(title_text="Mes (calendario)")
    fig.update_yaxes(title_text=f"La Fe {year_left} · miles Bs.", secondary_y=False)
    fig.update_yaxes(title_text=f"La Fe {year_right} · miles Bs.", secondary_y=True)
    polish_market_subplots(fig, height=height)
    return fig


def build_yoy_mercado_figure(
    year_left: int,
    year_right: int,
    tot_points_left: list[dict[str, Any]],
    tot_points_right: list[dict[str, Any]],
    *,
    height: int = 340,
) -> Figure:
    from plotly.subplots import make_subplots

    xs = list(MONTH_NAMES_ES)
    y_l = _month_series_primas(tot_points_left)
    y_r = _month_series_primas(tot_points_right)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=y_l,
            name=f"Mercado {year_left}",
            mode="lines+markers",
            line=dict(color=MARKET_BLUE, width=2.8, shape="spline"),
            hovertemplate=f"%{{x}} {year_left}<br>%{{y:,.2f}} mil Bs.<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=y_r,
            name=f"Mercado {year_right}",
            mode="lines+markers",
            line=dict(color="#38bdf8", width=2.8, shape="spline", dash="dot"),
            hovertemplate=f"%{{x}} {year_right}<br>%{{y:,.2f}} mil Bs.<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_xaxes(title_text="Mes (calendario)")
    fig.update_yaxes(title_text=f"Mercado {year_left} · miles Bs.", secondary_y=False)
    fig.update_yaxes(title_text=f"Mercado {year_right} · miles Bs.", secondary_y=True)
    polish_market_subplots(fig, height=height)
    return fig


def build_yoy_lr_compare_figure(
    year_left: int,
    year_right: int,
    la_left: list[dict[str, Any]],
    la_right: list[dict[str, Any]],
    *,
    height: int = 300,
) -> Figure:
    """Loss ratio La Fe: dos años, doble eje."""
    from plotly.subplots import make_subplots

    xs = list(MONTH_NAMES_ES)
    y_l = _month_series_lr(la_left)
    y_r = _month_series_lr(la_right)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=y_l,
            name=f"LR La Fe {year_left}",
            mode="lines+markers",
            line=dict(color=BRAND_PURPLE, width=2.5, shape="spline"),
            hovertemplate=f"%{{x}} {year_left}<br>%{{y:.4f}}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=y_r,
            name=f"LR La Fe {year_right}",
            mode="lines+markers",
            line=dict(color="#c084fc", width=2.5, shape="spline", dash="dot"),
            hovertemplate=f"%{{x}} {year_right}<br>%{{y:.4f}}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_xaxes(title_text="Mes")
    fig.update_yaxes(title_text=f"LR {year_left} (fracción)", secondary_y=False)
    fig.update_yaxes(title_text=f"LR {year_right} (fracción)", secondary_y=True)
    polish_market_subplots(fig, height=height)
    return fig


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


def build_kpi_gauge_figure(
    *,
    persistency_pct: float,
    technical_loss_pct: float | None,
    active_share_pct: float,
    height: int = 360,
    cohort_year: int | None = None,
) -> Figure:
    """Tacómetros (Plotly Indicator) con referencias, umbrales y delta respecto a benchmarks."""
    from plotly.subplots import make_subplots

    tlr = float(technical_loss_pct) if technical_loss_pct is not None else 0.0
    tlr_axis_max = max(120.0, tlr * 1.15, 1.0)
    ref_persist = 85.0
    ref_active = 80.0
    thr_tlr_warn = min(100.0, tlr_axis_max)

    fig = make_subplots(
        rows=1,
        cols=3,
        horizontal_spacing=0.07,
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
    )
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=min(100.0, max(0.0, persistency_pct)),
            number={"suffix": "%", "font": {"size": 26}, "valueformat": ".1f"},
            delta={"reference": ref_persist, "relative": False, "valueformat": ".1f", "suffix": "%"},
            title={
                "text": "Persistencia<br><sup style='font-size:10px;color:#64748b'>activas / cartera</sup>",
                "font": {"size": 13},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#94a3b8",
                    "tickvals": [0, 25, 50, 75, 100],
                    "ticktext": ["0", "25", "50", "75", "100"],
                },
                "bar": {"color": BRAND_PURPLE, "thickness": 0.35},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": "#e2e8f0",
                "steps": [
                    {"range": [0, 40], "color": "#f8fafc"},
                    {"range": [40, 70], "color": "#f1f5f9"},
                    {"range": [70, 100], "color": "#e8e2f4"},
                ],
                "threshold": {
                    "line": {"color": "#16a34a", "width": 3},
                    "thickness": 0.85,
                    "value": 90.0,
                },
            },
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=min(tlr_axis_max, max(0.0, tlr)),
            number={"suffix": "%", "font": {"size": 26}, "valueformat": ".1f"},
            title={
                "text": "Ratio técnico<br><sup style='font-size:10px;color:#64748b'>demo · menor es mejor</sup>",
                "font": {"size": 13},
            },
            gauge={
                "axis": {
                    "range": [0, tlr_axis_max],
                    "tickwidth": 1,
                    "tickcolor": "#94a3b8",
                },
                "bar": {"color": MARKET_BLUE, "thickness": 0.35},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": "#e2e8f0",
                "steps": [
                    {"range": [0, tlr_axis_max * 0.5], "color": "#f0fdf4"},
                    {"range": [tlr_axis_max * 0.5, tlr_axis_max * 0.8], "color": "#fef9c3"},
                    {"range": [tlr_axis_max * 0.8, tlr_axis_max], "color": "#fee2e2"},
                ],
                "threshold": {
                    "line": {"color": "#dc2626", "width": 3},
                    "thickness": 0.85,
                    "value": thr_tlr_warn,
                },
            },
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=min(100.0, max(0.0, active_share_pct)),
            number={"suffix": "%", "font": {"size": 26}, "valueformat": ".1f"},
            delta={"reference": ref_active, "relative": False, "valueformat": ".1f", "suffix": "%"},
            title={
                "text": "Activas (share)<br><sup style='font-size:10px;color:#64748b'>activas / (activas+lapsos)</sup>",
                "font": {"size": 13},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#94a3b8",
                    "tickvals": [0, 25, 50, 75, 100],
                },
                "bar": {"color": "#7c3aed", "thickness": 0.35},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": "#e2e8f0",
                "steps": [
                    {"range": [0, 33], "color": "#f8fafc"},
                    {"range": [33, 66], "color": "#f1f5f9"},
                    {"range": [66, 100], "color": "#ede9fe"},
                ],
                "threshold": {
                    "line": {"color": "#0d9488", "width": 3},
                    "thickness": 0.85,
                    "value": 50.0,
                },
            },
        ),
        row=1,
        col=3,
    )
    ann: list[dict[str, Any]] = []
    if cohort_year is not None:
        ann.append(
            {
                "text": f"Cohorte {cohort_year} · benchmarks orientativos",
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 1.12,
                "showarrow": False,
                "font": {"size": 11, "color": "#64748b"},
                "xanchor": "center",
            }
        )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        font=_FONT,
        height=height,
        margin=dict(l=20, r=20, t=56 if cohort_year else 44, b=28),
        annotations=ann,
    )
    return fig


def build_cartera_donut_figure(
    *,
    active: int,
    lapsed: int,
    height: int = 300,
) -> Figure:
    """Composición activas vs lapsos (donut)."""
    total = int(active) + int(lapsed)
    if total <= 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Sin pólizas en esta cartera",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="#64748b"),
        )
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(255,255,255,0)",
            font=_FONT,
            height=height,
            margin=dict(l=24, r=24, t=24, b=24),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Pólizas activas", "Lapsos"],
                values=[active, lapsed],
                hole=0.58,
                sort=False,
                direction="clockwise",
                marker=dict(
                    colors=[BRAND_PURPLE, "#94a3b8"],
                    line=dict(color="white", width=3),
                ),
                textinfo="label+percent",
                textposition="outside",
                textfont=dict(size=12, color="#334155"),
                hovertemplate="<b>%{label}</b><br>cantidad: %{value:,}<br>%{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        font=_FONT,
        height=height,
        margin=dict(l=24, r=24, t=32, b=24),
        showlegend=False,
        annotations=[
            dict(
                text=f"<b>{total:,}</b><br>pólizas",
                x=0.5,
                y=0.5,
                font_size=15,
                font_family="Inter, system-ui, sans-serif",
                font_color="#0f172a",
                showarrow=False,
            )
        ],
    )
    return fig


def _to_float(x: Any) -> float:
    if x is None:
        return float("nan")
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def _row_normalize_01(row: list[float]) -> list[float]:
    """Escala cada fila a [0,1] para comparar formas entre métricas de distinta magnitud."""
    vals = [v for v in row if not math.isnan(v)]
    if not vals:
        return [float("nan")] * len(row)
    lo, hi = min(vals), max(vals)
    out: list[float] = []
    for v in row:
        if math.isnan(v):
            out.append(float("nan"))
        elif hi <= lo:
            out.append(0.5)
        else:
            out.append((v - lo) / (hi - lo))
    return out


def _subsample_series(
    xs: list[str],
    *series: list[Any],
    max_points: int = 48,
) -> tuple[list[str], tuple[list[Any], ...]]:
    n = len(xs)
    if n <= max_points:
        return xs, series
    step = max(1, n // max_points)
    idx = list(range(0, n, step))
    if len(idx) > max_points:
        idx = idx[:max_points]
    xs_n = [xs[i] for i in idx]
    ser_n = tuple([s[i] for i in idx] for s in series)
    return xs_n, ser_n


def build_market_metrics_heatmap(
    xs: list[str],
    y_primas_la: list[Any],
    y_primas_mk: list[Any],
    y_lr_la: list[Any],
    y_lr_mk: list[Any],
    *,
    height: int = 400,
    max_points: int = 48,
) -> Figure:
    """
    Mapa de calor: filas = métricas, columnas = período.
    Valores normalizados por fila (0–1) para que primas y LR sean comparables visualmente;
    el valor original va en el hover.
    """
    xs_s, (pla, pmk, lra, lrm) = _subsample_series(
        xs,
        y_primas_la,
        y_primas_mk,
        y_lr_la,
        y_lr_mk,
        max_points=max_points,
    )
    z_raw = [
        [_to_float(a) for a in pla],
        [_to_float(a) for a in pmk],
        [_to_float(a) for a in lra],
        [_to_float(a) for a in lrm],
    ]
    z_norm = [_row_normalize_01(row) for row in z_raw]
    y_labels = [
        "Primas La Fe (mil Bs.)",
        "Primas mercado (mil Bs.)",
        "LR La Fe",
        "LR mercado",
    ]

    text_fmt: list[list[str]] = []
    for row_raw in z_raw:
        row_txt = []
        for v in row_raw:
            if math.isnan(v):
                row_txt.append("—")
            elif abs(v) >= 1000:
                row_txt.append(f"{v:,.0f}")
            elif abs(v) >= 1:
                row_txt.append(f"{v:.2f}")
            else:
                row_txt.append(f"{v:.4f}")
        text_fmt.append(row_txt)

    fig = go.Figure(
        data=go.Heatmap(
            z=z_norm,
            x=xs_s,
            y=y_labels,
            customdata=text_fmt,
            colorscale=[
                [0.0, "#f8fafc"],
                [0.35, "#e9d5ff"],
                [0.7, BRAND_PURPLE],
                [1.0, "#4c1d95"],
            ],
            zmin=0,
            zmax=1,
            colorbar=dict(
                title=dict(text="Norm. por fila", side="right"),
                tickvals=[0, 0.5, 1],
                ticktext=["mín", "medio", "máx"],
            ),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Período %{x}<br>"
                "Normalizado (fila): %{z:.2f}<br>"
                "Valor: %{customdata}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor=_PLOT_BG,
        font=_FONT,
        height=height,
        margin=dict(l=180, r=56, t=24, b=88),
        xaxis=dict(
            tickangle=-40,
            tickfont=dict(size=10, color="#64748b"),
            showgrid=False,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color="#334155"),
        ),
    )
    return fig
