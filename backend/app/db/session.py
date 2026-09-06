"""
SQLAlchemy engine and session factory.

The engine connects to PostgreSQL using DATABASE_URL from settings.
SessionLocal provides request-scoped sessions via the get_db dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
