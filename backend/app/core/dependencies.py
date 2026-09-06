"""
FastAPI dependency injection providers.

Provides reusable dependencies for:
- Database sessions
- Authentication and current user resolution
- Role-based authorization (active user, admin user)
"""

from collections.abc import Generator
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User

# Optional OAuth2 scheme to allow custom error handling in dependency
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate the Bearer access token and retrieve the corresponding User.

    Raises:
        HTTPException: 401 if token is missing, invalid, expired, or user not found.
    """
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "UNAUTHORIZED",
            "message": "Authentication token is missing, invalid, or expired.",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise unauthorized_exception

    payload = decode_access_token(token)
    if payload is None:
        raise unauthorized_exception

    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        raise unauthorized_exception

    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise unauthorized_exception

    from app.services.auth import auth_service

    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise unauthorized_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify the authenticated user account is active.

    Raises:
        HTTPException: 403 if account is deactivated.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_INACTIVE",
                "message": "This account is inactive.",
            },
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Verify the authenticated user has administrative privileges.

    Raises:
        HTTPException: 403 if user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Administrator privileges required.",
            },
        )
    return current_user
