"""
Source and OpportunitySource SQLAlchemy ORM models.

Maintains provenance for every ingested or manually seeded opportunity.
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship

from app.db.base import Base, generate_uuid


class Source(Base):
    """Origin platform or feed from which opportunities are ingested."""

    __tablename__ = "sources"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )
    name = Column(
        String(255),
        nullable=False,
    )
    base_url = Column(
        Text,
        nullable=True,
    )
    source_type = Column(
        String(50),
        nullable=False,
        default="manual",  # manual, web_scrape, api_feed
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    opportunity_sources = relationship(
        "OpportunitySource",
        back_populates="source",
        cascade="all, delete-orphan",
    )


class OpportunitySource(Base):
    """Provenance record linking an Opportunity to its Source and origin URL."""

    __tablename__ = "opportunity_sources"

    opportunity_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_url = Column(
        Text,
        nullable=True,
    )
    fetched_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    opportunity = relationship("Opportunity", back_populates="sources")
    source = relationship("Source", back_populates="opportunity_sources")
