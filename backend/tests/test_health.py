"""
Tests for the /api/health endpoint.

Verifies that:
1. The health endpoint returns 200.
2. The response follows the standard ApiResponse shape.
3. The database status is reported correctly.
"""


def test_health_returns_200(client):
    """Health check should return HTTP 200."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_response_shape(client):
    """Health response should follow { data: {...}, error: null } format."""
    response = client.get("/api/health")
    body = response.json()

    assert "data" in body
    assert "error" in body
    assert body["error"] is None


def test_health_data_fields(client):
    """Health data should contain status, database, and version."""
    response = client.get("/api/health")
    data = response.json()["data"]

    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert data["database"] in ("connected", "disconnected")


def test_health_database_connected(client):
    """With test DB available, database should report as connected."""
    response = client.get("/api/health")
    data = response.json()["data"]

    # SQLite test DB is always available
    assert data["database"] == "connected"
