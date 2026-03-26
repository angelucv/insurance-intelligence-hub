"""Estado del portal: URLs, KPIs y gráficos de mercado."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx
import plotly.graph_objects as go
import reflex as rx
from plotly.graph_objects import Figure as PlotlyFigure

from iihub_portal.plotly_charts import (
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

    input_year: str = "2022"
    persistency: str = "—"
    active_n: str = "—"
    lapsed_n: str = "—"
    avg_premium: str = "—"
    tlr: str = "—"
    note: str = ""
    busy: bool = False
    market_charts_busy: bool = False

    ui_main_tab: str = "mercado"
    market_fy: str = "2023"
    market_ty: str = "2026"
    market_mode: str = "monthly_flow"
    show_snap_more: bool = False

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

        fy = os.environ.get("MARKET_PREVIEW_FROM_YEAR", "").strip()
        ty = os.environ.get("MARKET_PREVIEW_TO_YEAR", "").strip()
        if fy.isdigit():
            self.market_fy = fy
        if ty.isdigit():
            self.market_ty = ty

    async def portal_on_load(self):
        await self.hydrate_urls()
        await asyncio.gather(
            self.load_sudeaseg_preview(),
            self.load_market_snapshot(),
        )

    async def load_sudeaseg_preview(self):
        self.market_plot_ok = False
        self.market_ratio_ok = False
        self.market_plot_error = ""
        self.market_plot_data = []
        self.market_plot_layout = {}
        self.market_ratio_plot_data = []
        self.market_ratio_plot_layout = {}
        self.market_charts_busy = True
        try:
            base = os.environ.get("COMPUTE_API_URL", "http://127.0.0.1:8000").rstrip("/")
            try:
                fy = int(self.market_fy.strip())
                ty = int(self.market_ty.strip())
            except ValueError:
                self.market_plot_error = "Indique años válidos (desde / hasta)."
                return
            mode = (self.market_mode or "monthly_flow").strip()
            if mode not in ("monthly_flow", "ytd"):
                mode = "monthly_flow"
            params = {"from_year": fy, "to_year": ty, "mode": mode}
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
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

    def set_market_fy(self, v: str):
        self.market_fy = v

    def set_market_ty(self, v: str):
        self.market_ty = v

    def set_market_mode(self, v: str):
        self.market_mode = v

    def pick_tab_mercado(self):
        self.ui_main_tab = "mercado"

    def pick_tab_cohorte(self):
        self.ui_main_tab = "cohorte"

    def toggle_snap_more(self):
        self.show_snap_more = not self.show_snap_more

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
