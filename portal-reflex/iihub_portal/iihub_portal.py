"""Portal gerencial: KPIs (API) + enlaces a Admin y laboratorio Streamlit."""

from __future__ import annotations

import os
from typing import Any

import httpx
import reflex as rx
from plotly.graph_objects import Figure as PlotlyFigure

# Marca Seguros La Fe (alineado con Streamlit / Admin)
_BRAND_PURPLE = "#7029B3"
_BRAND_DEEP = "#5a1f94"
_BRAND_LAVENDER = "#8B5CF6"
_BRAND_MUTED = "#64748b"


class State(rx.State):
    """URLs de despliegue en state: se rellenan en el servidor con on_load (no en tiempo de build)."""

    admin_upload_url: str = "http://127.0.0.1:8080/admin/upload-policies/"
    admin_claims_upload_url: str = "http://127.0.0.1:8080/admin/upload-claims/"
    streamlit_lab_url: str = "http://127.0.0.1:8501"

    input_year: str = "2022"
    persistency: str = "—"
    active_n: str = "—"
    lapsed_n: str = "—"
    avg_premium: str = "—"
    tlr: str = "—"
    note: str = ""
    busy: bool = False

    market_plot_data: list[Any] = []
    market_plot_layout: dict[str, Any] = {}
    market_plot_ok: bool = False
    market_plot_error: str = ""

    market_ratio_plot_data: list[Any] = []
    market_ratio_plot_layout: dict[str, Any] = {}
    market_ratio_ok: bool = False

    snap_ok: bool = False
    snap_period: str = "—"
    snap_primas: str = "—"
    snap_sini: str = "—"
    snap_lr: str = "—"
    snap_cuota: str = "—"
    snap_comisiones: str = "—"
    snap_gadm: str = "—"
    snap_mk_lr: str = "—"

    @rx.var(cache=True, auto_deps=True)
    def market_plot_figure(self) -> PlotlyFigure:
        """Reflex 0.8 exige `Figure` en rx.plotly(data=...), no listas sueltas."""
        if not self.market_plot_ok or not self.market_plot_data:
            return PlotlyFigure()
        return PlotlyFigure(data=self.market_plot_data, layout=self.market_plot_layout or {})

    @rx.var(cache=True, auto_deps=True)
    def market_ratio_figure(self) -> PlotlyFigure:
        if not self.market_ratio_ok or not self.market_ratio_plot_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.market_ratio_plot_data,
            layout=self.market_ratio_plot_layout or {},
        )

    async def hydrate_urls(self):
        """Lee variables de entorno en runtime (Reflex Cloud / servidor)."""
        ab = os.environ.get("DJANGO_ADMIN_BASE_URL", "").strip().rstrip("/")
        if ab:
            self.admin_upload_url = f"{ab}/admin/upload-policies/"
            self.admin_claims_upload_url = f"{ab}/admin/upload-claims/"
        else:
            self.admin_upload_url = "http://127.0.0.1:8080/admin/upload-policies/"
            self.admin_claims_upload_url = "http://127.0.0.1:8080/admin/upload-claims/"

        sl = os.environ.get("STREAMLIT_LAB_URL", "").strip().rstrip("/")
        if sl:
            self.streamlit_lab_url = sl
        else:
            self.streamlit_lab_url = "http://127.0.0.1:8501"

    async def portal_on_load(self):
        await self.hydrate_urls()
        await self.load_sudeaseg_preview()
        await self.load_market_snapshot()

    async def load_sudeaseg_preview(self):
        self.market_plot_ok = False
        self.market_ratio_ok = False
        self.market_plot_error = ""
        self.market_plot_data = []
        self.market_plot_layout = {}
        self.market_ratio_plot_data = []
        self.market_ratio_plot_layout = {}
        base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
        fy = int(os.environ.get("MARKET_PREVIEW_FROM_YEAR", "2023"))
        ty = int(os.environ.get("MARKET_PREVIEW_TO_YEAR", "2026"))
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                r1 = await client.get(
                    f"{base}/api/v1/market/la-fe/resumen-series",
                    params={"from_year": fy, "to_year": ty, "mode": "monthly_flow"},
                )
                r2 = await client.get(
                    f"{base}/api/v1/market/resumen/totals-series",
                    params={"from_year": fy, "to_year": ty, "mode": "monthly_flow"},
                )
                r1.raise_for_status()
                r2.raise_for_status()
        except Exception as e:  # noqa: BLE001
            self.market_plot_error = f"No se pudo cargar la referencia de mercado. ({e})"
            return

        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        la = r1.json().get("points") or []
        tot = r2.json().get("points") or []

        def primas_map(rows: list[dict[str, Any]]) -> dict[tuple[int, int], float | None]:
            out: dict[tuple[int, int], float | None] = {}
            for row in rows:
                key = (int(row["period_year"]), int(row["period_month"]))
                out[key] = row.get("primas_netas_thousands_bs")
            return out

        m1 = primas_map(la)
        m2 = primas_map(tot)
        keys = sorted(set(m1.keys()) | set(m2.keys()))
        if not keys:
            self.market_plot_error = "Sin puntos de mercado en el rango configurado."
            return

        xs = [f"{y}-{m:02d}" for y, m in keys]
        y_la = [m1.get(k) for k in keys]
        y_tot = [m2.get(k) for k in keys]

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=y_la,
                name="La Fe (eje izq.)",
                mode="lines+markers",
                line={"color": _BRAND_PURPLE},
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=y_tot,
                name="Mercado total (eje der.)",
                mode="lines+markers",
                line={"color": "#0284c7"},
            ),
            secondary_y=True,
        )
        fig.update_xaxes(title_text="Período")
        fig.update_yaxes(title_text="La Fe · miles de Bs.", secondary_y=False)
        fig.update_yaxes(title_text="Mercado total · miles de Bs.", secondary_y=True)
        fig.update_layout(
            height=360,
            margin=dict(l=24, r=56, t=40, b=24),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )
        pj = fig.to_plotly_json()
        self.market_plot_data = pj["data"]
        self.market_plot_layout = pj.get("layout") or {}
        self.market_plot_ok = True

        def lr_map(rows: list[dict[str, Any]]) -> dict[tuple[int, int], float | None]:
            out: dict[tuple[int, int], float | None] = {}
            for row in rows:
                key = (int(row["period_year"]), int(row["period_month"]))
                vlr = row.get("loss_ratio_proxy")
                out[key] = float(vlr) if vlr is not None else None
            return out

        lr1 = lr_map(la)
        lr2 = lr_map(tot)
        y_lr_la = [lr1.get(k) for k in keys]
        y_lr_mk = [lr2.get(k) for k in keys]
        fig_r = go.Figure()
        fig_r.add_trace(
            go.Scatter(
                x=xs,
                y=y_lr_la,
                name="Loss ratio La Fe (siniestros/primas)",
                mode="lines+markers",
                line={"color": _BRAND_PURPLE},
            ),
        )
        fig_r.add_trace(
            go.Scatter(
                x=xs,
                y=y_lr_mk,
                name="Loss ratio mercado",
                mode="lines+markers",
                line={"color": "#0284c7"},
            ),
        )
        fig_r.update_layout(
            height=300,
            margin=dict(l=24, r=24, t=40, b=24),
            yaxis_title="Ratio (fracción)",
            xaxis_title="Período",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )
        pjr = fig_r.to_plotly_json()
        self.market_ratio_plot_data = pjr["data"]
        self.market_ratio_plot_layout = pjr.get("layout") or {}
        self.market_ratio_ok = True

    async def load_market_snapshot(self):
        self.snap_ok = False
        self.snap_period = "—"
        self.snap_primas = "—"
        self.snap_sini = "—"
        self.snap_lr = "—"
        self.snap_cuota = "—"
        self.snap_comisiones = "—"
        self.snap_gadm = "—"
        self.snap_mk_lr = "—"
        base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.get(f"{base}/api/v1/market/la-fe/snapshot-latest")
                if r.status_code == 404:
                    return
                r.raise_for_status()
                d = r.json()
        except Exception:  # noqa: BLE001
            return
        py, pm = int(d["period_year"]), int(d["period_month"])
        self.snap_period = f"{py}-{pm:02d}"
        lf = d.get("la_fe") or {}
        mk = d.get("mercado_total") or {}

        def fmt_num(x: object) -> str:
            if x is None:
                return "—"
            try:
                return f"{float(x):,.2f}"
            except (TypeError, ValueError):
                return "—"

        def fmt_pct_ratio(x: object) -> str:
            if x is None:
                return "—"
            try:
                return f"{float(x) * 100:.2f} %"
            except (TypeError, ValueError):
                return "—"

        self.snap_primas = fmt_num(lf.get("primas_ytd"))
        self.snap_sini = fmt_num(lf.get("siniestros_totales_ytd"))
        self.snap_lr = fmt_pct_ratio(lf.get("loss_ratio_ytd"))
        cq = d.get("cuota_mercado_primas_pct")
        self.snap_cuota = f"{float(cq):.3f} %" if cq is not None else "—"
        self.snap_comisiones = fmt_num(lf.get("comisiones_ytd"))
        self.snap_gadm = fmt_num(lf.get("gastos_admin_ytd"))
        self.snap_mk_lr = fmt_pct_ratio(mk.get("loss_ratio_ytd"))
        self.snap_ok = True

    def set_input_year(self, v: str):
        self.input_year = v

    async def load_kpi(self):
        self.busy = True
        yield
        try:
            year = int(self.input_year.strip())
        except ValueError:
            self.note = "Indica un año válido."
            self.busy = False
            return
        base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                r = await client.get(
                    f"{base}/api/v1/kpi/summary",
                    params={"cohort_year": year, "use_db": "true"},
                )
                r.raise_for_status()
                d = r.json()
            self.persistency = f"{float(d['persistency_rate_pct']):.2f} %"
            self.active_n = f"{int(d['policies_active']):,}"
            self.lapsed_n = f"{int(d['policies_lapsed']):,}"
            self.avg_premium = f"{float(d['avg_annual_premium']):,.2f}"
            t = d.get("technical_loss_ratio_pct")
            self.tlr = f"{float(t):.2f} %" if t is not None else "—"
            self.note = str(d.get("data_note", ""))
        except Exception as e:  # noqa: BLE001
            self.note = f"No se pudieron cargar los indicadores. Intente de nuevo en unos minutos. ({e})"
        self.busy = False


def _shell_header() -> rx.Component:
    """Barra superior fija: logo grande + acciones (plantilla tipo aplicación)."""
    return rx.box(
        rx.box(
            rx.hstack(
                rx.image(
                    src="/logo-fe-1.jpg",
                    alt="Seguros La Fe",
                    height="88px",
                    width="auto",
                    style={"max_width": "min(100%, 320px)", "object_fit": "contain"},
                ),
                rx.spacer(),
                rx.hstack(
                    rx.link(
                        rx.button(
                            "Carga de pólizas",
                            size="3",
                            color_scheme="purple",
                        ),
                        href=State.admin_upload_url,
                        is_external=True,
                    ),
                    rx.link(
                        rx.button(
                            "Carga de siniestros",
                            size="3",
                            color_scheme="purple",
                            variant="outline",
                        ),
                        href=State.admin_claims_upload_url,
                        is_external=True,
                    ),
                    rx.link(
                        rx.button(
                            "Laboratorio analítico",
                            size="3",
                            color_scheme="purple",
                            variant="outline",
                        ),
                        href=State.streamlit_lab_url,
                        is_external=True,
                    ),
                    spacing="3",
                    align_items="center",
                    flex_wrap="wrap",
                ),
                spacing="4",
                align_items="center",
                width="100%",
                flex_wrap="wrap",
            ),
            width="100%",
            max_width="1200px",
            margin_x="auto",
            padding_x="6",
            padding_y="4",
        ),
        width="100%",
        style={
            "background": "linear-gradient(180deg, #ffffff 0%, #faf5ff 100%)",
            "border_bottom": "1px solid var(--gray-5)",
            "box_shadow": "0 4px 24px rgba(88, 28, 135, 0.08)",
        },
    )


def _hero_strip() -> rx.Component:
    """Franja de marca bajo el header (sin duplicar el logo)."""
    return rx.box(
        rx.box(
            rx.vstack(
                rx.heading(
                    "Insurance Intelligence Hub",
                    size="7",
                    style={"color": "white", "margin": 0},
                ),
                rx.text(
                    "Seguros La Fe · Indicadores de cohorte y accesos operativos",
                    size="3",
                    style={"color": "rgba(255,255,255,0.9)"},
                ),
                spacing="2",
                align_items="start",
                width="100%",
            ),
            width="100%",
            max_width="1200px",
            margin_x="auto",
            padding_x="6",
            padding_y="5",
        ),
        width="100%",
        style={
            "background": f"linear-gradient(115deg, {_BRAND_DEEP} 0%, {_BRAND_PURPLE} 45%, {_BRAND_LAVENDER} 100%)",
        },
    )


def _kpi_card(title: str, value: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(title, size="2", weight="bold", color="gray"),
            rx.heading(value, size="6", style={"color": _BRAND_DEEP}),
            spacing="1",
            align_items="start",
            width="100%",
        ),
        style={
            "border": "1px solid var(--gray-6)",
            "box_shadow": "0 4px 16px rgba(15, 23, 42, 0.06)",
            "min_height": "118px",
        },
        width="100%",
    )


def index() -> rx.Component:
    return rx.fragment(
        rx.box(
            rx.color_mode.button(position="top-right"),
            _shell_header(),
            _hero_strip(),
            rx.box(
                rx.container(
                    rx.vstack(
                        rx.heading("Referencia de mercado (SUDEASEG)", size="5", style={"color": _BRAND_DEEP}),
                        rx.text(
                            "Último cierre con dato La Fe (YTD miles de Bs.; ratios como fracción). Laboratorio Streamlit: series completas y CSV.",
                            size="2",
                            color="gray",
                        ),
                        rx.cond(
                            State.snap_ok,
                            rx.grid(
                                _kpi_card("Cierre", State.snap_period),
                                _kpi_card("Primas YTD La Fe", State.snap_primas),
                                _kpi_card("Siniestros tot. La Fe", State.snap_sini),
                                _kpi_card("Loss ratio La Fe", State.snap_lr),
                                _kpi_card("Cuota primas", State.snap_cuota),
                                _kpi_card("Comisiones YTD", State.snap_comisiones),
                                _kpi_card("Gasto adm. YTD", State.snap_gadm),
                                _kpi_card("Loss ratio mercado", State.snap_mk_lr),
                                columns="4",
                                spacing="3",
                                width="100%",
                            ),
                        ),
                        rx.text(
                            "Primas netas mensuales (miles de Bs.): La Fe (eje izquierdo) y total del sector (eje derecho).",
                            size="2",
                            color="gray",
                            style={"marginTop": "0.75rem"},
                        ),
                        rx.cond(
                            State.market_plot_ok,
                            rx.plotly(data=State.market_plot_figure),
                        ),
                        rx.cond(
                            State.market_ratio_ok,
                            rx.plotly(data=State.market_ratio_figure),
                        ),
                        rx.cond(
                            State.market_plot_error != "",
                            rx.callout(
                                State.market_plot_error,
                                icon="triangle_alert",
                                color_scheme="red",
                                width="100%",
                            ),
                        ),
                        rx.heading("Resumen de cohorte", size="5", style={"color": _BRAND_DEEP}),
                        rx.hstack(
                            rx.text("Año:", weight="medium", color=_BRAND_MUTED),
                            rx.input(
                                value=State.input_year,
                                on_change=State.set_input_year,
                                width="100px",
                            ),
                            rx.button(
                                "Actualizar indicadores",
                                on_click=State.load_kpi,
                                loading=State.busy,
                                color_scheme="purple",
                            ),
                            spacing="3",
                            align_items="center",
                            flex_wrap="wrap",
                        ),
                        rx.grid(
                            _kpi_card("Persistencia", State.persistency),
                            _kpi_card("Pólizas activas", State.active_n),
                            _kpi_card("Lapsos", State.lapsed_n),
                            _kpi_card("Prima media", State.avg_premium),
                            _kpi_card("Ratio técnico (demo)", State.tlr),
                            columns="5",
                            spacing="3",
                            width="100%",
                        ),
                        rx.cond(
                            State.note != "",
                            rx.callout(
                                State.note,
                                icon="info",
                                color_scheme="blue",
                                width="100%",
                            ),
                        ),
                        rx.text(
                            "Seguros La Fe · RIF J-000467382 · Inscrita en la SUDEASEG bajo el N.º 62",
                            size="1",
                            color="gray",
                            text_align="center",
                            width="100%",
                        ),
                        spacing="5",
                        width="100%",
                        padding_y="8",
                        padding_x="2",
                    ),
                    size="4",
                ),
                width="100%",
                min_height="50vh",
                style={"background": "var(--gray-2)"},
            ),
            min_height="100vh",
        ),
    )


app = rx.App()
app.add_page(index, on_load=State.portal_on_load)
