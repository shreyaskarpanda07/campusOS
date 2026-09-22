"""
User and Profile service layer.

Handles profile viewing, academic updates, and skill/interest synchronization.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.interest import Interest, UserInterest
from app.models.skill import Skill, UserSkill
from app.models.user import User
from app.schemas.user import (
    InterestItem,
    InterestRead,
    SkillItem,
    SkillRead,
    UserProfileResponse,
    UserProfileUpdateRequest,
)


class UserService:
    """Business logic for student profiles and preferences."""

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Fetch a User by UUID primary key."""
        stmt = select(User).where(User.id == user_id)
        return db.scalars(stmt).first()

    @classmethod
    def get_profile(cls, db: Session, user: User) -> UserProfileResponse:
        """
        Build and return a detailed profile response for the user,
        including assigned skills (with proficiency) and interests.
        """
        # Load user skills with joined Skill entity
        stmt_skills = (
            select(UserSkill)
            .where(UserSkill.user_id == user.id)
            .join(Skill)
            .order_by(Skill.name)
        )
        user_skills = db.scalars(stmt_skills).all()

        # Load user interests with joined Interest entity
        stmt_interests = (
            select(UserInterest)
            .where(UserInterest.user_id == user.id)
            .join(Interest)
            .order_by(Interest.name)
        )
        user_interests = db.scalars(stmt_interests).all()

        skills_list = [
            SkillRead(
                id=us.skill_id,
                name=us.skill.name,
                proficiency=us.proficiency,
            )
            for us in user_skills
        ]

        interests_list = [
            InterestRead(
                id=ui.interest_id,
                name=ui.interest.name,
            )
            for ui in user_interests
        ]

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            university=user.university,
            degree=user.degree,
            branch=user.branch,
            graduation_year=user.graduation_year,
            current_year=user.current_year,
            cgpa=float(user.cgpa) if user.cgpa is not None else None,
            preferred_opportunity_types=user.preferred_opportunity_types or [],
            preferred_work_modes=user.preferred_work_modes or [],
            preferred_locations=user.preferred_locations or [],
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
            skills=skills_list,
            interests=interests_list,
        )

    @classmethod
    def update_profile(
        cls, db: Session, user: User, req: UserProfileUpdateRequest
    ) -> UserProfileResponse:
        """
        Update academic details and general preferences.
        """
        data = req.model_dump(exclude_unset=True)

        for field, value in data.items():
            if field == "cgpa" and value is not None:
                setattr(user, field, round(value, 2))
            else:
                setattr(user, field, value)

        db.add(user)
        db.commit()
        db.refresh(user)

        return cls.get_profile(db, user)

    @classmethod
    def sync_skills(
        cls, db: Session, user: User, items: List[SkillItem]
    ) -> List[SkillRead]:
        """
        Replace user's skills with the provided list.
        Canonicalizes skill names and links them to the user.
        """
        # Delete existing associations
        existing = db.scalars(
            select(UserSkill).where(UserSkill.user_id == user.id)
        ).all()
        for us in existing:
            db.delete(us)
        db.flush()

        result_skills: List[SkillRead] = []
        seen_names = set()

        for item in items:
            clean_name = item.name.strip()
            if not clean_name:
                continue

            normalized_key = clean_name.lower()
            if normalized_key in seen_names:
                continue
            seen_names.add(normalized_key)

            # Find or create canonical Skill
            skill_stmt = select(Skill).where(
                func.lower(Skill.name) == normalized_key
            )
            skill = db.scalars(skill_stmt).first()
            if not skill:
                skill = Skill(name=clean_name)
                db.add(skill)
                db.flush()

            clean_prof = item.proficiency.strip() if item.proficiency else None
            user_skill = UserSkill(
                user_id=user.id,
                skill_id=skill.id,
                proficiency=clean_prof,
            )
            db.add(user_skill)
            result_skills.append(
                SkillRead(
                    id=skill.id,
                    name=skill.name,
                    proficiency=clean_prof,
                )
            )

        db.commit()
        return result_skills

    @classmethod
    def sync_interests(
        cls, db: Session, user: User, items: List[InterestItem]
    ) -> List[InterestRead]:
        """
        Replace user's interests with the provided list.
        Canonicalizes interest names and links them to the user.
        """
        # Delete existing associations
        existing = db.scalars(
            select(UserInterest).where(UserInterest.user_id == user.id)
        ).all()
        for ui in existing:
            db.delete(ui)
        db.flush()

        result_interests: List[InterestRead] = []
        seen_names = set()

        for item in items:
            clean_name = item.name.strip()
            if not clean_name:
                continue

            normalized_key = clean_name.lower()
            if normalized_key in seen_names:
                continue
            seen_names.add(normalized_key)

            # Find or create canonical Interest
            interest_stmt = select(Interest).where(
                func.lower(Interest.name) == normalized_key
            )
            interest = db.scalars(interest_stmt).first()
            if not interest:
                interest = Interest(name=clean_name)
                db.add(interest)
                db.flush()

            user_interest = UserInterest(
                user_id=user.id,
                interest_id=interest.id,
            )
            db.add(user_interest)
            result_interests.append(
                InterestRead(
                    id=interest.id,
                    name=interest.name,
                )
            )

        db.commit()
        return result_interests


user_service = UserService()
