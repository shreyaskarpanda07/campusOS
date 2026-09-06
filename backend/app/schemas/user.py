"""
Pydantic schemas for User and Authentication.
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
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Token representation."""

    access_token: str
    token_type: str = "bearer"


class AuthResponseData(BaseModel):
    """Returned on successful registration or login."""

    user: UserRead
    access_token: str
    token_type: str = "bearer"
