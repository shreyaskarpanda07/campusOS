"""
Authentication endpoints.

Provides:
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import (
    AuthResponseData,
    UserLoginRequest,
    UserRead,
    UserRegisterRequest,
)
from app.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    req: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new student or user.

    Validates that the email is unique, hashes the password with bcrypt,
    stores the user, and immediately returns a JWT access token.
    """
    user, access_token = auth_service.register_user(db, req)
    return ApiResponse(
        data=AuthResponseData(
            user=UserRead.model_validate(user),
            access_token=access_token,
            token_type="bearer",
        ).model_dump(mode="json"),
        error=None,
    )


@router.post(
    "/login",
    response_model=ApiResponse,
    summary="Authenticate and receive access token",
)
def login(
    req: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate an existing user with email and password.

    Returns the user profile and a signed JWT access token.
    """
    user, access_token = auth_service.authenticate_user(db, req)
    return ApiResponse(
        data=AuthResponseData(
            user=UserRead.model_validate(user),
            access_token=access_token,
            token_type="bearer",
        ).model_dump(mode="json"),
        error=None,
    )


@router.post(
    "/logout",
    response_model=ApiResponse,
    summary="Invalidate active session / logout",
)
def logout(
    current_user: User = Depends(get_current_active_user),
):
    """
    Log out the current user.

    For JWT tokens, client clears local token storage.
    Confirms token was valid.
    """
    return ApiResponse(
        data={"message": f"Successfully logged out {current_user.email}."},
        error=None,
    )
