"""API: KPIs, ingestión y observabilidad (Loguru / Sentry opcional)."""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine, init_engine
from app.deps import get_db, verify_ingest_key
from app.ingest_service import ingest_policies_bytes
from app.kpi_service import kpi_summary_payload
from app.schemas import IngestResult, KpiSummary


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    if settings.sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[
                FastApiIntegration(),
                LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
            ],
            traces_sample_rate=0.1,
        )
    init_engine()
    if get_engine():
        logger.info("Motor SQLAlchemy listo (DATABASE_URL)")
    else:
        logger.warning("Sin DATABASE_URL: ingestión vía API deshabilitada; KPI puede ser sintético")
    yield


app = FastAPI(
    title="Insurance Intelligence Hub API",
    description="Cómputo, KPIs, ingestión a PostgreSQL (Supabase) y validación Pydantic.",
    version="0.2.0",
    lifespan=lifespan,
)

_origins = os.environ.get("CORS_ALLOW_ORIGINS", "*").strip()
if _origins == "*":
    _cors = ["*"]
else:
    _cors = [o.strip() for o in _origins.split(",") if o.strip()]

_creds = False if _cors == ["*"] else True
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors,
    allow_credentials=_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "insurance-hub-api",
        "health": "/health",
        "docs": "/docs",
        "kpi": "/api/v1/kpi/summary",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/health/db")
def health_db() -> dict[str, bool]:
    eng = get_engine()
    if not eng:
        return {"database_configured": False, "reachable": False}
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database_configured": True, "reachable": True}
    except Exception as e:  # noqa: BLE001
        logger.warning("BD configurada pero no alcanzable: {}", e)
        return {"database_configured": True, "reachable": False}


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
    use_db: bool = True,
    db: Session | None = Depends(get_db),
) -> KpiSummary:
    """KPIs desde PostgreSQL + DuckDB si hay datos; si no, cartera sintética."""
    raw = kpi_summary_payload(
        session=db,
        cohort_year=cohort_year,
        seed=seed,
        n_policies=n_policies,
        prefer_db=use_db and db is not None,
    )
    return KpiSummary.model_validate(raw)


@app.post("/api/v1/ingest/policies", response_model=IngestResult, dependencies=[Depends(verify_ingest_key)])
async def ingest_policies(
    file: UploadFile = File(...),
    db: Session | None = Depends(get_db),
) -> IngestResult:
    """Carga CSV/XLSX de pólizas validadas. Requiere `X-API-Key` si `INGEST_API_KEY` está definida."""
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no configurada (defina DATABASE_URL)",
        )
    name = file.filename or "upload"
    data = await file.read()
    try:
        result = ingest_policies_bytes(db, data, name, source="api")
    except ValueError as e:
        logger.warning("Ingesta rechazada: {}", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        logger.exception("Ingesta falló ({})", name)
        raise HTTPException(status_code=500, detail=str(e)) from e
    try:
        payload = IngestResult.model_validate(result)
    except Exception as e:  # noqa: BLE001
        logger.exception("Respuesta ingest inválida")
        raise HTTPException(status_code=500, detail=f"validate: {e}") from e
    logger.info("Ingesta {}: insertadas {}", name, result.get("inserted"))
    return payload
