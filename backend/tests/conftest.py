"""
Pytest configuration and test fixtures using FastAPI TestClient.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True, scope="session")
def seed_test_database():
    """Ensure the Vayu-Kosh Corridor (VKC) is seeded with standard tasks and topology before tests run."""
    with TestClient(app) as c:
        c.post("/api/v1/gateway/seed/corridor")
