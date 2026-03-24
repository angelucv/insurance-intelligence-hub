"""Fila de póliza para ingestión CSV/XLSX (validación Pydantic v2)."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Status = Literal["active", "lapsed"]


class PolicyRow(BaseModel):
    policy_id: str = Field(..., min_length=1, max_length=64)
    cohort_year: int = Field(..., ge=2000, le=2100)
    issue_age: int = Field(..., ge=0, le=110)
    annual_premium: float = Field(..., gt=0)
    status: Status

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
