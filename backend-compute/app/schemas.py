"""Esquemas Pydantic v2 compartidos por la API (demo)."""

from typing import Any

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


class IngestResult(BaseModel):
    batch_id: str
    rows_valid: int
    inserted: int
    skipped_duplicate_policy_id: int
    errors: list[dict[str, Any]] = Field(default_factory=list)
    error_truncated: bool = False
