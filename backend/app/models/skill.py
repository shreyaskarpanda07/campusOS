"""
Skill and UserSkill SQLAlchemy ORM models.
"""

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship

from app.db.base import Base, generate_uuid


class Skill(Base):
    """Canonical skill entity."""

    __tablename__ = "skills"

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

    user_skills = relationship(
        "UserSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
    )


class UserSkill(Base):
    """Junction table associating a User with a Skill and optional proficiency."""

    __tablename__ = "user_skills"

    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    )
    proficiency = Column(
        String(20),
        nullable=True,
    )

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")
