"""Portal gerencial: KPIs desde la API de cómputo (Reflex)."""

from __future__ import annotations

import os

import httpx
import reflex as rx

from rxconfig import config


class State(rx.State):
    input_year: str = "2022"
    persistency: str = "—"
    active_n: str = "—"
    lapsed_n: str = "—"
    avg_premium: str = "—"
    tlr: str = "—"
    note: str = ""
    busy: bool = False

    def set_input_year(self, v: str):
        self.input_year = v

    async def load_kpi(self):
        self.busy = True
        yield
        try:
            year = int(self.input_year.strip())
        except ValueError:
            self.note = "Año inválido."
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
            self.note = f"Error al llamar a la API: {e}"
        self.busy = False


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Insurance Intelligence Hub", size="8"),
            rx.text(
                "Portal gerencial (demo). La carga de archivos vive en Django Admin; aquí solo lectura de KPIs.",
                size="3",
                color="gray",
            ),
            rx.hstack(
                rx.text("Cohorte (año):"),
                rx.input(
                    value=State.input_year,
                    on_change=State.set_input_year,
                    width="120px",
                ),
                rx.button("Cargar KPI", on_click=State.load_kpi, loading=State.busy),
                spacing="3",
                align="center",
            ),
            rx.grid(
                rx.card(
                    rx.text("Persistencia", weight="bold"),
                    rx.heading(State.persistency, size="6"),
                ),
                rx.card(
                    rx.text("Pólizas activas", weight="bold"),
                    rx.heading(State.active_n, size="6"),
                ),
                rx.card(
                    rx.text("Lapsos", weight="bold"),
                    rx.heading(State.lapsed_n, size="6"),
                ),
                rx.card(
                    rx.text("Prima media", weight="bold"),
                    rx.heading(State.avg_premium, size="6"),
                ),
                rx.card(
                    rx.text("Ratio técnico (demo)", weight="bold"),
                    rx.heading(State.tlr, size="6"),
                ),
                columns="5",
                spacing="3",
                width="100%",
            ),
            rx.text(State.note, size="2", color="gray"),
            rx.text(
                f"App: {config.app_name} — configurar COMPUTE_API_URL en despliegue.",
                size="2",
                color="gray",
            ),
            spacing="4",
            width="100%",
        ),
        padding_y="6",
    )


app = rx.App()
app.add_page(index)
