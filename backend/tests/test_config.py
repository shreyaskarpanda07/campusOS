"""
Tests for application configuration.

Verifies that the Settings class loads correctly with default values.
"""

from app.core.config import Settings


def test_default_settings():
    """Settings should load with sensible defaults."""
    s = Settings()
    assert s.PROJECT_NAME == "CampusOS"
    assert s.VERSION == "0.1.0"
    assert s.API_PREFIX == "/api"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 1440
    assert s.ALGORITHM == "HS256"


def test_cors_origins_default():
    """Default CORS should allow localhost:3000 (frontend dev server)."""
    s = Settings()
    assert "http://localhost:3000" in s.CORS_ORIGINS
