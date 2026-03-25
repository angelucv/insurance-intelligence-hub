"""Portal gerencial: KPIs (API) + enlaces a Admin y laboratorio Streamlit."""

from __future__ import annotations

import os

import httpx
import reflex as rx

from rxconfig import config

# Paleta demo (coherente con Streamlit config.toml)
_ACCENT_NAVY = "#1e3a8f"
_ACCENT_TEAL = "#0f766e"


class State(rx.State):
    """URLs de despliegue en state: se rellenan en el servidor con on_load (no en tiempo de build)."""

    admin_upload_url: str = "http://127.0.0.1:8080/admin/upload-policies/"
    streamlit_lab_url: str = "http://127.0.0.1:8501"
    env_hint: str = ""

    input_year: str = "2022"
    persistency: str = "—"
    active_n: str = "—"
    lapsed_n: str = "—"
    avg_premium: str = "—"
    tlr: str = "—"
    note: str = ""
    busy: bool = False

    async def hydrate_urls(self):
        """Lee Secrets / env en runtime en Reflex Cloud (evita href fijados a localhost en el bundle)."""
        ab = os.environ.get("DJANGO_ADMIN_BASE_URL", "").strip().rstrip("/")
        if ab:
            self.admin_upload_url = f"{ab}/admin/upload-policies/"
        else:
            self.admin_upload_url = "http://127.0.0.1:8080/admin/upload-policies/"

        sl = os.environ.get("STREAMLIT_LAB_URL", "").strip().rstrip("/")
        if sl:
            self.streamlit_lab_url = sl
        else:
            self.streamlit_lab_url = "http://127.0.0.1:8501"

        hints: list[str] = []
        if not ab:
            hints.append("Define DJANGO_ADMIN_BASE_URL en Secrets del servidor para enlazar al Admin en la nube.")
        if not sl:
            hints.append("Define STREAMLIT_LAB_URL en Secrets para enlazar al laboratorio Streamlit en la nube.")
        self.env_hint = " ".join(hints)

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


def _hero() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "Insurance Intelligence Hub",
                size="8",
                style={"color": "white", "margin": 0},
            ),
            rx.text(
                "Portal ejecutivo: KPIs al instante. Profundiza en el laboratorio Streamlit (gráficos y exportación).",
                size="3",
                style={"color": "rgba(255,255,255,0.92)", "max_width": "40rem"},
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        width="100%",
        padding="2rem",
        border_radius="14px",
        style={
            "background": f"linear-gradient(125deg, {_ACCENT_NAVY} 0%, {_ACCENT_TEAL} 55%, #134e4a 100%)",
            "box_shadow": "0 12px 40px rgba(15, 23, 42, 0.18)",
        },
    )


def _kpi_card(title: str, value: rx.Var) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(title, size="2", weight="bold", color="gray"),
            rx.heading(value, size="6", style={"color": _ACCENT_NAVY}),
            spacing="1",
            align_items="start",
            width="100%",
        ),
        style={
            "border": "1px solid var(--gray-6)",
            "box_shadow": "0 2px 12px rgba(15, 23, 42, 0.06)",
            "min_height": "110px",
        },
        width="100%",
    )


def index() -> rx.Component:
    return rx.box(
        rx.color_mode.button(position="top-right"),
        rx.container(
            rx.vstack(
                _hero(),
                rx.hstack(
                    rx.link(
                        rx.button(
                            "Carga de pólizas (Admin)",
                            size="3",
                            color_scheme="blue",
                        ),
                        href=State.admin_upload_url,
                        is_external=True,
                    ),
                    rx.link(
                        rx.button(
                            "Abrir laboratorio (Streamlit)",
                            size="3",
                            color_scheme="teal",
                            variant="solid",
                        ),
                        href=State.streamlit_lab_url,
                        is_external=True,
                    ),
                    spacing="4",
                    align="center",
                    flex_wrap="wrap",
                    padding_y="2",
                ),
                rx.text(
                    "Admin: usuarios staff. Los enlaces usan las URLs configuradas en Secrets (runtime).",
                    size="1",
                    color="gray",
                ),
                rx.cond(
                    State.env_hint != "",
                    rx.text(State.env_hint, size="1", color="orange"),
                ),
                rx.divider(),
                rx.heading("Resumen de cohorte", size="5"),
                rx.hstack(
                    rx.text("Año cohorte:", weight="medium"),
                    rx.input(
                        value=State.input_year,
                        on_change=State.set_input_year,
                        width="100px",
                    ),
                    rx.button(
                        "Actualizar KPI",
                        on_click=State.load_kpi,
                        loading=State.busy,
                        color_scheme="blue",
                    ),
                    spacing="3",
                    align="center",
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
                rx.text(State.note, size="2", color="gray"),
                rx.text(
                    f"{config.app_name} · variables de entorno en despliegue (API, Admin, Streamlit).",
                    size="1",
                    color="gray",
                ),
                spacing="4",
                width="100%",
                max_width="1200px",
                margin_x="auto",
            ),
            padding_y="6",
            size="4",
        ),
        min_height="100vh",
        style={"background": "var(--gray-2)"},
    )


app = rx.App()
app.add_page(index, on_load=State.hydrate_urls)
