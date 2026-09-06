"""
Authentication service layer.

Encapsulates user registration, credential verification, and token issuance.
"""

from typing import Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserLoginRequest, UserRegisterRequest


class AuthService:
    """Handles business logic for user authentication."""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch a user record by email address."""
        stmt = select(User).where(User.email == email.lower().strip())
        return db.scalars(stmt).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Fetch a user record by primary key UUID."""
        stmt = select(User).where(User.id == user_id)
        return db.scalars(stmt).first()

    @classmethod
    def register_user(
        cls, db: Session, req: UserRegisterRequest
    ) -> Tuple[User, str]:
        """
        Register a new user account.

        Raises:
            HTTPException: 409 if email is already taken.
        """
        existing = cls.get_user_by_email(db, req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "EMAIL_TAKEN",
                    "message": "An account with this email address already exists.",
                },
            )

        password_hash = get_password_hash(req.password)
        user = User(
            email=req.email.lower().strip(),
            name=req.name.strip(),
            password_hash=password_hash,
            preferred_opportunity_types=[],
            preferred_work_modes=[],
            is_active=True,
            is_admin=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id)})
        return user, access_token

    @classmethod
    def authenticate_user(
        cls, db: Session, req: UserLoginRequest
    ) -> Tuple[User, str]:
        """
        Authenticate user credentials and issue an access token.

        Raises:
            HTTPException: 401 if email or password does not match.
            HTTPException: 403 if account is marked inactive.
        """
        user = cls.get_user_by_email(db, req.email)
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password.",
                },
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCOUNT_INACTIVE",
                    "message": "This account is inactive.",
                },
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        return user, access_token


auth_service = AuthService()
