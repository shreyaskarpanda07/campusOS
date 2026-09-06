"""
User SQLAlchemy ORM model.

Represents a student or admin user profile in CampusOS.
"""

from sqlalchemy import Boolean, Column, Integer, Numeric, String, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy import Uuid

from app.db.base import Base, TimestampMixin, generate_uuid

# Support JSONB on PostgreSQL with JSON fallback on SQLite
JsonType = JSONB().with_variant(JSON(), "sqlite")


class User(Base, TimestampMixin):
    """User account and academic profile."""

    __tablename__ = "users"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash = Column(
        String(255),
        nullable=False,
    )
    name = Column(
        String(255),
        nullable=False,
    )
    university = Column(
        String(255),
        nullable=True,
    )
    degree = Column(
        String(100),
        nullable=True,
    )
    branch = Column(
        String(100),
        nullable=True,
    )
    graduation_year = Column(
        Integer,
        nullable=True,
    )
    current_year = Column(
        Integer,
        nullable=True,
    )
    cgpa = Column(
        Numeric(4, 2),
        nullable=True,
    )
    preferred_opportunity_types = Column(
        JsonType,
        default=list,
        nullable=False,
    )
    preferred_work_modes = Column(
        JsonType,
        default=list,
        nullable=False,
    )
    is_admin = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
