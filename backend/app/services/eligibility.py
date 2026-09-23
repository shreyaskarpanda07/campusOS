"""
Deterministic Eligibility Engine (PRD FR-04).

Evaluates hard academic, graduation, and qualification constraints
before recommendation ranking. Returns a tri-state status:
- 'eligible': All known criteria satisfied
- 'ineligible': One or more hard criteria failed
- 'uncertain': Missing information in user profile or opportunity
"""

import re
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel

from app.models.opportunity import Opportunity
from app.models.user import User


class EligibilityResult(BaseModel):
    """Evaluation outcome with human-readable reasoning."""

    status: Literal["eligible", "ineligible", "uncertain"]
    reasons: List[str]
    missing_data: List[str]


def _normalize(text: Optional[str]) -> str:
    """Normalize text for case- and punctuation-insensitive matching."""
    if not text:
        return ""
    return re.sub(r"[^\w\s]", "", text.strip().lower())


def _branch_matches(user_branch: str, eligible_branches: List[str]) -> bool:
    """Check if student's branch matches eligible branches (handles partial/synonym matches)."""
    norm_user = _normalize(user_branch)
    for branch in eligible_branches:
        norm_eligible = _normalize(branch)
        if norm_eligible in ["all", "all branches", "any"]:
            return True
        if norm_user in norm_eligible or norm_eligible in norm_user:
            return True
        # Common synonyms
        if "cs" in norm_user.split() and "computer science" in norm_eligible:
            return True
        if "computer science" in norm_user and "cs" in norm_eligible.split():
            return True
        if "it" in norm_user.split() and "information technology" in norm_eligible:
            return True
        if "ece" in norm_user.split() and "electronics" in norm_eligible:
            return True
    return False


def _degree_matches(user_degree: str, eligible_degrees: List[str]) -> bool:
    """Check if student's degree matches eligible degrees."""
    norm_user = _normalize(user_degree)
    for deg in eligible_degrees:
        norm_deg = _normalize(deg)
        if norm_deg in ["all", "all degrees", "any", "undergraduate"]:
            return True
        if norm_user == norm_deg or norm_user in norm_deg or norm_deg in norm_user:
            return True
    return False


class EligibilityEngine:
    """Deterministic, rule-based qualification checker."""

    @classmethod
    def evaluate(
        cls,
        user: Optional[User],
        opportunity: Opportunity,
    ) -> EligibilityResult:
        """
        Evaluate student eligibility against an opportunity.

        If user is not provided (anonymous browsing), returns 'uncertain'.
        """
        if not user:
            return EligibilityResult(
                status="uncertain",
                reasons=["Sign in and complete your academic profile to verify eligibility."],
                missing_data=["Authentication required"],
            )

        eligibility_data: Dict[str, Any] = opportunity.eligibility or {}
        reasons: List[str] = []
        missing_data: List[str] = []
        is_ineligible = False

        # ── 1. Minimum CGPA Check ──────────────────────────────────────
        if opportunity.minimum_cgpa is not None:
            min_cgpa = float(opportunity.minimum_cgpa)
            if user.cgpa is None:
                missing_data.append("CGPA not specified in student profile")
                reasons.append(f"Requires minimum CGPA of {min_cgpa:.2f} (your CGPA is missing)")
            else:
                user_cgpa = float(user.cgpa)
                if user_cgpa < min_cgpa:
                    is_ineligible = True
                    reasons.append(
                        f"CGPA requirement not met: minimum {min_cgpa:.2f} required, your CGPA is {user_cgpa:.2f}"
                    )
                else:
                    reasons.append(f"Meets CGPA requirement: {user_cgpa:.2f} >= {min_cgpa:.2f}")

        # ── 2. Eligible Graduation Years Check ────────────────────────
        eligible_years = eligibility_data.get("eligible_years")
        if eligible_years and isinstance(eligible_years, list) and len(eligible_years) > 0:
            if user.graduation_year is None:
                missing_data.append("Graduation year not specified in student profile")
                reasons.append(f"Eligible graduation years: {', '.join(str(y) for y in eligible_years)}")
            else:
                if user.graduation_year not in eligible_years:
                    is_ineligible = True
                    reasons.append(
                        f"Graduation year {user.graduation_year} is not in eligible batches ({', '.join(str(y) for y in eligible_years)})"
                    )
                else:
                    reasons.append(f"Graduation year {user.graduation_year} is eligible")

        # ── 3. Current Year of Study Check ────────────────────────────
        eligible_current_years = eligibility_data.get("eligible_current_years")
        if (
            eligible_current_years
            and isinstance(eligible_current_years, list)
            and len(eligible_current_years) > 0
        ):
            if user.current_year is None:
                missing_data.append("Current year of study not specified in student profile")
                reasons.append(f"Eligible years of study: {', '.join(str(y) for y in eligible_current_years)}")
            else:
                if user.current_year not in eligible_current_years:
                    is_ineligible = True
                    reasons.append(
                        f"Current year {user.current_year} is not eligible ({', '.join(str(y) for y in eligible_current_years)})"
                    )
                else:
                    reasons.append(f"Current year {user.current_year} is eligible")

        # ── 4. Eligible Degree Check ──────────────────────────────────
        eligible_degrees = eligibility_data.get("degree_levels")
        if (
            eligible_degrees
            and isinstance(eligible_degrees, list)
            and len(eligible_degrees) > 0
        ):
            if not any(_normalize(d) in ["all", "all degrees", "any"] for d in eligible_degrees):
                if not user.degree:
                    missing_data.append("Degree not specified in student profile")
                    reasons.append(f"Eligible degree levels: {', '.join(eligible_degrees)}")
                else:
                    if not _degree_matches(user.degree, eligible_degrees):
                        is_ineligible = True
                        reasons.append(
                            f"Degree '{user.degree}' is not in eligible degrees ({', '.join(eligible_degrees)})"
                        )
                    else:
                        reasons.append(f"Degree '{user.degree}' is eligible")

        # ── 5. Eligible Branches / Disciplines Check ──────────────────
        eligible_branches = eligibility_data.get("eligible_branches")
        if (
            eligible_branches
            and isinstance(eligible_branches, list)
            and len(eligible_branches) > 0
        ):
            if not any(_normalize(b) in ["all", "all branches", "any"] for b in eligible_branches):
                if not user.branch:
                    missing_data.append("Branch / major not specified in student profile")
                    reasons.append(f"Eligible disciplines: {', '.join(eligible_branches)}")
                else:
                    if not _branch_matches(user.branch, eligible_branches):
                        is_ineligible = True
                        reasons.append(
                            f"Discipline '{user.branch}' is not in eligible branches ({', '.join(eligible_branches)})"
                        )
                    else:
                        reasons.append(f"Discipline '{user.branch}' is eligible")

        # ── Decision Synthesis ────────────────────────────────────────
        if is_ineligible:
            final_status = "ineligible"
        elif len(missing_data) > 0:
            final_status = "uncertain"
        else:
            final_status = "eligible"
            if len(reasons) == 0:
                reasons.append("No restrictive academic criteria specified; open to all students.")

        return EligibilityResult(
            status=final_status,
            reasons=reasons,
            missing_data=missing_data,
        )


eligibility_engine = EligibilityEngine()
