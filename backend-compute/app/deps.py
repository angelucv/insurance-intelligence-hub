"""Dependencias FastAPI."""

from collections.abc import Generator

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_session_local


def get_db() -> Generator[Session | None, None, None]:
    SessionLocal = get_session_local()
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def verify_ingest_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    expected = get_settings().ingest_api_key
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(status_code=401, detail="API key de ingestión inválida o ausente")
