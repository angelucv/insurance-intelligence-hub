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


class IngestResult(BaseModel):
    batch_id: str
    rows_valid: int
    inserted: int
    skipped_duplicate_policy_id: int
    errors: list[dict[str, Any]] = Field(default_factory=list)
    error_truncated: bool = False
