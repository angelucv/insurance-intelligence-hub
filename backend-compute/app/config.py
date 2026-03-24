"""Configuración por entorno."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str | None = None
    ingest_api_key: str | None = None
    sentry_dsn: str | None = None
    app_env: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
