"""
Test health endpoint distinguishing process reachability from database status.
"""
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "SAMARATH"
    assert data["process"] == "reachable"
    assert "status" in data
    assert "database" in data
    assert "connected" in data["database"]
    assert "engine" in data["database"]
