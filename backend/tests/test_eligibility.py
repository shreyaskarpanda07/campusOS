"""
Tests for Deterministic Eligibility Engine (PRD FR-04).
Covers:
- CGPA threshold checks
- Graduation year matches and mismatches
- Degree and Branch matching with synonyms
- Missing data yielding 'uncertain' status
- Ineligibility overriding uncertain criteria
- Integration with Opportunity API
"""

from datetime import date, timedelta
from app.models.opportunity import Opportunity
from app.models.user import User
from app.services.eligibility import eligibility_engine
from app.core.security import get_password_hash, create_access_token


def make_user(
    email="student@univ.edu",
    cgpa=8.5,
    graduation_year=2027,
    current_year=3,
    degree="B.Tech",
    branch="Computer Science",
):
    return User(
        email=email,
        name="Eligible Student",
        password_hash="hash",
        cgpa=cgpa,
        graduation_year=graduation_year,
        current_year=current_year,
        degree=degree,
        branch=branch,
        is_active=True,
    )


def make_opportunity(
    title="SWE Internship",
    minimum_cgpa=7.5,
    eligible_years=[2026, 2027],
    eligible_branches=["Computer Science", "Information Technology"],
    degree_levels=["B.Tech", "B.S."],
):
    return Opportunity(
        title=title,
        organization="Tech Corp",
        type="internship",
        minimum_cgpa=minimum_cgpa,
        eligibility={
            "eligible_years": eligible_years,
            "eligible_branches": eligible_branches,
            "degree_levels": degree_levels,
        },
        status="active",
    )


def test_eligibility_fully_qualified():
    """All criteria met -> status is 'eligible'."""
    user = make_user(cgpa=8.8, graduation_year=2027, branch="Computer Science", degree="B.Tech")
    opp = make_opportunity(minimum_cgpa=7.5, eligible_years=[2026, 2027], eligible_branches=["Computer Science"])

    result = eligibility_engine.evaluate(user, opp)
    assert result.status == "eligible"
    assert result.missing_data == []
    assert any("Meets CGPA requirement" in r for r in result.reasons)
    assert any("Graduation year 2027 is eligible" in r for r in result.reasons)


def test_eligibility_cgpa_cutoff_failed():
    """CGPA below cutoff -> status is 'ineligible'."""
    user = make_user(cgpa=6.9)
    opp = make_opportunity(minimum_cgpa=7.5)

    result = eligibility_engine.evaluate(user, opp)
    assert result.status == "ineligible"
    assert any("CGPA requirement not met" in r for r in result.reasons)


def test_eligibility_graduation_year_mismatch():
    """Graduation year not in list -> status is 'ineligible'."""
    user = make_user(graduation_year=2029)
    opp = make_opportunity(eligible_years=[2026, 2027])

    result = eligibility_engine.evaluate(user, opp)
    assert result.status == "ineligible"
    assert any("Graduation year 2029 is not in eligible batches" in r for r in result.reasons)


def test_eligibility_branch_mismatch():
    """Discipline not in eligible list -> status is 'ineligible'."""
    user = make_user(branch="Civil Engineering")
    opp = make_opportunity(eligible_branches=["Computer Science", "Information Technology"])

    result = eligibility_engine.evaluate(user, opp)
    assert result.status == "ineligible"
    assert any("Discipline 'Civil Engineering' is not in eligible branches" in r for r in result.reasons)


def test_eligibility_branch_synonym_match():
    """Discipline 'Computer Science & Engineering' should match 'Computer Science'."""
    user = make_user(branch="Computer Science & Engineering")
    opp = make_opportunity(eligible_branches=["Computer Science"])

    result = eligibility_engine.evaluate(user, opp)
    assert result.status == "eligible"


def test_eligibility_uncertain_on_missing_profile_data():
    """Missing CGPA and graduation year -> status is 'uncertain', not eliminated."""
    user = make_user(cgpa=None, graduation_year=None)
    opp = make_opportunity(minimum_cgpa=7.5, eligible_years=[2027])

    result = eligibility_engine.evaluate(user, opp)
    assert result.status == "uncertain"
    assert len(result.missing_data) >= 2
    assert any("CGPA not specified" in m for m in result.missing_data)
    assert any("Graduation year not specified" in m for m in result.missing_data)


def test_eligibility_ineligible_overrides_uncertain():
    """If one hard criteria fails (e.g. year), status is 'ineligible' even if CGPA is missing."""
    user = make_user(cgpa=None, graduation_year=2030)
    opp = make_opportunity(minimum_cgpa=8.0, eligible_years=[2026, 2027])

    result = eligibility_engine.evaluate(user, opp)
    assert result.status == "ineligible"
    assert any("Graduation year 2030 is not in eligible batches" in r for r in result.reasons)


def test_eligibility_open_opportunity():
    """Opportunities with no constraints are open and eligible for everyone."""
    user = make_user()
    opp = Opportunity(
        title="Open Hackathon",
        organization="Community",
        type="hackathon",
        minimum_cgpa=None,
        eligibility={},
        status="active",
    )

    result = eligibility_engine.evaluate(user, opp)
    assert result.status == "eligible"
    assert any("open to all students" in r for r in result.reasons)


def test_eligibility_api_integration(client, db):
    """Calling /api/opportunities and detail returns computed eligibility for student."""
    # 1. Create a student with CGPA 9.0, Grad 2027
    user = User(
        email="api_elig_student@univ.edu",
        name="API Student",
        password_hash=get_password_hash("ValidPass123!"),
        cgpa=9.0,
        graduation_year=2027,
        degree="B.Tech",
        branch="Computer Science",
        is_active=True,
    )
    db.add(user)
    db.commit()
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create opportunity with min CGPA 8.0
    opp = Opportunity(
        title="Google AI Residency",
        organization="Google DeepMind",
        type="fellowship",
        minimum_cgpa=8.0,
        eligibility={"eligible_years": [2027]},
        status="active",
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)

    # 3. Query list
    res_list = client.get("/api/opportunities", headers=headers)
    assert res_list.status_code == 200
    items = res_list.json()["data"]["items"]
    target_opp = next((item for item in items if item["id"] == str(opp.id)), None)
    assert target_opp is not None
    assert target_opp["eligibility_evaluation"] is not None
    assert target_opp["eligibility_evaluation"]["status"] == "eligible"

    # 4. Query detail
    res_detail = client.get(f"/api/opportunities/{opp.id}", headers=headers)
    assert res_detail.status_code == 200
    detail_data = res_detail.json()["data"]
    assert detail_data["eligibility_evaluation"]["status"] == "eligible"
    assert any("Meets CGPA requirement" in r for r in detail_data["eligibility_evaluation"]["reasons"])
