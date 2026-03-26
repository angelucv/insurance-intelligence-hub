"""Esquemas Pydantic v2 compartidos por la API (demo)."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class KpiSummary(BaseModel):
    """Resumen de KPIs para tablero gerencial / laboratorio."""

    persistency_rate_pct: float = Field(
        ...,
        ge=0,
        le=100,
        description="Tasa de persistencia (pólizas activas / emitidas cohorte).",
    )
    policies_active: int = Field(..., ge=0)
    policies_lapsed: int = Field(..., ge=0)
    avg_annual_premium: float = Field(..., gt=0)
    cohort_year: int = Field(..., ge=2000, le=2100)
    technical_loss_ratio_pct: float | None = Field(
        default=None,
        ge=0,
        description="Demo: siniestralidad / prima; None si no aplica.",
    )
    data_note: str = Field(
        default="",
        description="Aclaración de que los datos son sintéticos para demo.",
    )


class MarketSeriesPoint(BaseModel):
    """Un punto de serie temporal SUDEASEG (miles de Bs. salvo ratio)."""

    period_year: int = Field(..., ge=2000, le=2100)
    period_month: int = Field(..., ge=1, le=12)
    primas_netas_thousands_bs: float | None = None
    siniestros_totales_thousands_bs: float | None = None
    loss_ratio_proxy: float | None = Field(
        default=None,
        description="siniestros_totales / primas_netas (misma granularidad que mode).",
    )


class MarketResumenSeries(BaseModel):
    """Serie desde resumen por empresa (YTD o flujo mensual)."""

    granularity: Literal["ytd_eom", "monthly_flow"]
    unit: str = Field(default="thousands_bs", description="Miles de bolívares según SUDEASEG.")
    source: str = Field(default="market_sudeaseg_resumen_empresa")
    empresa_filter_note: str = Field(
        default="",
        description="Criterio aplicado sobre empresa_nombre_norm (La Fe por defecto).",
    )
    points: list[MarketSeriesPoint] = Field(default_factory=list)


class MarketResumenExtendedPoint(BaseModel):
    """Punto resumen SUDEASEG con el conjunto de magnitudes analíticas (miles de Bs.)."""

    period_year: int = Field(..., ge=2000, le=2100)
    period_month: int = Field(..., ge=1, le=12)
    primas_netas_thousands_bs: float | None = None
    siniestros_pagados_thousands_bs: float | None = None
    reservas_psp_brutas_thousands_bs: float | None = None
    reservas_psp_netas_reaseg_thousands_bs: float | None = None
    siniestros_totales_thousands_bs: float | None = None
    comisiones_thousands_bs: float | None = None
    gastos_adquisicion_thousands_bs: float | None = None
    gastos_administracion_thousands_bs: float | None = None
    loss_ratio_proxy: float | None = Field(default=None, description="siniestros_totales / primas")
    comision_ratio_proxy: float | None = Field(default=None, description="comisiones / primas")
    gasto_adm_ratio_proxy: float | None = Field(default=None, description="gastos_admin / primas")


class MarketResumenExtendedSeries(BaseModel):
    granularity: Literal["ytd_eom", "monthly_flow"]
    unit: str = Field(default="thousands_bs")
    source: str = Field(default="market_sudeaseg_resumen_empresa")
    empresa_filter_note: str = ""
    points: list[MarketResumenExtendedPoint] = Field(default_factory=list)


class MarketCuadroPoint(BaseModel):
    period_year: int = Field(..., ge=2000, le=2100)
    period_month: int = Field(..., ge=1, le=12)
    primas_netas_thousands_bs: float | None = None
    resultado_tecnico_bruto_thousands_bs: float | None = None
    resultado_reaseguro_cedido_thousands_bs: float | None = None
    resultado_tecnico_neto_thousands_bs: float | None = None
    resultado_gestion_general_thousands_bs: float | None = None
    saldo_operaciones_thousands_bs: float | None = None


class MarketCuadroSeries(BaseModel):
    granularity: Literal["ytd_eom", "monthly_flow"]
    unit: str = Field(default="thousands_bs")
    source: str = Field(default="market_sudeaseg_cuadro_resultados")
    empresa_filter_note: str = ""
    points: list[MarketCuadroPoint] = Field(default_factory=list)


class MarketLaFeSnapshot(BaseModel):
    """Último cierre disponible para La Fe + referencia de mercado (YTD a ese mes)."""

    period_year: int
    period_month: int
    unit: str = Field(default="thousands_bs")
    la_fe: dict[str, float | None] = Field(
        default_factory=dict,
        description="primas_ytd, siniestros_totales_ytd, siniestros_pagados_ytd, comisiones_ytd, gastos_admin_ytd, loss_ratio_ytd",
    )
    mercado_total: dict[str, float | None] = Field(
        default_factory=dict,
        description="primas_ytd, siniestros_totales_ytd, loss_ratio_ytd",
    )
    cuota_mercado_primas_pct: float | None = Field(
        default=None,
        description="100 * la_fe.primas_ytd / mercado_total.primas_ytd",
    )
    empresa_filter_note: str = ""


class PortalMercadoYoySeries(BaseModel):
    """Series La Fe y mercado total para dos años (comparativa YoY del portal)."""

    la_fe_a: MarketResumenSeries
    la_fe_b: MarketResumenSeries
    totals_a: MarketResumenSeries
    totals_b: MarketResumenSeries


class PortalMercadoBundle(BaseModel):
    """Una sola respuesta HTTP: snapshot + series rango + opcional YoY (portal Reflex)."""

    snapshot: MarketLaFeSnapshot | None = None
    la_fe_range: MarketResumenSeries
    totals_range: MarketResumenSeries
    yoy: PortalMercadoYoySeries | None = None


class IngestResult(BaseModel):
    batch_id: str
    rows_valid: int
    inserted: int
    skipped_duplicate_policy_id: int
    errors: list[dict[str, Any]] = Field(default_factory=list)
    error_truncated: bool = False
