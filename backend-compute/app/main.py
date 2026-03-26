"""API: KPIs, ingestión y observabilidad (Loguru / Sentry opcional)."""

from __future__ import annotations

import logging
from typing import Any
import os
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_engine, init_engine
from app.deps import get_db, verify_ingest_key
from app.ingest_service import ingest_policies_bytes
from app.kpi_service import kpi_cohort_bundle_payload, kpi_summary_payload
from app.portfolio_analytics import cohort_portfolio_payload
from app.market_service import (
    la_fe_cuadro_series,
    la_fe_market_snapshot_latest,
    la_fe_resumen_extended_series,
    la_fe_resumen_series,
    market_cuadro_totals_series,
    market_resumen_totals_extended_series,
    market_resumen_totals_series,
    sanitize_empresa_norm_fragment,
)
from app.schemas import (
    IngestResult,
    KpiSummary,
    MarketCuadroPoint,
    MarketCuadroSeries,
    MarketLaFeSnapshot,
    MarketResumenExtendedPoint,
    MarketResumenExtendedSeries,
    MarketResumenSeries,
    MarketSeriesPoint,
)


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
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "insurance-hub-api",
        "health": "/health",
        "docs": "/docs",
        "kpi": "/api/v1/kpi/summary",
        "kpi_bundle": "/api/v1/kpi/cohort-bundle",
        "market_la_fe": "/api/v1/market/la-fe/resumen-series",
        "market_totals": "/api/v1/market/resumen/totals-series",
        "market_la_fe_resumen_extended": "/api/v1/market/la-fe/resumen-extended",
        "market_totals_resumen_extended": "/api/v1/market/resumen/totals-extended",
        "market_la_fe_cuadro": "/api/v1/market/la-fe/cuadro-series",
        "market_cuadro_totals": "/api/v1/market/cuadro/totals-series",
        "market_la_fe_snapshot": "/api/v1/market/la-fe/snapshot-latest",
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


def _market_db_error(e: Exception) -> HTTPException:
    msg = str(e).lower()
    if "undefinedcolumn" in msg or "does not exist" in msg:
        return HTTPException(
            status_code=503,
            detail="Tablas o columnas SUDEASEG ausentes. Aplique supabase/migrations/003_market_sudeaseg_monthly.sql y ejecute el ETL.",
        )
    return HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/market/la-fe/resumen-series", response_model=MarketResumenSeries)
def market_la_fe_resumen_series(
    from_year: int = 2023,
    to_year: int = 2026,
    mode: str = "monthly_flow",
    empresa_norm_fragment: str = "fe c.a.",
    db: Session | None = Depends(get_db),
) -> MarketResumenSeries:
    """Serie temporal La Fe (resumen SUDEASEG). `mode`: `ytd` | `monthly_flow`."""
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no configurada (DATABASE_URL)")
    if mode not in ("ytd", "monthly_flow"):
        raise HTTPException(status_code=400, detail="mode debe ser ytd o monthly_flow")
    try:
        rows = la_fe_resumen_series(
            db,
            from_year=from_year,
            to_year=to_year,
            mode=mode,  # type: ignore[arg-type]
            empresa_norm_fragment=empresa_norm_fragment,
        )
    except ProgrammingError as e:
        raise _market_db_error(e) from e
    gran = "ytd_eom" if mode == "ytd" else "monthly_flow"
    note = (
        "empresa_nombre_norm LIKE '%…%' AND '%seguros%' (fragmento: "
        f"{sanitize_empresa_norm_fragment(empresa_norm_fragment)!r})"
    )
    return MarketResumenSeries(
        granularity=gran,  # type: ignore[arg-type]
        empresa_filter_note=note,
        points=[MarketSeriesPoint.model_validate(p) for p in rows],
    )


@app.get("/api/v1/market/resumen/totals-series", response_model=MarketResumenSeries)
def market_resumen_totals_series_ep(
    from_year: int = 2023,
    to_year: int = 2026,
    mode: str = "monthly_flow",
    db: Session | None = Depends(get_db),
) -> MarketResumenSeries:
    """Totales de mercado (suma de empresas) por mes — misma granularidad que La Fe."""
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no configurada (DATABASE_URL)")
    if mode not in ("ytd", "monthly_flow"):
        raise HTTPException(status_code=400, detail="mode debe ser ytd o monthly_flow")
    try:
        rows = market_resumen_totals_series(
            db,
            from_year=from_year,
            to_year=to_year,
            mode=mode,  # type: ignore[arg-type]
        )
    except ProgrammingError as e:
        raise _market_db_error(e) from e
    gran = "ytd_eom" if mode == "ytd" else "monthly_flow"
    return MarketResumenSeries(
        granularity=gran,  # type: ignore[arg-type]
        source="market_sudeaseg_resumen_empresa:sum",
        empresa_filter_note="Suma de todas las filas por (año, mes) en la tabla cargada.",
        points=[MarketSeriesPoint.model_validate(p) for p in rows],
    )


@app.get("/api/v1/market/la-fe/resumen-extended", response_model=MarketResumenExtendedSeries)
def market_la_fe_resumen_extended(
    from_year: int = 2023,
    to_year: int = 2026,
    mode: str = "monthly_flow",
    empresa_norm_fragment: str = "fe c.a.",
    db: Session | None = Depends(get_db),
) -> MarketResumenExtendedSeries:
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no configurada (DATABASE_URL)")
    if mode not in ("ytd", "monthly_flow"):
        raise HTTPException(status_code=400, detail="mode debe ser ytd o monthly_flow")
    try:
        rows = la_fe_resumen_extended_series(
            db,
            from_year=from_year,
            to_year=to_year,
            mode=mode,  # type: ignore[arg-type]
            empresa_norm_fragment=empresa_norm_fragment,
        )
    except ProgrammingError as e:
        raise _market_db_error(e) from e
    gran = "ytd_eom" if mode == "ytd" else "monthly_flow"
    note = (
        "empresa_nombre_norm LIKE '%…%' AND '%seguros%' (fragmento: "
        f"{sanitize_empresa_norm_fragment(empresa_norm_fragment)!r})"
    )
    return MarketResumenExtendedSeries(
        granularity=gran,  # type: ignore[arg-type]
        empresa_filter_note=note,
        points=[MarketResumenExtendedPoint.model_validate(p) for p in rows],
    )


@app.get("/api/v1/market/resumen/totals-extended", response_model=MarketResumenExtendedSeries)
def market_resumen_totals_extended_ep(
    from_year: int = 2023,
    to_year: int = 2026,
    mode: str = "monthly_flow",
    db: Session | None = Depends(get_db),
) -> MarketResumenExtendedSeries:
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no configurada (DATABASE_URL)")
    if mode not in ("ytd", "monthly_flow"):
        raise HTTPException(status_code=400, detail="mode debe ser ytd o monthly_flow")
    try:
        rows = market_resumen_totals_extended_series(
            db,
            from_year=from_year,
            to_year=to_year,
            mode=mode,  # type: ignore[arg-type]
        )
    except ProgrammingError as e:
        raise _market_db_error(e) from e
    gran = "ytd_eom" if mode == "ytd" else "monthly_flow"
    return MarketResumenExtendedSeries(
        granularity=gran,  # type: ignore[arg-type]
        source="market_sudeaseg_resumen_empresa:sum",
        empresa_filter_note="Suma de todas las filas por (año, mes) en la tabla cargada.",
        points=[MarketResumenExtendedPoint.model_validate(p) for p in rows],
    )


@app.get("/api/v1/market/la-fe/cuadro-series", response_model=MarketCuadroSeries)
def market_la_fe_cuadro_series_ep(
    from_year: int = 2023,
    to_year: int = 2026,
    mode: str = "monthly_flow",
    empresa_norm_fragment: str = "fe c.a.",
    db: Session | None = Depends(get_db),
) -> MarketCuadroSeries:
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no configurada (DATABASE_URL)")
    if mode not in ("ytd", "monthly_flow"):
        raise HTTPException(status_code=400, detail="mode debe ser ytd o monthly_flow")
    try:
        rows = la_fe_cuadro_series(
            db,
            from_year=from_year,
            to_year=to_year,
            mode=mode,  # type: ignore[arg-type]
            empresa_norm_fragment=empresa_norm_fragment,
        )
    except ProgrammingError as e:
        raise _market_db_error(e) from e
    gran = "ytd_eom" if mode == "ytd" else "monthly_flow"
    note = (
        "empresa_nombre_norm LIKE '%…%' AND '%seguros%' (fragmento: "
        f"{sanitize_empresa_norm_fragment(empresa_norm_fragment)!r})"
    )
    return MarketCuadroSeries(
        granularity=gran,  # type: ignore[arg-type]
        empresa_filter_note=note,
        points=[MarketCuadroPoint.model_validate(p) for p in rows],
    )


@app.get("/api/v1/market/cuadro/totals-series", response_model=MarketCuadroSeries)
def market_cuadro_totals_series_ep(
    from_year: int = 2023,
    to_year: int = 2026,
    mode: str = "monthly_flow",
    db: Session | None = Depends(get_db),
) -> MarketCuadroSeries:
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no configurada (DATABASE_URL)")
    if mode not in ("ytd", "monthly_flow"):
        raise HTTPException(status_code=400, detail="mode debe ser ytd o monthly_flow")
    try:
        rows = market_cuadro_totals_series(
            db,
            from_year=from_year,
            to_year=to_year,
            mode=mode,  # type: ignore[arg-type]
        )
    except ProgrammingError as e:
        raise _market_db_error(e) from e
    gran = "ytd_eom" if mode == "ytd" else "monthly_flow"
    return MarketCuadroSeries(
        granularity=gran,  # type: ignore[arg-type]
        source="market_sudeaseg_cuadro_resultados:sum",
        empresa_filter_note="Suma de todas las filas por (año, mes) en cuadro de resultados.",
        points=[MarketCuadroPoint.model_validate(p) for p in rows],
    )


@app.get("/api/v1/market/la-fe/snapshot-latest", response_model=MarketLaFeSnapshot)
def market_la_fe_snapshot_latest_ep(
    empresa_norm_fragment: str = "fe c.a.",
    db: Session | None = Depends(get_db),
) -> MarketLaFeSnapshot:
    if db is None:
        raise HTTPException(status_code=503, detail="Base de datos no configurada (DATABASE_URL)")
    try:
        raw = la_fe_market_snapshot_latest(db, empresa_norm_fragment=empresa_norm_fragment)
    except ProgrammingError as e:
        raise _market_db_error(e) from e
    if not raw:
        raise HTTPException(status_code=404, detail="Sin datos La Fe en resumen SUDEASEG.")
    return MarketLaFeSnapshot.model_validate(raw)


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


@app.get("/api/v1/kpi/cohort-bundle")
def kpi_cohort_bundle(
    cohort_year: int = 2022,
    seed: int = 42,
    n_policies: int = 8000,
    use_db: bool = True,
    db: Session | None = Depends(get_db),
) -> dict[str, Any]:
    """
    KPI + agregados de cartera en una sola respuesta HTTP.
    Evita duplicar la lectura de `policies` que ocurría al llamar summary y cohort-portfolio en paralelo.
    """
    return kpi_cohort_bundle_payload(
        session=db,
        cohort_year=cohort_year,
        seed=seed,
        n_policies=n_policies,
        prefer_db=use_db and db is not None,
    )


@app.get("/api/v1/kpi/cohort-portfolio")
def cohort_portfolio_charts(
    cohort_year: int,
    db: Session | None = Depends(get_db),
) -> dict[str, Any]:
    """
    Agregados listos para Plotly: emisión mensual, siniestralidad, histogramas,
    dispersión prima vs pagado, etc. Requiere pólizas en BD para la cohorte.
    """
    if db is None or db.bind is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no configurada (defina DATABASE_URL)",
        )
    raw = cohort_portfolio_payload(db, cohort_year)
    if raw is None:
        raise HTTPException(
            status_code=404,
            detail="Sin pólizas en base para esta cohorte",
        )
    return raw


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
