"""
Application configuration loaded from environment variables.

All secrets and environment-specific values live here.
See .env.example for the full list of supported variables.
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # ── Project ──────────────────────────────────────────────────────
    PROJECT_NAME: str = "CampusOS"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"

    # ── Database ─────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://campusos:campusos@localhost:5432/campusos"

    # ── Security ─────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-to-a-random-string-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── CORS ─────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


settings = Settings()
