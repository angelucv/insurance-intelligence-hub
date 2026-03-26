"""Estado del portal: URLs, KPIs y gráficos de mercado."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx
import plotly.graph_objects as go
import reflex as rx
from plotly.graph_objects import Figure as PlotlyFigure

from iihub_portal.portfolio_plotly import build_all_portfolio_figures
from iihub_portal.plotly_charts import (
    build_cartera_donut_figure,
    build_kpi_gauge_figure,
    build_market_metrics_heatmap,
    build_yoy_lr_compare_figure,
    build_yoy_mercado_figure,
    build_yoy_primas_figure,
    polish_market_subplots,
    polish_ratio_figure,
    trace_lr_la_fe,
    trace_lr_mercado,
    trace_primas_la_fe,
    trace_primas_mercado,
)


class State(rx.State):
    """URLs de despliegue en state: se rellenan en el servidor con on_load (no en tiempo de build)."""

    admin_upload_url: str = "http://127.0.0.1:8080/admin/upload-policies/"
    admin_claims_upload_url: str = "http://127.0.0.1:8080/admin/upload-claims/"
    streamlit_lab_url: str = "http://127.0.0.1:8501"

    input_year: str = "2025"
    input_month: str = "01"
    persistency: str = "—"
    active_n: str = "—"
    lapsed_n: str = "—"
    avg_premium: str = "—"
    tlr: str = "—"
    note: str = ""
    busy: bool = False
    market_charts_busy: bool = False

    ui_main_tab: str = "cartera"
    market_fy: str = "2023"
    market_ty: str = "2026"
    market_mode: str = "monthly_flow"
    market_yoy_a: str = "2023"
    market_yoy_b: str = "2024"
    show_snap_more: bool = False

    market_plot_data: list[Any] = []
    market_plot_layout: dict[str, Any] = {}
    market_plot_ok: bool = False
    market_plot_error: str = ""

    market_ratio_plot_data: list[Any] = []
    market_ratio_plot_layout: dict[str, Any] = {}
    market_ratio_ok: bool = False

    kpi_gauge_data: list[Any] = []
    kpi_gauge_layout: dict[str, Any] = {}
    kpi_gauge_ok: bool = False

    cartera_donut_data: list[Any] = []
    cartera_donut_layout: dict[str, Any] = {}
    cartera_donut_ok: bool = False

    portfolio_viz_ok: bool = False
    portfolio_note: str = ""
    portfolio_bundle: dict[str, Any] = {}

    market_heatmap_data: list[Any] = []
    market_heatmap_layout: dict[str, Any] = {}
    market_heatmap_ok: bool = False

    market_yoy_la_data: list[Any] = []
    market_yoy_la_layout: dict[str, Any] = {}
    market_yoy_la_ok: bool = False
    market_yoy_mk_data: list[Any] = []
    market_yoy_mk_layout: dict[str, Any] = {}
    market_yoy_mk_ok: bool = False
    market_yoy_lr_data: list[Any] = []
    market_yoy_lr_layout: dict[str, Any] = {}
    market_yoy_lr_ok: bool = False

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

    @rx.var(cache=True, auto_deps=True)
    def kpi_gauge_figure(self) -> PlotlyFigure:
        if not self.kpi_gauge_ok or not self.kpi_gauge_data:
            return PlotlyFigure()
        return PlotlyFigure(data=self.kpi_gauge_data, layout=self.kpi_gauge_layout or {})

    @rx.var(cache=True, auto_deps=True)
    def cartera_donut_figure(self) -> PlotlyFigure:
        if not self.cartera_donut_ok or not self.cartera_donut_data:
            return PlotlyFigure()
        return PlotlyFigure(data=self.cartera_donut_data, layout=self.cartera_donut_layout or {})

    @rx.var(cache=True, auto_deps=True)
    def market_heatmap_figure(self) -> PlotlyFigure:
        if not self.market_heatmap_ok or not self.market_heatmap_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.market_heatmap_data,
            layout=self.market_heatmap_layout or {},
        )

    @rx.var(cache=True, auto_deps=True)
    def market_yoy_la_figure(self) -> PlotlyFigure:
        if not self.market_yoy_la_ok or not self.market_yoy_la_data:
            return PlotlyFigure()
        return PlotlyFigure(data=self.market_yoy_la_data, layout=self.market_yoy_la_layout or {})

    @rx.var(cache=True, auto_deps=True)
    def market_yoy_mk_figure(self) -> PlotlyFigure:
        if not self.market_yoy_mk_ok or not self.market_yoy_mk_data:
            return PlotlyFigure()
        return PlotlyFigure(data=self.market_yoy_mk_data, layout=self.market_yoy_mk_layout or {})

    @rx.var(cache=True, auto_deps=True)
    def market_yoy_lr_figure(self) -> PlotlyFigure:
        if not self.market_yoy_lr_ok or not self.market_yoy_lr_data:
            return PlotlyFigure()
        return PlotlyFigure(data=self.market_yoy_lr_data, layout=self.market_yoy_lr_layout or {})

    @rx.var(cache=True, auto_deps=True)
    def cartera_period_label(self) -> str:
        y = (self.input_year or "").strip() or "—"
        m = (self.input_month or "").strip() or "—"
        if m.isdigit() and len(m) == 1:
            m = f"0{m}"
        return f"{y}-{m}"

    def _portfolio_figure(self, key: str) -> PlotlyFigure:
        b = (self.portfolio_bundle or {}).get(key)
        if not b or not b.get("data"):
            return PlotlyFigure()
        return PlotlyFigure(data=b["data"], layout=b.get("layout") or {})

    @rx.var(cache=True, auto_deps=True)
    def portfolio_sunburst_figure(self) -> PlotlyFigure:
        return self._portfolio_figure("sunburst")

    @rx.var(cache=True, auto_deps=True)
    def portfolio_treemap_figure(self) -> PlotlyFigure:
        return self._portfolio_figure("treemap")

    @rx.var(cache=True, auto_deps=True)
    def portfolio_waterfall_figure(self) -> PlotlyFigure:
        return self._portfolio_figure("waterfall")

    @rx.var(cache=True, auto_deps=True)
    def portfolio_sankey_figure(self) -> PlotlyFigure:
        return self._portfolio_figure("sankey")

    @rx.var(cache=True, auto_deps=True)
    def portfolio_stacked_figure(self) -> PlotlyFigure:
        return self._portfolio_figure("stacked")

    @rx.var(cache=True, auto_deps=True)
    def portfolio_violin_age_figure(self) -> PlotlyFigure:
        return self._portfolio_figure("violin_age")

    @rx.var(cache=True, auto_deps=True)
    def portfolio_box_status_figure(self) -> PlotlyFigure:
        return self._portfolio_figure("box_status")

    async def hydrate_urls(self):
        """Lee variables de entorno en runtime (Reflex Cloud / servidor)."""
        from datetime import datetime

        now = datetime.now()
        self.input_year = str(now.year)
        self.input_month = f"{now.month:02d}"

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

        fy = os.environ.get("MARKET_PREVIEW_FROM_YEAR", "").strip()
        ty = os.environ.get("MARKET_PREVIEW_TO_YEAR", "").strip()
        if fy.isdigit():
            self.market_fy = fy
        if ty.isdigit():
            self.market_ty = ty
        self._ensure_market_desde_le_hasta()

    async def portal_on_load(self):
        await self.hydrate_urls()
        await asyncio.gather(
            self.load_sudeaseg_preview(),
            self.load_market_snapshot(),
            self.load_kpi(),
        )

    async def load_sudeaseg_preview(self):
        self.market_plot_ok = False
        self.market_ratio_ok = False
        self.market_plot_error = ""
        self.market_plot_data = []
        self.market_plot_layout = {}
        self.market_ratio_plot_data = []
        self.market_ratio_plot_layout = {}
        self.market_heatmap_ok = False
        self.market_heatmap_data = []
        self.market_heatmap_layout = {}
        self.market_yoy_la_ok = False
        self.market_yoy_la_data = []
        self.market_yoy_la_layout = {}
        self.market_yoy_mk_ok = False
        self.market_yoy_mk_data = []
        self.market_yoy_mk_layout = {}
        self.market_yoy_lr_ok = False
        self.market_yoy_lr_data = []
        self.market_yoy_lr_layout = {}
        self.market_charts_busy = True
        try:
            base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
            try:
                fy = int(self.market_fy.strip())
                ty = int(self.market_ty.strip())
                yoy_a = int(self.market_yoy_a.strip())
                yoy_b = int(self.market_yoy_b.strip())
            except ValueError:
                self.market_plot_error = "Indique años válidos (desde / hasta y comparativa)."
                return
            if fy > ty:
                self.market_ty = str(fy)
                ty = fy
            mode = (self.market_mode or "monthly_flow").strip()
            if mode not in ("monthly_flow", "ytd"):
                mode = "monthly_flow"
            params = {"from_year": fy, "to_year": ty, "mode": mode}
            rla1 = rla2 = rt1 = rt2 = None
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    if yoy_a != yoy_b:
                        py1 = {"from_year": yoy_a, "to_year": yoy_a, "mode": mode}
                        py2 = {"from_year": yoy_b, "to_year": yoy_b, "mode": mode}
                        r1, r2, rla1, rla2, rt1, rt2 = await asyncio.gather(
                            client.get(f"{base}/api/v1/market/la-fe/resumen-series", params=params),
                            client.get(f"{base}/api/v1/market/resumen/totals-series", params=params),
                            client.get(f"{base}/api/v1/market/la-fe/resumen-series", params=py1),
                            client.get(f"{base}/api/v1/market/la-fe/resumen-series", params=py2),
                            client.get(f"{base}/api/v1/market/resumen/totals-series", params=py1),
                            client.get(f"{base}/api/v1/market/resumen/totals-series", params=py2),
                        )
                    else:
                        r1, r2 = await asyncio.gather(
                            client.get(f"{base}/api/v1/market/la-fe/resumen-series", params=params),
                            client.get(f"{base}/api/v1/market/resumen/totals-series", params=params),
                        )
                    r1.raise_for_status()
                    r2.raise_for_status()
            except Exception as e:  # noqa: BLE001
                self.market_plot_error = f"No se pudo cargar la referencia de mercado. ({e})"
                return

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
            fig.add_trace(trace_primas_la_fe(xs, y_la), secondary_y=False)
            fig.add_trace(trace_primas_mercado(xs, y_tot), secondary_y=True)
            fig.update_xaxes(title_text="Período")
            fig.update_yaxes(title_text="La Fe · miles de Bs.", secondary_y=False)
            fig.update_yaxes(title_text="Mercado total · miles de Bs.", secondary_y=True)
            polish_market_subplots(fig, height=360)
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
            fig_r.add_trace(trace_lr_la_fe(xs, y_lr_la))
            fig_r.add_trace(trace_lr_mercado(xs, y_lr_mk))
            fig_r.update_layout(yaxis_title="Ratio (fracción)", xaxis_title="Período")
            polish_ratio_figure(fig_r, height=300)
            pjr = fig_r.to_plotly_json()
            self.market_ratio_plot_data = pjr["data"]
            self.market_ratio_plot_layout = pjr.get("layout") or {}
            self.market_ratio_ok = True

            hm = build_market_metrics_heatmap(
                xs,
                y_la,
                y_tot,
                y_lr_la,
                y_lr_mk,
                height=420,
                max_points=48,
            )
            hmj = hm.to_plotly_json()
            self.market_heatmap_data = hmj["data"]
            self.market_heatmap_layout = hmj.get("layout") or {}
            self.market_heatmap_ok = True

            if yoy_a != yoy_b and rla1 is not None and rla2 is not None and rt1 is not None and rt2 is not None:
                try:
                    rla1.raise_for_status()
                    rla2.raise_for_status()
                    rt1.raise_for_status()
                    rt2.raise_for_status()
                    la_y1 = rla1.json().get("points") or []
                    la_y2 = rla2.json().get("points") or []
                    tot_y1 = rt1.json().get("points") or []
                    tot_y2 = rt2.json().get("points") or []
                    f_la = build_yoy_primas_figure(yoy_a, yoy_b, la_y1, la_y2, height=320)
                    pj_la = f_la.to_plotly_json()
                    self.market_yoy_la_data = pj_la["data"]
                    self.market_yoy_la_layout = pj_la.get("layout") or {}
                    self.market_yoy_la_ok = True

                    f_mk = build_yoy_mercado_figure(yoy_a, yoy_b, tot_y1, tot_y2, height=320)
                    pj_mk = f_mk.to_plotly_json()
                    self.market_yoy_mk_data = pj_mk["data"]
                    self.market_yoy_mk_layout = pj_mk.get("layout") or {}
                    self.market_yoy_mk_ok = True

                    f_lr = build_yoy_lr_compare_figure(yoy_a, yoy_b, la_y1, la_y2, height=280)
                    pj_lr = f_lr.to_plotly_json()
                    self.market_yoy_lr_data = pj_lr["data"]
                    self.market_yoy_lr_layout = pj_lr.get("layout") or {}
                    self.market_yoy_lr_ok = True
                except Exception:  # noqa: BLE001
                    pass
        finally:
            self.market_charts_busy = False

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

    def set_input_month(self, v: str):
        self.input_month = v

    def _ensure_market_desde_le_hasta(self) -> None:
        """Garantiza Desde (market_fy) ≤ Hasta (market_ty) en el estado del cliente."""
        try:
            fy = int((self.market_fy or "0").strip())
            ty = int((self.market_ty or "0").strip())
        except ValueError:
            return
        if fy > ty:
            self.market_ty = str(fy)

    def set_market_fy(self, v: str):
        self.market_fy = v
        self._ensure_market_desde_le_hasta()

    def set_market_ty(self, v: str):
        self.market_ty = v
        try:
            fy = int((self.market_fy or "0").strip())
            ty = int((self.market_ty or "0").strip())
        except ValueError:
            return
        if fy > ty:
            self.market_fy = str(ty)

    def set_market_mode(self, v: str):
        self.market_mode = v

    def set_market_yoy_a(self, v: str):
        self.market_yoy_a = v

    def set_market_yoy_b(self, v: str):
        self.market_yoy_b = v

    def pick_tab_mercado(self):
        self.ui_main_tab = "mercado"

    def pick_tab_cartera(self):
        self.ui_main_tab = "cartera"

    def toggle_snap_more(self):
        self.show_snap_more = not self.show_snap_more

    async def load_kpi(self):
        self.busy = True
        self.kpi_gauge_ok = False
        self.kpi_gauge_data = []
        self.kpi_gauge_layout = {}
        self.cartera_donut_ok = False
        self.cartera_donut_data = []
        self.cartera_donut_layout = {}
        self.portfolio_viz_ok = False
        self.portfolio_note = ""
        self.portfolio_bundle = {}
        try:
            year = int(self.input_year.strip())
        except ValueError:
            self.note = "Indique un año válido en el selector."
            self.busy = False
            return
        base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.get(
                    f"{base}/api/v1/kpi/summary",
                    params={"cohort_year": year, "use_db": "true"},
                )
                r.raise_for_status()
                d = r.json()
                per = float(d["persistency_rate_pct"])
                act = int(d["policies_active"])
                lap = int(d["policies_lapsed"])
                total_pl = act + lap
                active_share = (act / total_pl * 100.0) if total_pl > 0 else 0.0
                t_raw = d.get("technical_loss_ratio_pct")
                tlr_f = float(t_raw) if t_raw is not None else None

                self.persistency = f"{per:.2f} %"
                self.active_n = f"{act:,}"
                self.lapsed_n = f"{lap:,}"
                self.avg_premium = f"{float(d['avg_annual_premium']):,.2f}"
                self.tlr = f"{float(t_raw):.2f} %" if t_raw is not None else "—"
                self.note = str(d.get("data_note", ""))

                gfig = build_kpi_gauge_figure(
                    persistency_pct=per,
                    technical_loss_pct=tlr_f,
                    active_share_pct=active_share,
                    height=280,
                )
                gpj = gfig.to_plotly_json()
                self.kpi_gauge_data = gpj["data"]
                self.kpi_gauge_layout = gpj.get("layout") or {}
                self.kpi_gauge_ok = True

                dfig = build_cartera_donut_figure(active=act, lapsed=lap, height=260)
                dj = dfig.to_plotly_json()
                self.cartera_donut_data = dj["data"]
                self.cartera_donut_layout = dj.get("layout") or {}
                self.cartera_donut_ok = True

                try:
                    rp = await client.get(
                        f"{base}/api/v1/kpi/cohort-portfolio",
                        params={"cohort_year": year},
                    )
                    if rp.status_code == 200:
                        raw_pf = rp.json()
                        figs = build_all_portfolio_figures(raw_pf)
                        self.portfolio_bundle = {
                            k: {"data": d, "layout": l} for k, (d, l) in figs.items()
                        }
                        self.portfolio_viz_ok = True
                        self.portfolio_note = ""
                    elif rp.status_code == 404:
                        self.portfolio_viz_ok = False
                        self.portfolio_note = (
                            "No hay pólizas en base para este año: cargue datos en Admin "
                            "para activar sunburst, treemap, waterfall, Sankey y el resto."
                        )
                    elif rp.status_code == 503:
                        self.portfolio_viz_ok = False
                        self.portfolio_note = (
                            "El servidor de cómputo no tiene base de datos configurada (DATABASE_URL)."
                        )
                    else:
                        self.portfolio_viz_ok = False
                        self.portfolio_note = f"Paquete de cartera no disponible (HTTP {rp.status_code})."
                except Exception as pe:  # noqa: BLE001
                    self.portfolio_viz_ok = False
                    self.portfolio_note = f"No se pudo cargar el análisis de cartera. ({pe})"
        except Exception as e:  # noqa: BLE001
            self.note = f"No se pudieron cargar los indicadores. Intente de nuevo en unos minutos. ({e})"
            self.portfolio_viz_ok = False
            self.portfolio_bundle = {}
        self.busy = False
