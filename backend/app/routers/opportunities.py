"""
Opportunities API router.

Provides:
- GET /api/opportunities — Search and filter opportunity feed
- GET /api/opportunities/{id} — Retrieve detailed opportunity with sources & skills
- POST /api/opportunities — Create opportunity (admin only)
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_current_admin_user,
    get_db,
)
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.opportunity import (
    OpportunityCreateRequest,
    OpportunityDetail,
    OpportunityListResponse,
)
from app.services.opportunity import opportunity_service

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get(
    "",
    response_model=ApiResponse,
    summary="Search and filter opportunities feed",
)
def list_opportunities(
    type: Optional[str] = Query(None, description="Opportunity type: internship, hackathon, competition, etc."),
    work_mode: Optional[str] = Query(None, description="Work mode: remote, onsite, hybrid"),
    location: Optional[str] = Query(None, description="Location search query"),
    organization: Optional[str] = Query(None, description="Organization search query"),
    search: Optional[str] = Query(None, description="Text search across title, organization, description"),
    status_filter: Optional[str] = Query("active", alias="status", description="Opportunity status"),
    max_cgpa: Optional[float] = Query(None, description="Filter for opportunities student is eligible for by CGPA"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Search and filter opportunities with pagination.
    Requires student authentication.
    """
    res: OpportunityListResponse = opportunity_service.list_opportunities(
        db=db,
        type=type,
        work_mode=work_mode,
        location=location,
        organization=organization,
        search=search,
        status=status_filter,
        max_cgpa=max_cgpa,
        page=page,
        per_page=per_page,
        student=current_user,
    )
    return ApiResponse(
        data=res.model_dump(mode="json"),
        error=None,
    )


@router.get(
    "/{id}",
    response_model=ApiResponse,
    summary="Get opportunity details",
)
def get_opportunity(
    id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve full opportunity details including required skills and source provenance.
    """
    opp = opportunity_service.get_opportunity_by_id(db, id, student=current_user)
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "OPPORTUNITY_NOT_FOUND",
                "message": f"Opportunity with id '{id}' was not found.",
            },
        )
    return ApiResponse(
        data=opp.model_dump(mode="json"),
        error=None,
    )


@router.post(
    "",
    response_model=ApiResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create opportunity (Admin only)",
)
def create_opportunity(
    req: OpportunityCreateRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Create a new opportunity record with skill linking and source provenance.
    Restricted to administrators.
    """
    opp = opportunity_service.create_opportunity(db, req)
    return ApiResponse(
        data=opp.model_dump(mode="json"),
        error=None,
    )
