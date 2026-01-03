from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_API_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PSMA_",
        extra="ignore",
        env_file=str(_API_DIR / ".env"),
        env_file_encoding="utf-8",
    )

    cors_origins: str = "http://localhost:3000"

    http_timeout_seconds: float = 10.0
    user_agent: str = "PSMA/0.0.0 (local dev)"

    log_level: str = "INFO"
    log_format: str = "json"  # json | text

    tmdb_api_key: str | None = None


settings = Settings()
