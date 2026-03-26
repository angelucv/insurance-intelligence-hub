"""Fila de póliza para ingestión CSV/XLSX (validación Pydantic v2)."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Status = Literal["active", "lapsed"]


class PolicyRow(BaseModel):
    policy_id: str = Field(..., min_length=1, max_length=64)
    cohort_year: int = Field(..., ge=2000, le=2100)
    issue_age: int = Field(..., ge=0, le=110)
    annual_premium: float = Field(..., gt=0)
    status: Status
    issue_date: date | None = Field(
        default=None,
        description="Fecha de emisión; si falta en CSV se usa 15-jun cohort_year.",
    )

    @field_validator("policy_id")
    @classmethod
    def strip_policy_id(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("policy_id vacío")
        return s

    @field_validator("status", mode="before")
    @classmethod
    def lower_status(cls, v: object) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return str(v).lower()

    @model_validator(mode="after")
    def _default_and_check_issue_date(self) -> PolicyRow:
        d = self.issue_date
        if d is None:
            return self.model_copy(update={"issue_date": date(self.cohort_year, 6, 15)})
        if d.year != self.cohort_year:
            raise ValueError("issue_date debe ser del mismo año calendario que cohort_year")
        return self
