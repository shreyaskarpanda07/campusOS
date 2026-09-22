"""
Tests for Student Profile and Preferences:
- GET /api/users/me
- PATCH /api/users/me
- PUT /api/users/me/skills
- PUT /api/users/me/interests
- Authorization and user data isolation
"""


def register_and_get_token(client, email="student_profile@univ.edu", name="Profile Tester"):
    res = client.post(
        "/api/auth/register",
        json={"email": email, "password": "Password123!", "name": name},
    )
    assert res.status_code == 201
    return res.json()["data"]["access_token"]


def test_get_profile_unauthorized(client):
    """Calling /api/users/me without credentials returns 401."""
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_get_profile_success(client):
    """Calling /api/users/me with valid Bearer token returns empty academic defaults."""
    token = register_and_get_token(client, email="alice@mit.edu", name="Alice Smith")
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@mit.edu"
    assert data["skills"] == []
    assert data["interests"] == []
    assert data["university"] is None
    assert data["cgpa"] is None


def test_patch_profile_academic_fields(client):
    """Updating academic background and preference fields."""
    token = register_and_get_token(client, email="bob@stanford.edu", name="Bob Jones")

    payload = {
        "university": "Stanford University",
        "degree": "B.S.",
        "branch": "Computer Science",
        "graduation_year": 2026,
        "current_year": 3,
        "cgpa": 9.45,
        "preferred_opportunity_types": ["internship", "hackathon"],
        "preferred_work_modes": ["remote", "hybrid"],
        "preferred_locations": ["San Francisco", "Remote"],
    }
    response = client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["university"] == "Stanford University"
    assert data["degree"] == "B.S."
    assert data["branch"] == "Computer Science"
    assert data["graduation_year"] == 2026
    assert data["current_year"] == 3
    assert data["cgpa"] == 9.45
    assert data["preferred_opportunity_types"] == ["internship", "hackathon"]
    assert data["preferred_work_modes"] == ["remote", "hybrid"]
    assert data["preferred_locations"] == ["San Francisco", "Remote"]


def test_patch_profile_validation_errors(client):
    """Validates boundary constraints: CGPA <= 10.0 and current_year <= 6."""
    token = register_and_get_token(client, email="val_test@univ.edu")

    # Invalid CGPA > 10.0
    res1 = client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"cgpa": 11.5},
    )
    assert res1.status_code == 422
    assert res1.json()["error"]["code"] == "VALIDATION_ERROR"

    # Invalid current_year > 6
    res2 = client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_year": 10},
    )
    assert res2.status_code == 422
    assert res2.json()["error"]["code"] == "VALIDATION_ERROR"


def test_put_skills_sync(client):
    """Synchronizing skills replaces the entire list and canonicalizes."""
    token = register_and_get_token(client, email="skills_user@univ.edu")
    headers = {"Authorization": f"Bearer {token}"}

    skills_payload = {
        "skills": [
            {"name": "Python", "proficiency": "advanced"},
            {"name": "FastAPI", "proficiency": "intermediate"},
            {"name": "PostgreSQL"},
        ]
    }
    res = client.put("/api/users/me/skills", headers=headers, json=skills_payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 3
    names = [s["name"] for s in data]
    assert "Python" in names
    assert "FastAPI" in names
    assert "PostgreSQL" in names

    # Verify profile reflects skills
    profile_res = client.get("/api/users/me", headers=headers)
    assert len(profile_res.json()["data"]["skills"]) == 3

    # Replace with updated list (removes PostgreSQL, adds Docker)
    updated_payload = {
        "skills": [
            {"name": "Python", "proficiency": "expert"},
            {"name": "Docker", "proficiency": "beginner"},
        ]
    }
    res2 = client.put("/api/users/me/skills", headers=headers, json=updated_payload)
    assert res2.status_code == 200
    updated_skills = res2.json()["data"]
    assert len(updated_skills) == 2
    updated_names = [s["name"] for s in updated_skills]
    assert "Python" in updated_names
    assert "Docker" in updated_names
    assert "PostgreSQL" not in updated_names


def test_put_interests_sync(client):
    """Synchronizing interests creates canonical interests and links them."""
    token = register_and_get_token(client, email="interests_user@univ.edu")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "interests": [
            {"name": "Machine Learning"},
            {"name": "Open Source"},
        ]
    }
    res = client.put("/api/users/me/interests", headers=headers, json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 2
    names = [i["name"] for i in data]
    assert "Machine Learning" in names
    assert "Open Source" in names

    # Verify in profile
    profile_res = client.get("/api/users/me", headers=headers)
    assert len(profile_res.json()["data"]["interests"]) == 2


def test_profile_isolation_between_users(client):
    """Ensures one user's skills and academic info are never leaked to another user."""
    token_a = register_and_get_token(client, email="user_a@univ.edu", name="User A")
    token_b = register_and_get_token(client, email="user_b@univ.edu", name="User B")

    # User A updates profile and skills
    client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"university": "University A", "cgpa": 9.0},
    )
    client.put(
        "/api/users/me/skills",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"skills": [{"name": "Rust"}]},
    )

    # User B queries their profile
    res_b = client.get("/api/users/me", headers={"Authorization": f"Bearer {token_b}"})
    data_b = res_b.json()["data"]

    assert data_b["name"] == "User B"
    assert data_b["university"] is None
    assert data_b["cgpa"] is None
    assert len(data_b["skills"]) == 0
