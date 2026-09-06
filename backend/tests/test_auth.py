"""
Tests for Authentication: Security utilities, Registration, Login, and Logout.
"""

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    """Verify password hashing and matching."""
    plain = "SuperSecret123!"
    hashed = get_password_hash(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_generation_and_decoding():
    """Verify JWT token encoding and decoding."""
    payload = {"sub": "12345-test-user-id", "role": "student"}
    token = create_access_token(payload)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "12345-test-user-id"
    assert decoded["role"] == "student"
    assert "exp" in decoded

    # Tampered token should return None
    assert decode_access_token(token + "tampered") is None


def test_register_user_success(client):
    """Registering a new valid user should succeed with 201 and return user + token."""
    payload = {
        "email": "student@university.edu",
        "password": "Password123!",
        "name": "Jane Doe",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["error"] is None
    data = body["data"]
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    user = data["user"]
    assert user["email"] == "student@university.edu"
    assert user["name"] == "Jane Doe"
    assert "id" in user
    assert "password_hash" not in user
    assert user["is_admin"] is False


def test_register_duplicate_email(client):
    """Registering an existing email must return 409 EMAIL_TAKEN."""
    payload = {
        "email": "duplicate@university.edu",
        "password": "Password123!",
        "name": "First User",
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt to register again
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    body = res2.json()
    assert body["data"] is None
    assert body["error"]["code"] == "EMAIL_TAKEN"


def test_register_short_password(client):
    """Registering with password < 8 chars must fail with 422 VALIDATION_ERROR."""
    payload = {
        "email": "shortpass@university.edu",
        "password": "short",
        "name": "Short Pass",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_login_success(client):
    """Login with valid credentials returns 200 and access token."""
    reg_payload = {
        "email": "login_test@university.edu",
        "password": "ValidPassword123!",
        "name": "Login Tester",
    }
    client.post("/api/auth/register", json=reg_payload)

    login_payload = {
        "email": "login_test@university.edu",
        "password": "ValidPassword123!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["error"] is None
    data = body["data"]
    assert "access_token" in data
    assert data["user"]["email"] == "login_test@university.edu"


def test_login_invalid_password(client):
    """Login with incorrect password returns 401 INVALID_CREDENTIALS."""
    reg_payload = {
        "email": "wrong_pwd@university.edu",
        "password": "ValidPassword123!",
        "name": "Wrong Password",
    }
    client.post("/api/auth/register", json=reg_payload)

    login_payload = {
        "email": "wrong_pwd@university.edu",
        "password": "IncorrectPassword!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_user(client):
    """Login with unknown email returns 401 INVALID_CREDENTIALS."""
    login_payload = {
        "email": "does_not_exist@university.edu",
        "password": "AnyPassword123!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_logout_authenticated(client):
    """Authenticated user calling logout should receive 200."""
    reg_payload = {
        "email": "logout_test@university.edu",
        "password": "ValidPassword123!",
        "name": "Logout Tester",
    }
    res = client.post("/api/auth/register", json=reg_payload)
    token = res.json()["data"]["access_token"]

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert "Successfully logged out" in body["data"]["message"]


def test_logout_unauthenticated(client):
    """Unauthenticated call to logout must return 401 UNAUTHORIZED."""
    response = client.post("/api/auth/logout")
    assert response.status_code == 401
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "UNAUTHORIZED"
