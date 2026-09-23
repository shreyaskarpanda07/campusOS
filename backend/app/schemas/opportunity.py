"""
Pydantic schemas for Opportunities, OpportunitySkills, and Sources.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EligibilityRead(BaseModel):
    """Result of deterministic eligibility evaluation."""

    status: str  # eligible, ineligible, uncertain
    reasons: List[str] = Field(default_factory=list)
    missing_data: List[str] = Field(default_factory=list)


class OpportunitySkillItem(BaseModel):
    """Skill specification for opportunity creation."""

    name: str = Field(..., min_length=1, max_length=100)
    requirement_type: str = Field(default="required", pattern="^(required|preferred)$")


class OpportunitySkillRead(BaseModel):
    """Skill requirement attached to an opportunity."""

    id: UUID
    name: str
    requirement_type: str

    model_config = ConfigDict(from_attributes=True)


class OpportunitySourceRead(BaseModel):
    """Source provenance details for an opportunity."""

    source_id: UUID
    source_name: str
    source_url: Optional[str] = None
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityCreateRequest(BaseModel):
    """Payload for creating a new opportunity (admin)."""

    title: str = Field(..., min_length=2, max_length=500)
    organization: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    deadline: Optional[date] = None
    start_date: Optional[date] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None  # remote, onsite, hybrid
    minimum_cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    eligibility: Dict[str, Any] = Field(default_factory=dict)
    compensation: Optional[str] = None
    application_url: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|expired|draft|archived)$")
    extraction_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    skills: List[OpportunitySkillItem] = Field(default_factory=list)
    source_name: Optional[str] = None
    source_url: Optional[str] = None


class OpportunityRead(BaseModel):
    """Standard opportunity representation returned in list feeds and cards."""

    id: UUID
    title: str
    organization: str
    type: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    start_date: Optional[date] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    minimum_cgpa: Optional[float] = None
    eligibility: Dict[str, Any] = Field(default_factory=dict)
    compensation: Optional[str] = None
    application_url: Optional[str] = None
    status: str
    skills: List[OpportunitySkillRead] = Field(default_factory=list)
    eligibility_evaluation: Optional[EligibilityRead] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityDetail(OpportunityRead):
    """Detailed opportunity view including source provenance and updated timestamp."""

    sources: List[OpportunitySourceRead] = Field(default_factory=list)
    updated_at: datetime


class PaginationMeta(BaseModel):
    """Pagination metadata returned in paginated lists."""

    total: int
    page: int
    per_page: int
    pages: int


class OpportunityListResponse(BaseModel):
    """Paginated collection of opportunities."""

    items: List[OpportunityRead]
    pagination: PaginationMeta
