"""Figuras Plotly avanzadas a partir del payload `/api/v1/kpi/cohort-portfolio`."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
from plotly.graph_objs import Figure

from iihub_portal.theme import BRAND_PURPLE, MARKET_BLUE

_FONT = dict(family="Inter, system-ui, sans-serif", size=12, color="#334155")
_EMPTY = dict(template="plotly_white", paper_bgcolor="rgba(255,255,255,0)", font=_FONT, height=260)


def _empty_fig(msg: str) -> Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=msg,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=13, color="#64748b"),
    )
    fig.update_layout(**_EMPTY, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


def _pj(fig: Figure) -> tuple[list[Any], dict[str, Any]]:
    j = fig.to_plotly_json()
    return j["data"], j.get("layout") or {}


def build_sunburst(rows: list[dict[str, Any]]) -> tuple[list[Any], dict[str, Any]]:
    if not rows:
        return _pj(_empty_fig("Sin desglose edad × estado"))
    ids: list[str] = []
    labels: list[str] = []
    parents: list[str] = []
    values: list[int] = []
    total = sum(int(r.get("n") or 0) for r in rows)
    ids.append("root")
    labels.append("Cartera")
    parents.append("")
    values.append(total)

    by_status: dict[str, int] = {}
    for r in rows:
        st = str(r.get("status") or "?")
        by_status[st] = by_status.get(st, 0) + int(r.get("n") or 0)

    for st, v in sorted(by_status.items()):
        sid = f"st_{st}"
        ids.append(sid)
        labels.append(st)
        parents.append("root")
        values.append(v)

    for r in rows:
        st = str(r.get("status") or "?")
        ab = str(r.get("age_band") or "?")
        aid = f"{st}|{ab}"
        ids.append(aid)
        labels.append(ab)
        parents.append(f"st_{st}")
        values.append(int(r.get("n") or 0))

    fig = go.Figure(
        go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(line=dict(width=1, color="white")),
            hovertemplate="<b>%{label}</b><br>pólizas: %{value}<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        font=_FONT,
        height=380,
        margin=dict(l=8, r=8, t=24, b=8),
    )
    return _pj(fig)


def build_treemap(rows: list[dict[str, Any]]) -> tuple[list[Any], dict[str, Any]]:
    if not rows:
        return _pj(_empty_fig("Sin datos para treemap"))
    ids: list[str] = []
    labels: list[str] = []
    parents: list[str] = []
    values: list[int] = []
    total = sum(int(r.get("n") or 0) for r in rows)
    ids.append("root")
    labels.append("Cartera")
    parents.append("")
    values.append(total)
    by_status: dict[str, int] = {}
    for r in rows:
        st = str(r.get("status") or "?")
        by_status[st] = by_status.get(st, 0) + int(r.get("n") or 0)
    for st, v in sorted(by_status.items()):
        sid = f"st_{st}"
        ids.append(sid)
        labels.append(st)
        parents.append("root")
        values.append(v)
    for r in rows:
        st = str(r.get("status") or "?")
        ab = str(r.get("age_band") or "?")
        aid = f"{st}|{ab}"
        ids.append(aid)
        labels.append(ab)
        parents.append(f"st_{st}")
        values.append(int(r.get("n") or 0))

    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colorscale=[[0, "#f5f3ff"], [1, BRAND_PURPLE]], line=dict(width=1, color="white")),
            hovertemplate="<b>%{label}</b><br>pólizas: %{value}<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        font=_FONT,
        height=380,
        margin=dict(l=8, r=8, t=24, b=8),
    )
    return _pj(fig)


def build_waterfall(issue_by_month: list[dict[str, Any]]) -> tuple[list[Any], dict[str, Any]]:
    if not issue_by_month:
        return _pj(_empty_fig("Sin emisión mensual en BD"))
    rows = sorted(issue_by_month, key=lambda x: str(x.get("month") or ""))
    x = [str(r.get("month")) for r in rows]
    y = [float(r.get("premium_sum") or 0) for r in rows]
    measure = ["relative"] * len(y)

    fig = go.Figure(
        go.Waterfall(
            name="Prima",
            orientation="v",
            measure=measure,
            x=x,
            y=y,
            connector=dict(line=dict(color="#cbd5e1", width=1)),
            increasing=dict(marker=dict(color=BRAND_PURPLE)),
            decreasing=dict(marker=dict(color="#94a3b8")),
            totals=dict(marker=dict(color="#4c1d95")),
            text=[f"{v:,.0f}" for v in y],
            textposition="outside",
            hovertemplate="%{x}<br>Prima: %{y:,.2f} Bs.<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#f8fafc",
        font=_FONT,
        height=360,
        margin=dict(l=48, r=24, t=28, b=72),
        xaxis=dict(tickangle=-35, title="Mes emisión"),
        yaxis=dict(title="Prima anual emitida (Bs.)", gridcolor="#e2e8f0"),
        showlegend=False,
    )
    return _pj(fig)


def build_sankey(
    total_premium: float,
    total_paid: float,
) -> tuple[list[Any], dict[str, Any]]:
    tp = max(0.0, float(total_premium or 0))
    paid = max(0.0, float(total_paid or 0))
    residual = max(0.0, tp - paid)
    if tp <= 0 and paid <= 0:
        return _pj(_empty_fig("Sin prima ni pagos para flujo"))

    labels = ["Prima emitida (anual)", "Pagado siniestros", "No liquidado como siniestro"]
    src = [0, 0]
    tgt = [1, 2]
    val = [min(paid, tp) if tp > 0 else paid, residual]
    if val[0] <= 0 and val[1] <= 0:
        return _pj(_empty_fig("Flujo nulo"))

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=20,
                    thickness=14,
                    line=dict(color="white", width=0.6),
                    label=labels,
                    color=["#ede9fe", "#bae6fd", "#f1f5f9"],
                ),
                link=dict(source=src, target=tgt, value=val, color=["rgba(112,41,179,0.35)", "rgba(148,163,184,0.35)"]),
            )
        ]
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        font=_FONT,
        height=320,
        margin=dict(l=24, r=24, t=28, b=16),
    )
    return _pj(fig)


def build_stacked_100(rows: list[dict[str, Any]]) -> tuple[list[Any], dict[str, Any]]:
    if not rows:
        return _pj(_empty_fig("Sin datos para barras"))
    age_bands: list[str] = []
    seen: set[str] = set()
    for r in rows:
        ab = str(r.get("age_band") or "?")
        if ab not in seen:
            seen.add(ab)
            age_bands.append(ab)
    statuses: list[str] = []
    seen_s: set[str] = set()
    for r in rows:
        st = str(r.get("status") or "?")
        if st not in seen_s:
            seen_s.add(st)
            statuses.append(st)

    mat: dict[tuple[str, str], int] = {}
    for r in rows:
        mat[(str(r.get("age_band")), str(r.get("status")))] = int(r.get("n") or 0)

    colors = [BRAND_PURPLE, MARKET_BLUE, "#94a3b8", "#f59e0b", "#10b981"]
    fig = go.Figure()
    for i, st in enumerate(statuses):
        raw = [mat.get((ab, st), 0) for ab in age_bands]
        row_sum = [sum(mat.get((ab, s), 0) for s in statuses) for ab in age_bands]
        pct = [(raw[j] / row_sum[j] * 100.0) if row_sum[j] > 0 else 0.0 for j in range(len(age_bands))]
        fig.add_trace(
            go.Bar(
                name=st,
                x=age_bands,
                y=pct,
                marker=dict(color=colors[i % len(colors)], line=dict(width=0)),
                hovertemplate=f"<b>{st}</b><br>%{{x}}<br>%{{y:.1f}} %<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="stack",
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#f8fafc",
        font=_FONT,
        height=360,
        margin=dict(l=48, r=24, t=28, b=56),
        yaxis=dict(title="Porcentaje (100% por tramo de edad)", range=[0, 100], gridcolor="#e2e8f0"),
        xaxis=dict(title="Edad al emitir", tickangle=-25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return _pj(fig)


def build_violin_age(box_samples: dict[str, list[float]]) -> tuple[list[Any], dict[str, Any]]:
    if not box_samples:
        return _pj(_empty_fig("Sin muestras de prima por tramo"))
    fig = go.Figure()
    colors = ["#7c3aed", "#0284c7", "#0d9488", "#ea580c", "#be185d"]
    for i, (band, ys) in enumerate(sorted(box_samples.items())):
        if not ys:
            continue
        fig.add_trace(
            go.Violin(
                y=ys,
                name=band,
                box_visible=True,
                meanline_visible=True,
                fillcolor=colors[i % len(colors)],
                opacity=0.65,
                line=dict(color="#334155", width=1),
                hovertemplate=f"<b>{band}</b><br>prima: %{{y:,.2f}}<extra></extra>",
            )
        )
    if not fig.data:
        return _pj(_empty_fig("Sin muestras de prima por tramo"))
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#f8fafc",
        font=_FONT,
        height=380,
        margin=dict(l=56, r=24, t=28, b=48),
        yaxis=dict(title="Prima anual (Bs.)", gridcolor="#e2e8f0"),
        xaxis=dict(title="Tramo de edad"),
        violingap=0.25,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
    )
    return _pj(fig)


def build_box_status(box_samples: dict[str, list[float]]) -> tuple[list[Any], dict[str, Any]]:
    if not box_samples:
        return _pj(_empty_fig("Sin muestras por estado"))
    fig = go.Figure()
    colors = [BRAND_PURPLE, MARKET_BLUE, "#64748b"]
    for i, (st, ys) in enumerate(sorted(box_samples.items())):
        if not ys:
            continue
        fig.add_trace(
            go.Box(
                y=ys,
                name=st,
                marker_color=colors[i % len(colors)],
                boxmean="sd",
                hovertemplate=f"<b>{st}</b><br>prima: %{{y:,.2f}}<extra></extra>",
            )
        )
    if not fig.data:
        return _pj(_empty_fig("Sin muestras por estado"))
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="#f8fafc",
        font=_FONT,
        height=360,
        margin=dict(l=56, r=24, t=28, b=48),
        yaxis=dict(title="Prima anual (Bs.)", gridcolor="#e2e8f0"),
        xaxis=dict(title="Estado póliza"),
        showlegend=False,
    )
    return _pj(fig)


def build_all_portfolio_figures(payload: dict[str, Any]) -> dict[str, tuple[list[Any], dict[str, Any]]]:
    rows = list(payload.get("sunburst_age_status") or [])
    issue = list(payload.get("issue_by_month") or [])
    tp = float(payload.get("total_annual_premium") or 0)
    paid = float(payload.get("total_paid_claims") or 0)
    samples_age = dict(payload.get("box_samples_age_band") or {})
    samples_st = dict(payload.get("box_samples_status") or {})

    return {
        "sunburst": build_sunburst(rows),
        "treemap": build_treemap(rows),
        "waterfall": build_waterfall(issue),
        "sankey": build_sankey(tp, paid),
        "stacked": build_stacked_100(rows),
        "violin_age": build_violin_age(samples_age),
        "box_status": build_box_status(samples_st),
    }
