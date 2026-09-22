"""
User profile and preferences API router.

Provides:
- GET /api/users/me — Read current authenticated user's profile with skills & interests
- PATCH /api/users/me — Update academic details and opportunity preferences
- PUT /api/users/me/skills — Synchronize skill tags and proficiency
- PUT /api/users/me/interests — Synchronize interest tags
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import (
    UserInterestsUpdateRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserSkillsUpdateRequest,
)
from app.services.user import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=ApiResponse,
    summary="Get current user profile",
)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve full profile of the authenticated student, including
    assigned skills (with proficiency levels) and career interests.
    """
    profile = user_service.get_profile(db, current_user)
    return ApiResponse(
        data=profile.model_dump(mode="json"),
        error=None,
    )


@router.patch(
    "/me",
    response_model=ApiResponse,
    summary="Update academic profile and preferences",
)
def update_my_profile(
    req: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update university, degree, branch, year, CGPA, and preference lists.
    """
    profile = user_service.update_profile(db, current_user, req)
    return ApiResponse(
        data=profile.model_dump(mode="json"),
        error=None,
    )


@router.put(
    "/me/skills",
    response_model=ApiResponse,
    summary="Update user skill tags",
)
def update_my_skills(
    req: UserSkillsUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Synchronize user's skills list and proficiency levels.
    Replaces existing skill links with the provided list.
    """
    skills = user_service.sync_skills(db, current_user, req.skills)
    return ApiResponse(
        data=[s.model_dump(mode="json") for s in skills],
        error=None,
    )


@router.put(
    "/me/interests",
    response_model=ApiResponse,
    summary="Update user career interests",
)
def update_my_interests(
    req: UserInterestsUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Synchronize user's career and opportunity interests.
    Replaces existing interest links with the provided list.
    """
    interests = user_service.sync_interests(db, current_user, req.interests)
    return ApiResponse(
        data=[i.model_dump(mode="json") for i in interests],
        error=None,
    )
