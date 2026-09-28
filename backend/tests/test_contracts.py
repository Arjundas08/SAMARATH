"""
Test typed Pydantic contracts, unit validations, and RFC 7807 error handling.
"""
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.schemas.task import Task, TaskCreate
from app.schemas.enums import DepartmentType, CriticalityTier, DemandStatus, ProvenanceMode


def test_task_valid_creation():
    create_dto = TaskCreate(
        business_key="TASK-TEST-0001",
        department=DepartmentType.ENGINEERING,
        sub_department="PWAY",
        work_type="TAMPING",
        description="Plain track tamping",
        station_from="ALP",
        station_to="BRV",
        track_segment_id="SEC-01-UP",
        chainage_start_km=10.0,
        chainage_end_km=12.5,
        duration_minutes=150,
        setup_buffer_minutes=30,
        restoration_buffer_minutes=30,
        criticality=CriticalityTier.TIER_2_SPEED_RESTRICTION,
        deadline_utc=datetime(2026, 10, 18, 23, 59, 59, tzinfo=timezone.utc),
        requires_power_block=False,
    )
    task = Task.from_create(create_dto)
    assert task.total_block_minutes == 210  # 150 + 30 + 30
    assert task.demand_status == DemandStatus.VALIDATED
    assert task.provenance_mode == ProvenanceMode.TEST


def test_task_invalid_chainage_rejection():
    with pytest.raises(ValidationError):
        TaskCreate(
            business_key="TASK-TEST-0002",
            department=DepartmentType.ENGINEERING,
            sub_department="PWAY",
            work_type="TAMPING",
            description="Invalid chainage",
            station_from="ALP",
            station_to="BRV",
            track_segment_id="SEC-01-UP",
            chainage_start_km=15.0,
            chainage_end_km=10.0,  # Invalid: end < start
            duration_minutes=120,
            deadline_utc=datetime(2026, 10, 18, 23, 59, 59, tzinfo=timezone.utc),
        )


def test_task_power_block_missing_section():
    with pytest.raises(ValidationError):
        TaskCreate(
            business_key="TASK-TEST-0003",
            department=DepartmentType.ELECTRICAL,
            sub_department="TRD",
            work_type="OHE_INSPECTION",
            description="Power block without section",
            station_from="ALP",
            station_to="BRV",
            track_segment_id="SEC-01-UP",
            chainage_start_km=5.0,
            chainage_end_km=8.0,
            duration_minutes=120,
            requires_power_block=True,
            power_block_elementary_section=None,  # Missing mandatory elementary section
            deadline_utc=datetime(2026, 10, 18, 23, 59, 59, tzinfo=timezone.utc),
        )


def test_rfc7807_validation_error_response(client: TestClient):
    # Send empty payload to trigger 422
    response = client.post("/api/v1/tasks", json={})
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    problem = response.json()
    assert problem["error_code"] == "ERR_VALIDATION_FAILED"
    assert "invalid_params" in problem
    assert len(problem["invalid_params"]) > 0
