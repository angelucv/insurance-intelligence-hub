"""Fila de siniestro para ingestión CSV/XLSX (validación Pydantic v2)."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ClaimStatus = Literal["reported", "adjusted", "paid", "closed", "rejected"]


class ClaimRow(BaseModel):
    claim_id: str = Field(..., min_length=1, max_length=128)
    policy_id: str = Field(..., min_length=1, max_length=64)
    loss_date: date
    reported_amount_bs: float = Field(default=0, ge=0)
    paid_amount_bs: float = Field(default=0, ge=0)
    status: ClaimStatus

    @field_validator("claim_id", "policy_id")
    @classmethod
    def strip_ids(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("identificador vacío")
        return s

    @field_validator("status", mode="before")
    @classmethod
    def lower_status(cls, v: object) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return str(v).lower()
