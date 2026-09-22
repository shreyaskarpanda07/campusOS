"""
Interest and UserInterest SQLAlchemy ORM models.
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship

from app.db.base import Base, generate_uuid


class Interest(Base):
    """Canonical career/opportunity interest domain."""

    __tablename__ = "interests"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=generate_uuid,
    )
    name = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user_interests = relationship(
        "UserInterest",
        back_populates="interest",
        cascade="all, delete-orphan",
    )


class UserInterest(Base):
    """Junction table associating a User with an Interest."""

    __tablename__ = "user_interests"

    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    interest_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("interests.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user = relationship("User", back_populates="interests")
    interest = relationship("Interest", back_populates="user_interests")
