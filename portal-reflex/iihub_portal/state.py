"""Estado del portal: URLs, KPIs y gráficos de mercado."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx
import plotly.graph_objects as go
import reflex as rx
from plotly.graph_objects import Figure as PlotlyFigure

from iihub_portal.plotly_responsive import merge_responsive_layout
from iihub_portal.portfolio_plotly import build_all_portfolio_figures, demo_portfolio_payload_from_kpi
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

# HTTP: conexiones reutilizadas y tiempos acotados.
_HTTP_TIMEOUT = httpx.Timeout(90.0, connect=15.0)
_HTTP_LIMITS = httpx.Limits(max_keepalive_connections=20, max_connections=30)


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
    show_portal_guide: bool = True

    # Vista «La suite»: documentación completa vs. resumen ejecutivo
    suite_docs_mode: str = "full"
    # Menú lateral en móvil (sidebar oculto por defecto)
    mobile_nav_open: bool = False
    # KPI: fallo de red/API (para mensaje y acciones de recuperación)
    kpi_load_failed: bool = False

    # Mercado SUDEASEG: no cargar hasta que el usuario abra la pestaña (ahorra red/CPU en móvil).
    mercado_hydrated: bool = False
    mercado_loading: bool = False

    # Cartera: KPI rápido primero; gráficos avanzados en segundo plane (página principal más ligera).
    portfolio_charts_busy: bool = False
    kpi_act_n: int = 0
    kpi_lap_n: int = 0
    kpi_avg_pr: float = 0.0

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
        return PlotlyFigure(
            data=self.market_plot_data,
            layout=merge_responsive_layout(self.market_plot_layout),
        )

    @rx.var(cache=True, auto_deps=True)
    def market_ratio_figure(self) -> PlotlyFigure:
        if not self.market_ratio_ok or not self.market_ratio_plot_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.market_ratio_plot_data,
            layout=merge_responsive_layout(self.market_ratio_plot_layout),
        )

    @rx.var(cache=True, auto_deps=True)
    def kpi_gauge_figure(self) -> PlotlyFigure:
        if not self.kpi_gauge_ok or not self.kpi_gauge_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.kpi_gauge_data,
            layout=merge_responsive_layout(self.kpi_gauge_layout),
        )

    @rx.var(cache=True, auto_deps=True)
    def cartera_donut_figure(self) -> PlotlyFigure:
        if not self.cartera_donut_ok or not self.cartera_donut_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.cartera_donut_data,
            layout=merge_responsive_layout(self.cartera_donut_layout),
        )

    @rx.var(cache=True, auto_deps=True)
    def market_heatmap_figure(self) -> PlotlyFigure:
        if not self.market_heatmap_ok or not self.market_heatmap_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.market_heatmap_data,
            layout=merge_responsive_layout(self.market_heatmap_layout),
        )

    @rx.var(cache=True, auto_deps=True)
    def market_yoy_la_figure(self) -> PlotlyFigure:
        if not self.market_yoy_la_ok or not self.market_yoy_la_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.market_yoy_la_data,
            layout=merge_responsive_layout(self.market_yoy_la_layout),
        )

    @rx.var(cache=True, auto_deps=True)
    def market_yoy_mk_figure(self) -> PlotlyFigure:
        if not self.market_yoy_mk_ok or not self.market_yoy_mk_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.market_yoy_mk_data,
            layout=merge_responsive_layout(self.market_yoy_mk_layout),
        )

    @rx.var(cache=True, auto_deps=True)
    def market_yoy_lr_figure(self) -> PlotlyFigure:
        if not self.market_yoy_lr_ok or not self.market_yoy_lr_data:
            return PlotlyFigure()
        return PlotlyFigure(
            data=self.market_yoy_lr_data,
            layout=merge_responsive_layout(self.market_yoy_lr_layout),
        )

    @rx.var(cache=True, auto_deps=True)
    def kpi_refresh_busy(self) -> bool:
        """True mientras carga el resumen KPI o los gráficos de cartera en segundo plano."""
        return bool(self.busy or self.portfolio_charts_busy)

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
        return PlotlyFigure(
            data=b["data"],
            layout=merge_responsive_layout(b.get("layout")),
        )

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

    def _django_admin_base_url(self) -> str:
        """Base pública del Django Admin (sin barra final). Varias claves por compatibilidad con hosting."""
        for key in (
            "DJANGO_ADMIN_BASE_URL",
            "ADMIN_BASE_URL",
            "PUBLIC_DJANGO_ADMIN_URL",
        ):
            v = os.environ.get(key, "").strip().rstrip("/")
            if v:
                return v
        return ""

    async def hydrate_urls(self):
        """Lee variables de entorno en runtime (Reflex Cloud / servidor)."""
        from datetime import datetime

        now = datetime.now()
        self.input_year = str(now.year)
        self.input_month = f"{now.month:02d}"

        ab = self._django_admin_base_url()
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
        # Solo cartera en arranque: snapshot + gráficos SUDEASEG se cargan al abrir «Mercado SUDEASEG»
        # (menos latencia y menos trabajo en 3G/móvil).
        await self.load_kpi()

    def _apply_snapshot_payload(self, d: dict[str, Any] | None) -> None:
        """Rellena celdas del hero de mercado desde JSON snapshot (API o portal-bundle)."""
        self.snap_ok = False
        self.snap_period = "—"
        self.snap_primas = "—"
        self.snap_sini = "—"
        self.snap_lr = "—"
        self.snap_cuota = "—"
        self.snap_comisiones = "—"
        self.snap_gadm = "—"
        self.snap_mk_lr = "—"
        if not d:
            return

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

        py, pm = int(d["period_year"]), int(d["period_month"])
        self.snap_period = f"{py}-{pm:02d}"
        lf = d.get("la_fe") or {}
        mk = d.get("mercado_total") or {}
        self.snap_primas = fmt_num(lf.get("primas_ytd"))
        self.snap_sini = fmt_num(lf.get("siniestros_totales_ytd"))
        self.snap_lr = fmt_pct_ratio(lf.get("loss_ratio_ytd"))
        cq = d.get("cuota_mercado_primas_pct")
        self.snap_cuota = f"{float(cq):.3f} %" if cq is not None else "—"
        self.snap_comisiones = fmt_num(lf.get("comisiones_ytd"))
        self.snap_gadm = fmt_num(lf.get("gastos_admin_ytd"))
        self.snap_mk_lr = fmt_pct_ratio(mk.get("loss_ratio_ytd"))
        self.snap_ok = True

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
        self._apply_snapshot_payload(None)
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
            params = {
                "from_year": fy,
                "to_year": ty,
                "mode": mode,
                "yoy_a": yoy_a,
                "yoy_b": yoy_b,
            }
            try:
                async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, limits=_HTTP_LIMITS) as client:
                    r = await client.get(f"{base}/api/v1/market/portal-bundle", params=params)
                    r.raise_for_status()
                    bundle = r.json()
            except Exception as e:  # noqa: BLE001
                self.market_plot_error = f"No se pudo cargar la referencia de mercado. ({e})"
                return

            from plotly.subplots import make_subplots

            self._apply_snapshot_payload(bundle.get("snapshot"))
            la = (bundle.get("la_fe_range") or {}).get("points") or []
            tot = (bundle.get("totals_range") or {}).get("points") or []

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

            yoy_block = bundle.get("yoy")
            if yoy_a != yoy_b and isinstance(yoy_block, dict):
                try:
                    la_y1 = (yoy_block.get("la_fe_a") or {}).get("points") or []
                    la_y2 = (yoy_block.get("la_fe_b") or {}).get("points") or []
                    tot_y1 = (yoy_block.get("totals_a") or {}).get("points") or []
                    tot_y2 = (yoy_block.get("totals_b") or {}).get("points") or []
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

    async def pick_tab_mercado(self):
        self.ui_main_tab = "mercado"
        self.mobile_nav_open = False
        if self.mercado_hydrated or self.mercado_loading:
            return
        self.mercado_loading = True
        try:
            await self.load_sudeaseg_preview()
        finally:
            self.mercado_loading = False
        self.mercado_hydrated = True

    def pick_tab_cartera(self):
        self.ui_main_tab = "cartera"
        self.mobile_nav_open = False

    def pick_tab_suite(self):
        self.ui_main_tab = "suite"
        self.mobile_nav_open = False

    def toggle_mobile_nav(self):
        self.mobile_nav_open = not self.mobile_nav_open

    def close_mobile_nav(self):
        self.mobile_nav_open = False

    def toggle_snap_more(self):
        self.show_snap_more = not self.show_snap_more

    def dismiss_portal_guide(self):
        self.show_portal_guide = False

    def set_suite_docs_full(self):
        self.suite_docs_mode = "full"

    def set_suite_docs_summary(self):
        self.suite_docs_mode = "summary"

    async def _load_portfolio_charts_async(self, year: int) -> None:
        """Segunda fase: payload pesado de cartera (no bloquea tacómetros ni donut)."""
        self.portfolio_charts_busy = True
        self.portfolio_viz_ok = False
        self.portfolio_bundle = {}
        try:
            base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
            raw_pf: dict[str, Any] | None = None
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, limits=_HTTP_LIMITS) as client:
                r = await client.get(
                    f"{base}/api/v1/kpi/cohort-portfolio",
                    params={"cohort_year": year},
                )
                if r.status_code == 404:
                    raw_pf = None
                else:
                    r.raise_for_status()
                    raw_pf = r.json()

            act, lap = self.kpi_act_n, self.kpi_lap_n
            avg_pr = self.kpi_avg_pr
            note_low = str(self.note or "").lower()

            try:
                if raw_pf is not None:
                    self.portfolio_note = ""
                else:
                    raw_pf = demo_portfolio_payload_from_kpi(
                        cohort_year=year,
                        policies_active=act,
                        policies_lapsed=lap,
                        avg_annual_premium=avg_pr,
                    )
                    if "sin filas" in note_low or "sintética" in note_low or "synthetic" in note_low:
                        self.portfolio_note = (
                            "Sin datos de cohorte en BD para gráficos avanzados: demostración alineada al KPI. "
                            "Cargue pólizas en Admin para vistas reales."
                        )
                    else:
                        self.portfolio_note = (
                            "Visualización demostrativa alineada al resumen KPI (sin detalle de cohorte en BD)."
                        )
                figs = await asyncio.to_thread(build_all_portfolio_figures, raw_pf)
                self.portfolio_bundle = {
                    k: {"data": fd, "layout": fl} for k, (fd, fl) in figs.items()
                }
                self.portfolio_viz_ok = True
            except Exception as pe:  # noqa: BLE001
                raw_pf = demo_portfolio_payload_from_kpi(
                    cohort_year=year,
                    policies_active=act,
                    policies_lapsed=lap,
                    avg_annual_premium=avg_pr,
                )
                figs = await asyncio.to_thread(build_all_portfolio_figures, raw_pf)
                self.portfolio_bundle = {
                    k: {"data": fd, "layout": fl} for k, (fd, fl) in figs.items()
                }
                self.portfolio_viz_ok = True
                self.portfolio_note = f"Error al construir gráficos de cartera ({pe}). Demostración con KPI."
        finally:
            self.portfolio_charts_busy = False

    async def load_kpi(self):
        self.busy = True
        self.portfolio_charts_busy = True
        self.kpi_load_failed = False
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
            self.portfolio_charts_busy = False
            return
        base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, limits=_HTTP_LIMITS) as client:
                r = await client.get(
                    f"{base}/api/v1/kpi/cohort-bundle",
                    params={
                        "cohort_year": year,
                        "use_db": "true",
                        "include_portfolio": False,
                    },
                )
                r.raise_for_status()
                bundle = r.json()
                d = bundle["summary"]
                per = float(d["persistency_rate_pct"])
                act = int(d["policies_active"])
                lap = int(d["policies_lapsed"])
                total_pl = act + lap
                active_share = (act / total_pl * 100.0) if total_pl > 0 else 0.0
                t_raw = d.get("technical_loss_ratio_pct")
                tlr_f = float(t_raw) if t_raw is not None else None

                self.kpi_act_n = act
                self.kpi_lap_n = lap
                self.kpi_avg_pr = float(d["avg_annual_premium"])

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
                    height=360,
                    cohort_year=year,
                )
                gpj = gfig.to_plotly_json()
                self.kpi_gauge_data = gpj["data"]
                self.kpi_gauge_layout = gpj.get("layout") or {}
                self.kpi_gauge_ok = True

                dfig = build_cartera_donut_figure(active=act, lapsed=lap, height=300)
                dj = dfig.to_plotly_json()
                self.cartera_donut_data = dj["data"]
                self.cartera_donut_layout = dj.get("layout") or {}
                self.cartera_donut_ok = True

            self.busy = False
            # No usar asyncio.create_task: en Reflex el handler termina y la tarea en segundo plano
            # puede no ejecutarse o no actualizar estado → «Cargando…» infinito en gráficos de cartera.
            await self._load_portfolio_charts_async(year)
        except Exception as e:  # noqa: BLE001
            self.kpi_load_failed = True
            self.note = f"No se pudieron cargar los indicadores. Intente de nuevo en unos minutos. ({e})"
            self.portfolio_viz_ok = False
            self.portfolio_bundle = {}
            self.busy = False
            self.portfolio_charts_busy = False
