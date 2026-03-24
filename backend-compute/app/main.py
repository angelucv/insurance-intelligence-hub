"""API mínima neutra: ampliar con routers y lógica actuarial."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.demo_engine import compute_kpi_summary
from app.schemas import KpiSummary

app = FastAPI(
    title="Insurance Intelligence Hub API",
    description="Capa de cómputo y endpoints (demo base).",
    version="0.1.0",
)

_origins = os.environ.get("CORS_ALLOW_ORIGINS", "*").strip()
if _origins == "*":
    _cors = ["*"]
else:
    _cors = [o.strip() for o in _origins.split(",") if o.strip()]

# allow_credentials=True no es compatible con allow_origins=["*"] en Starlette.
_creds = False if _cors == ["*"] else True
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors,
    allow_credentials=_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/info")
def info() -> dict[str, str]:
    return {
        "service": "backend-compute",
        "role": "api_and_analytics",
    }


@app.get("/api/v1/kpi/summary", response_model=KpiSummary)
def kpi_summary(
    cohort_year: int = 2022,
    seed: int = 42,
    n_policies: int = 8000,
) -> KpiSummary:
    """KPIs agregados en DuckDB sobre cartera sintética (demo)."""
    raw = compute_kpi_summary(seed=seed, n_policies=n_policies, cohort_year=cohort_year)
    return KpiSummary.model_validate(raw)
