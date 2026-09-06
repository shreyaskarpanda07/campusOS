"""
FastAPI dependency injection providers.

Provides reusable dependencies for:
- Database sessions
- Authentication (Phase 2)
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
