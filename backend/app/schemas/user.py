"""
Pydantic schemas for User, Authentication, and Student Profile.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base fields shared across user schemas."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)


class UserRegisterRequest(BaseModel):
    """Payload for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password with minimum 8 characters")
    name: str = Field(..., min_length=1, max_length=255)


class UserLoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class SkillItem(BaseModel):
    """Single skill input item with optional proficiency."""

    name: str = Field(..., min_length=1, max_length=100)
    proficiency: Optional[str] = Field(
        None,
        description="Skill level: beginner, intermediate, or advanced",
    )


class SkillRead(BaseModel):
    """Skill details returned to client."""

    id: UUID
    name: str
    proficiency: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class InterestItem(BaseModel):
    """Single interest item."""

    name: str = Field(..., min_length=1, max_length=100)


class InterestRead(BaseModel):
    """Interest details returned to client."""

    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserSkillsUpdateRequest(BaseModel):
    """Payload to synchronize user skills."""

    skills: List[SkillItem] = Field(default_factory=list)


class UserInterestsUpdateRequest(BaseModel):
    """Payload to synchronize user interests."""

    interests: List[InterestItem] = Field(default_factory=list)


class UserProfileUpdateRequest(BaseModel):
    """Payload for updating academic details and preferences."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    university: Optional[str] = Field(None, max_length=255)
    degree: Optional[str] = Field(None, max_length=100)
    branch: Optional[str] = Field(None, max_length=100)
    graduation_year: Optional[int] = Field(None, ge=1990, le=2100)
    current_year: Optional[int] = Field(None, ge=1, le=6)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    preferred_opportunity_types: Optional[List[str]] = None
    preferred_work_modes: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None


class UserRead(UserBase):
    """Public user profile schema."""

    id: UUID
    university: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    current_year: Optional[int] = None
    cgpa: Optional[float] = None
    preferred_opportunity_types: List[str] = Field(default_factory=list)
    preferred_work_modes: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserRead):
    """Detailed profile response including assigned skills and interests."""

    skills: List[SkillRead] = Field(default_factory=list)
    interests: List[InterestRead] = Field(default_factory=list)


class TokenData(BaseModel):
    """Token representation."""

    access_token: str
    token_type: str = "bearer"


class AuthResponseData(BaseModel):
    """Returned on successful registration or login."""

    user: UserRead
    access_token: str
    token_type: str = "bearer"
