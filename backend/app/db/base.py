"""
SQLAlchemy declarative base and shared mixins.

All models should inherit from Base.
Models that need created_at / updated_at should also use TimestampMixin.
"""

import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns to a model."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def generate_uuid() -> uuid.UUID:
    """Generate a new UUID4 for use as a primary key."""
    return uuid.uuid4()
