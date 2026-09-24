"""
Opportunity and OpportunitySkill SQLAlchemy ORM models.

Stores structured opportunity records with requirements, deadlines, and skill links.
"""

from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Numeric,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base, TimestampMixin, generate_uuid

# Cross-database JSON support (Postgres JSONB with SQLite JSON fallback)
JsonType = JSONB().with_variant(JSON(), "sqlite")
# Cross-database Vector support (pgvector on Postgres with SQLite JSON fallback)
VectorType = Vector(1536).with_variant(JSON(), "sqlite")


class Opportunity(Base, TimestampMixin):
    """Normalized opportunity record (internship, hackathon, competition, etc.)."""

    __tablename__ = "opportunities"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )
    title = Column(
        String(500),
        nullable=False,
    )
    organization = Column(
        String(255),
        nullable=False,
        index=True,
    )
    type = Column(
        String(50),
        nullable=False,
        index=True,  # internship, hackathon, competition, fellowship, scholarship, other
    )
    description = Column(
        Text,
        nullable=True,
    )
    deadline = Column(
        Date,
        nullable=True,
        index=True,
    )
    start_date = Column(
        Date,
        nullable=True,
    )
    location = Column(
        String(255),
        nullable=True,
    )
    work_mode = Column(
        String(20),
        nullable=True,  # remote, onsite, hybrid
    )
    minimum_cgpa = Column(
        Numeric(4, 2),
        nullable=True,
    )
    eligibility = Column(
        JsonType,
        default=dict,
        nullable=False,  # e.g. {"eligible_years": [2026, 2027], "eligible_branches": ["CS"]}
    )
    compensation = Column(
        String(255),
        nullable=True,
    )
    application_url = Column(
        Text,
        nullable=True,
    )
    status = Column(
        String(20),
        nullable=False,
        default="active",
        index=True,  # active, expired, draft, archived
    )
    extraction_confidence = Column(
        Float,
        nullable=True,
    )
    embedding = Column(
        VectorType,
        nullable=True,
    )

    # Relationships
    skills = relationship(
        "OpportunitySkill",
        back_populates="opportunity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sources = relationship(
        "OpportunitySource",
        back_populates="opportunity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OpportunitySkill(Base):
    """Junction table linking an Opportunity to required/preferred skills."""

    __tablename__ = "opportunity_skills"

    opportunity_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    requirement_type = Column(
        String(20),
        nullable=False,
        default="required",  # required or preferred
    )

    opportunity = relationship("Opportunity", back_populates="skills")
    skill = relationship("Skill")
