"""
Tests for Opportunity CRUD, Search, Filters, and Role-Based Authorization.
"""

from datetime import date, timedelta
from app.models.user import User
from app.core.security import get_password_hash, create_access_token


def create_user_token(db, email: str, is_admin: bool = False) -> str:
    user = User(
        email=email,
        name="Test User",
        password_hash=get_password_hash("ValidPass123!"),
        is_admin=is_admin,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return create_access_token({"sub": str(user.id)})


def sample_opp_payload():
    return {
        "title": "Software Engineering Intern",
        "organization": "Google",
        "type": "internship",
        "description": "Distributed systems engineering",
        "deadline": str(date.today() + timedelta(days=10)),
        "location": "Mountain View, CA",
        "work_mode": "hybrid",
        "minimum_cgpa": 7.5,
        "eligibility": {"eligible_years": [2026, 2027]},
        "compensation": "$55/hr",
        "application_url": "https://careers.google.com/jobs/1",
        "source_name": "Google Careers",
        "source_url": "https://careers.google.com",
        "skills": [
            {"name": "Python", "requirement_type": "required"},
            {"name": "C++", "requirement_type": "preferred"},
        ],
    }


def test_create_opportunity_admin_protection(client, db):
    """Only administrator accounts can create opportunities."""
    student_token = create_user_token(db, "student@univ.edu", is_admin=False)
    payload = sample_opp_payload()

    # Student cannot create opportunity -> 403
    res_student = client.post(
        "/api/opportunities",
        headers={"Authorization": f"Bearer {student_token}"},
        json=payload,
    )
    assert res_student.status_code == 403
    assert res_student.json()["error"]["code"] == "FORBIDDEN"

    # Unauthenticated cannot create -> 401
    res_anon = client.post("/api/opportunities", json=payload)
    assert res_anon.status_code == 401


def test_create_opportunity_admin_success(client, db):
    """Admin can create opportunity with skills and source provenance."""
    admin_token = create_user_token(db, "admin@campusos.internal", is_admin=True)
    payload = sample_opp_payload()

    response = client.post(
        "/api/opportunities",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload,
    )
    assert response.status_code == 201
    data = response.json()["data"]

    assert data["title"] == "Software Engineering Intern"
    assert data["organization"] == "Google"
    assert data["type"] == "internship"
    assert data["work_mode"] == "hybrid"
    assert data["minimum_cgpa"] == 7.5
    assert len(data["skills"]) == 2
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source_name"] == "Google Careers"
    assert data["sources"][0]["source_url"] == "https://careers.google.com"


def test_get_opportunity_by_id(client, db):
    """Retrieve full opportunity detail by ID."""
    admin_token = create_user_token(db, "admin2@campusos.internal", is_admin=True)
    student_token = create_user_token(db, "student2@univ.edu", is_admin=False)

    create_res = client.post(
        "/api/opportunities",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=sample_opp_payload(),
    )
    opp_id = create_res.json()["data"]["id"]

    # Student can read detail
    res = client.get(
        f"/api/opportunities/{opp_id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["id"] == opp_id
    assert data["organization"] == "Google"

    # Non-existent ID returns 404
    missing_res = client.get(
        "/api/opportunities/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert missing_res.status_code == 404
    assert missing_res.json()["error"]["code"] == "OPPORTUNITY_NOT_FOUND"


def test_list_opportunities_filters(client, db):
    """Test filtering opportunities by type, work mode, and search keyword."""
    admin_token = create_user_token(db, "admin3@campusos.internal", is_admin=True)
    student_token = create_user_token(db, "student3@univ.edu", is_admin=False)
    headers_student = {"Authorization": f"Bearer {student_token}"}
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # Create 3 distinct opportunities
    opp1 = sample_opp_payload()
    opp1["title"] = "SWE Intern"
    opp1["type"] = "internship"
    opp1["work_mode"] = "remote"

    opp2 = sample_opp_payload()
    opp2["title"] = "Deloitte Case Challenge"
    opp2["organization"] = "Deloitte"
    opp2["type"] = "competition"
    opp2["work_mode"] = "onsite"

    opp3 = sample_opp_payload()
    opp3["title"] = "HackMIT 2026"
    opp3["organization"] = "MIT"
    opp3["type"] = "hackathon"
    opp3["work_mode"] = "hybrid"

    client.post("/api/opportunities", headers=headers_admin, json=opp1)
    client.post("/api/opportunities", headers=headers_admin, json=opp2)
    client.post("/api/opportunities", headers=headers_admin, json=opp3)

    # Filter by type=competition
    res_type = client.get("/api/opportunities?type=competition", headers=headers_student)
    assert res_type.status_code == 200
    items = res_type.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["organization"] == "Deloitte"

    # Filter by work_mode=remote
    res_mode = client.get("/api/opportunities?work_mode=remote", headers=headers_student)
    assert res_mode.status_code == 200
    items_mode = res_mode.json()["data"]["items"]
    assert len(items_mode) == 1
    assert items_mode[0]["title"] == "SWE Intern"

    # Search keyword
    res_search = client.get("/api/opportunities?search=HackMIT", headers=headers_student)
    assert res_search.status_code == 200
    items_search = res_search.json()["data"]["items"]
    assert len(items_search) == 1
    assert items_search[0]["title"] == "HackMIT 2026"


def test_list_opportunities_pagination(client, db):
    """Pagination metadata and item counts."""
    admin_token = create_user_token(db, "admin4@campusos.internal", is_admin=True)
    student_token = create_user_token(db, "student4@univ.edu", is_admin=False)

    for i in range(5):
        opp = sample_opp_payload()
        opp["title"] = f"Opportunity {i+1}"
        client.post(
            "/api/opportunities",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=opp,
        )

    res = client.get(
        "/api/opportunities?page=1&per_page=2",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data["items"]) == 2
    assert data["pagination"]["total"] == 5
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 2
    assert data["pagination"]["pages"] == 3
