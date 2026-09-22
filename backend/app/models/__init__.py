# Models module — SQLAlchemy ORM models
from app.models.interest import Interest, UserInterest
from app.models.skill import Skill, UserSkill
from app.models.user import User

__all__ = [
    "User",
    "Skill",
    "UserSkill",
    "Interest",
    "UserInterest",
]
