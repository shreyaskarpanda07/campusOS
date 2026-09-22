# Services module — business logic layer
from app.services.auth import AuthService, auth_service
from app.services.opportunity import OpportunityService, opportunity_service
from app.services.user import UserService, user_service

__all__ = [
    "AuthService",
    "auth_service",
    "UserService",
    "user_service",
    "OpportunityService",
    "opportunity_service",
]
