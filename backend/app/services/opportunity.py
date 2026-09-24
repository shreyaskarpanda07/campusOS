"""
Opportunity service layer.

Provides:
- Opportunity creation with skill linking and source provenance
- Filtered search and pagination
- Detail retrieval
- Automated deterministic eligibility evaluation for authenticated students
"""

import math
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity, OpportunitySkill
from app.models.skill import Skill
from app.models.source import OpportunitySource, Source
from app.models.user import User
from app.schemas.opportunity import (
    EligibilityRead,
    OpportunityCreateRequest,
    OpportunityDetail,
    OpportunityListResponse,
    OpportunityRead,
    OpportunitySkillRead,
    OpportunitySourceRead,
    PaginationMeta,
)
from app.services.eligibility import eligibility_engine


class OpportunityService:
    """Business logic for opportunity ingestion, search, and retrieval."""

    @classmethod
    def create_opportunity(
        cls, db: Session, req: OpportunityCreateRequest
    ) -> OpportunityDetail:
        """
        Create a new opportunity record with skill links and source provenance.
        Preserves source URL and guarantees unknown fields remain null (FR-03).
        """
        opp = Opportunity(
            title=req.title.strip(),
            organization=req.organization.strip(),
            type=req.type.strip().lower(),
            description=req.description.strip() if req.description else None,
            deadline=req.deadline,
            start_date=req.start_date,
            location=req.location.strip() if req.location else None,
            work_mode=req.work_mode.strip().lower() if req.work_mode else None,
            minimum_cgpa=round(req.minimum_cgpa, 2) if req.minimum_cgpa is not None else None,
            eligibility=req.eligibility or {},
            compensation=req.compensation.strip() if req.compensation else None,
            application_url=req.application_url.strip() if req.application_url else None,
            status=req.status,
            extraction_confidence=req.extraction_confidence,
        )
        db.add(opp)
        db.flush()

        # Link skills
        skill_reads: List[OpportunitySkillRead] = []
        for s_item in req.skills:
            clean_name = s_item.name.strip()
            if not clean_name:
                continue

            # Find or create canonical Skill
            skill_stmt = select(Skill).where(
                func.lower(Skill.name) == clean_name.lower()
            )
            skill = db.scalars(skill_stmt).first()
            if not skill:
                skill = Skill(name=clean_name)
                db.add(skill)
                db.flush()

            opp_skill = OpportunitySkill(
                opportunity_id=opp.id,
                skill_id=skill.id,
                requirement_type=s_item.requirement_type,
            )
            db.add(opp_skill)
            skill_reads.append(
                OpportunitySkillRead(
                    id=skill.id,
                    name=skill.name,
                    requirement_type=s_item.requirement_type,
                )
            )

        # Link source provenance if provided
        source_reads: List[OpportunitySourceRead] = []
        if req.source_name:
            clean_source_name = req.source_name.strip()
            source_stmt = select(Source).where(
                func.lower(Source.name) == clean_source_name.lower()
            )
            source = db.scalars(source_stmt).first()
            if not source:
                source = Source(
                    name=clean_source_name,
                    source_type="manual",
                )
                db.add(source)
                db.flush()

            opp_source = OpportunitySource(
                opportunity_id=opp.id,
                source_id=source.id,
                source_url=req.source_url.strip() if req.source_url else None,
            )
            db.add(opp_source)
            db.flush()

            source_reads.append(
                OpportunitySourceRead(
                    source_id=source.id,
                    source_name=source.name,
                    source_url=opp_source.source_url,
                    fetched_at=opp_source.fetched_at,
                )
            )

        # Generate vector embedding for semantic search
        from app.services.embedding import embedding_service
        opp.embedding = embedding_service.embed_opportunity(opp)

        db.commit()
        db.refresh(opp)

        return OpportunityDetail(
            id=opp.id,
            title=opp.title,
            organization=opp.organization,
            type=opp.type,
            description=opp.description,
            deadline=opp.deadline,
            start_date=opp.start_date,
            location=opp.location,
            work_mode=opp.work_mode,
            minimum_cgpa=float(opp.minimum_cgpa) if opp.minimum_cgpa is not None else None,
            eligibility=opp.eligibility or {},
            compensation=opp.compensation,
            application_url=opp.application_url,
            status=opp.status,
            skills=skill_reads,
            sources=source_reads,
            created_at=opp.created_at,
            updated_at=opp.updated_at,
        )

    @classmethod
    def get_opportunity_by_id(
        cls,
        db: Session,
        opp_id: UUID,
        student: Optional[User] = None,
    ) -> Optional[OpportunityDetail]:
        """Fetch a single opportunity with attached skills, sources, and evaluated eligibility."""
        stmt = select(Opportunity).where(Opportunity.id == opp_id)
        opp = db.scalars(stmt).first()
        if not opp:
            return None

        # Build skill reads
        skills = [
            OpportunitySkillRead(
                id=os.skill.id,
                name=os.skill.name,
                requirement_type=os.requirement_type,
            )
            for os in opp.skills
        ]

        # Build source reads
        sources = [
            OpportunitySourceRead(
                source_id=src.source.id,
                source_name=src.source.name,
                source_url=src.source_url,
                fetched_at=src.fetched_at,
            )
            for src in opp.sources
        ]

        # Evaluate eligibility if student provided
        eligibility_eval: Optional[EligibilityRead] = None
        if student:
            eval_res = eligibility_engine.evaluate(student, opp)
            eligibility_eval = EligibilityRead(
                status=eval_res.status,
                reasons=eval_res.reasons,
                missing_data=eval_res.missing_data,
            )

        return OpportunityDetail(
            id=opp.id,
            title=opp.title,
            organization=opp.organization,
            type=opp.type,
            description=opp.description,
            deadline=opp.deadline,
            start_date=opp.start_date,
            location=opp.location,
            work_mode=opp.work_mode,
            minimum_cgpa=float(opp.minimum_cgpa) if opp.minimum_cgpa is not None else None,
            eligibility=opp.eligibility or {},
            compensation=opp.compensation,
            application_url=opp.application_url,
            status=opp.status,
            skills=skills,
            sources=sources,
            eligibility_evaluation=eligibility_eval,
            created_at=opp.created_at,
            updated_at=opp.updated_at,
        )

    @classmethod
    def list_opportunities(
        cls,
        db: Session,
        type: Optional[str] = None,
        work_mode: Optional[str] = None,
        location: Optional[str] = None,
        organization: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = "active",
        max_cgpa: Optional[float] = None,
        page: int = 1,
        per_page: int = 20,
        student: Optional[User] = None,
    ) -> OpportunityListResponse:
        """
        Search and filter opportunities with pagination and per-opportunity eligibility calculation.
        """
        page = max(1, page)
        per_page = max(1, min(100, per_page))

        query = select(Opportunity)

        if status:
            query = query.where(Opportunity.status == status.lower())
        if type:
            query = query.where(func.lower(Opportunity.type) == type.lower())
        if work_mode:
            query = query.where(func.lower(Opportunity.work_mode) == work_mode.lower())
        if location:
            query = query.where(Opportunity.location.ilike(f"%{location}%"))
        if organization:
            query = query.where(Opportunity.organization.ilike(f"%{organization}%"))
        if max_cgpa is not None:
            # Opportunities where student meets or exceeds requirement
            query = query.where(
                or_(
                    Opportunity.minimum_cgpa.is_(None),
                    Opportunity.minimum_cgpa <= max_cgpa,
                )
            )
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Opportunity.title.ilike(search_pattern),
                    Opportunity.organization.ilike(search_pattern),
                    Opportunity.description.ilike(search_pattern),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.scalar(count_stmt) or 0

        # Order by deadline ascending (nulls last) then created_at desc
        query = query.order_by(
            Opportunity.deadline.asc().nullslast(),
            Opportunity.created_at.desc(),
        )

        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        opps = db.scalars(query).all()

        items: List[OpportunityRead] = []
        for o in opps:
            eligibility_eval: Optional[EligibilityRead] = None
            if student:
                eval_res = eligibility_engine.evaluate(student, o)
                eligibility_eval = EligibilityRead(
                    status=eval_res.status,
                    reasons=eval_res.reasons,
                    missing_data=eval_res.missing_data,
                )

            items.append(
                OpportunityRead(
                    id=o.id,
                    title=o.title,
                    organization=o.organization,
                    type=o.type,
                    description=o.description,
                    deadline=o.deadline,
                    start_date=o.start_date,
                    location=o.location,
                    work_mode=o.work_mode,
                    minimum_cgpa=float(o.minimum_cgpa) if o.minimum_cgpa is not None else None,
                    eligibility=o.eligibility or {},
                    compensation=o.compensation,
                    application_url=o.application_url,
                    status=o.status,
                    skills=[
                        OpportunitySkillRead(
                            id=os.skill.id,
                            name=os.skill.name,
                            requirement_type=os.requirement_type,
                        )
                        for os in o.skills
                    ],
                    eligibility_evaluation=eligibility_eval,
                    created_at=o.created_at,
                )
            )

        pages = math.ceil(total / per_page) if total > 0 else 0

        return OpportunityListResponse(
            items=items,
            pagination=PaginationMeta(
                total=total,
                page=page,
                per_page=per_page,
                pages=pages,
            ),
        )


opportunity_service = OpportunityService()
