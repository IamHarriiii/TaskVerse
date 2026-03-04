"""
TaskVerse application configuration.
Reads from environment variables / .env file using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration — values come from env vars or .env file."""

    # ── App ──
    app_name: str = "TaskVerse"
    app_version: str = "2.0.0"
    debug: bool = False

    # ── API ──
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ── CORS ──
    cors_origins: list[str] = ["*"]

    # ── Auth (JWT) ──
    secret_key: str = Field(
        default="taskverse-dev-secret-change-me-in-production",
        description="JWT signing key — MUST be changed in production",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ── Frontend ──
    api_base_url: str = "http://localhost:8000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
