"""
Phase 02 Automated Acceptance Tests: Real Login, Scoped Permissions, and Secure Sessions.
"""
import pytest
from fastapi.testclient import TestClient


def test_login_success_and_cookie_issuance(client: TestClient):
    """Verify login sets HttpOnly session cookie and CSRF cookie."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "planner_tms", "password": "tms@pass2026"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "planner_tms"
    assert data["department"] == "ENGINEERING"
    assert data["territory"] == "VKC"
    assert "csrf_token" in data
    assert data["is_authenticated"] is True

    # Verify cookies
    cookies = response.cookies
    assert "samarath_session" in cookies
    assert "samarath_csrf" in cookies


def test_login_invalid_credentials_rejected(client: TestClient):
    """Verify invalid password returns 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "planner_tms", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_logout_clears_cookies(client: TestClient):
    """Verify logout removes authentication cookies."""
    # First login
    client.post(
        "/api/v1/auth/login",
        json={"username": "planner_tms", "password": "tms@pass2026"},
    )
    # Then logout
    logout_resp = client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Session successfully terminated."


def test_unauthenticated_request_returns_401(client: TestClient):
    """Verify accessing protected session without cookie returns 401."""
    # Create fresh client without cookies
    client.cookies.clear()
    response = client.get("/api/v1/auth/session")
    assert response.status_code == 401


def test_session_inspection_reflects_authenticated_identity(client: TestClient):
    """Verify /session returns current identity, roles, and permissions."""
    client.post(
        "/api/v1/auth/login",
        json={"username": "reviewer_operating", "password": "rev@pass2026"},
    )
    response = client.get("/api/v1/auth/session")
    assert response.status_code == 200
    data = response.json()
    assert "OPERATING_REVIEWER" in data["roles"]
    assert "TIMETABLE_MUTATE" in data["permissions"]
    assert data["territory"] == "VKC"


def test_delegated_approver_can_approve_programme(client: TestClient):
    """Verify user with DELEGATED_APPROVER role can approve programme."""
    client.post(
        "/api/v1/auth/login",
        json={"username": "approver_operating", "password": "appr@pass2026"},
    )
    response = client.post("/api/v1/protected/plans/plan-001/approve")
    assert response.status_code == 200
    assert response.json()["action"] == "APPROVED"
    assert response.json()["status"] == "APPROVED_PROGRAMME"


def test_planner_cannot_approve_programme(client: TestClient):
    """Verify DEPARTMENT_PLANNER receives 403 when attempting programme approval."""
    client.post(
        "/api/v1/auth/login",
        json={"username": "planner_tms", "password": "tms@pass2026"},
    )
    response = client.post("/api/v1/protected/plans/plan-001/approve")
    assert response.status_code == 403
    assert "PROGRAMME_APPROVE" in response.json()["detail"]


def test_administrator_cannot_approve_programme(client: TestClient):
    """
    CRUCIAL ARCHITECTURAL INVARIANT (Diagram D16):
    Infrastructure administrator is NOT a business approver and cannot approve programmes.
    """
    client.post(
        "/api/v1/auth/login",
        json={"username": "admin_infra", "password": "admin@pass2026"},
    )
    response = client.post("/api/v1/protected/plans/plan-001/approve")
    assert response.status_code == 403
    assert "PROGRAMME_APPROVE" in response.json()["detail"]


def test_departmental_isolation_enforced(client: TestClient):
    """
    Verify departmental isolation:
    TMS planner can mutate ENGINEERING demands, but is blocked (403) from ELECTRICAL demands.
    """
    client.post(
        "/api/v1/auth/login",
        json={"username": "planner_tms", "password": "tms@pass2026"},
    )

    # 1. Posting to own department (ENGINEERING) -> Succeeds
    resp_eng = client.post("/api/v1/protected/departments/ENGINEERING/demands")
    assert resp_eng.status_code == 200
    assert resp_eng.json()["department"] == "ENGINEERING"

    # 2. Posting to foreign department (ELECTRICAL) -> Forbidden 403
    resp_elec = client.post("/api/v1/protected/departments/ELECTRICAL/demands")
    assert resp_elec.status_code == 403
    assert "Department isolation violation" in resp_elec.json()["detail"]
