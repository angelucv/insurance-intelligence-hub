"""Conexión SQLAlchemy opcional (sin DATABASE_URL no se crea engine)."""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

if TYPE_CHECKING:
    pass

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _normalize_postgres_url(url: str) -> str:
    """Supabase suele entregar postgresql://; SQLAlchemy + psycopg3 usa postgresql+psycopg://."""
    if url.startswith("postgresql://") and "+psycopg" not in url.split("://", 1)[0]:
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


def init_engine() -> Engine | None:
    global _engine, _SessionLocal
    url = get_settings().database_url
    if not url:
        _engine = None
        _SessionLocal = None
        return None
    url = _normalize_postgres_url(url.strip())
    # Supabase pooler en modo transacción no admite prepared statements; evita errores opacos.
    connect_kw: dict = {}
    if "psycopg" in url:
        connect_kw["connect_args"] = {"prepare_threshold": None}
    _engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=5,
        **connect_kw,
    )
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    return _engine


def get_engine() -> Engine | None:
    return _engine


def get_session_local() -> sessionmaker[Session] | None:
    return _SessionLocal


def db_session() -> Generator[Session, None, None]:
    if _SessionLocal is None:
        raise RuntimeError("DATABASE_URL no configurada")
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
