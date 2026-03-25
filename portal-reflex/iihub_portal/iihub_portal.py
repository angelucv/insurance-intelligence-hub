"""Portal gerencial: KPIs (API) + enlaces a Admin y laboratorio Streamlit."""

from __future__ import annotations

import os

import httpx
import reflex as rx

# Marca Seguros La Fe (alineado con Streamlit / Admin)
_BRAND_PURPLE = "#7029B3"
_BRAND_DEEP = "#5a1f94"
_BRAND_LAVENDER = "#8B5CF6"
_BRAND_MUTED = "#64748b"


class State(rx.State):
    """URLs de despliegue en state: se rellenan en el servidor con on_load (no en tiempo de build)."""

    admin_upload_url: str = "http://127.0.0.1:8080/admin/upload-policies/"
    streamlit_lab_url: str = "http://127.0.0.1:8501"

    input_year: str = "2022"
    persistency: str = "—"
    active_n: str = "—"
    lapsed_n: str = "—"
    avg_premium: str = "—"
    tlr: str = "—"
    note: str = ""
    busy: bool = False

    async def hydrate_urls(self):
        """Lee variables de entorno en runtime (Reflex Cloud / servidor)."""
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
            rx.center(
                rx.image(
                    src="/logo2.jpg",
                    alt="60 años Seguros La Fe",
                    height="64px",
                    style={"max_width": "min(100%, 480px)", "object_fit": "contain"},
                ),
                width="100%",
                padding_y="4",
                style={"background": "var(--gray-2)"},
            ),
            rx.box(
                rx.container(
                    rx.vstack(
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
app.add_page(index, on_load=State.hydrate_urls)
