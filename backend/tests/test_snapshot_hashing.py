"""
Test deterministic canonical Snapshot hashing.
Verifies sorted membership, explicit timestamp representation, and hash sensitivity.
"""
from datetime import datetime
from app.schemas.snapshot import Snapshot, TrainOccupation, ResourceCalendarEntry
from app.schemas.task import Task, TaskCreate
from app.schemas.enums import DepartmentType, CriticalityTier, ProvenanceMode


def test_snapshot_hashing_determinism_under_permutation():
    # Create two tasks
    t1 = Task.from_create(
        TaskCreate(
            business_key="TASK-A",
            department=DepartmentType.ENGINEERING,
            sub_department="PWAY",
            work_type="TAMPING",
            description="Task A",
            station_from="ALP",
            station_to="BRV",
            track_segment_id="SEC-01-UP",
            chainage_start_km=5.0,
            chainage_end_km=8.0,
            duration_minutes=120,
            deadline_utc=datetime.fromisoformat("2026-10-18T23:59:59Z"),
        )
    )
    t2 = Task.from_create(
        TaskCreate(
            business_key="TASK-B",
            department=DepartmentType.ELECTRICAL,
            sub_department="TRD",
            work_type="OHE",
            description="Task B",
            station_from="BRV",
            station_to="CHR",
            track_segment_id="SEC-02-UP",
            chainage_start_km=25.0,
            chainage_end_km=28.0,
            duration_minutes=90,
            deadline_utc=datetime.fromisoformat("2026-10-18T23:59:59Z"),
        )
    )

    # Snapshot 1 with [t1, t2]
    s1 = Snapshot(
        horizon_start_utc=datetime.fromisoformat("2026-10-12T00:00:00Z"),
        horizon_end_utc=datetime.fromisoformat("2026-10-18T23:59:59Z"),
        provenance_mode=ProvenanceMode.TEST,
        tasks=[t1, t2],
    )

    # Snapshot 2 with [t2, t1] (permuted order)
    s2 = Snapshot(
        horizon_start_utc=datetime.fromisoformat("2026-10-12T00:00:00Z"),
        horizon_end_utc=datetime.fromisoformat("2026-10-18T23:59:59Z"),
        provenance_mode=ProvenanceMode.TEST,
        tasks=[t2, t1],
    )

    hash1 = s1.compute_canonical_hash()
    hash2 = s2.compute_canonical_hash()

    assert hash1.startswith("sha256:")
    assert hash1 == hash2, "Snapshots with identical contents in different order must yield identical hash"


def test_snapshot_hashing_changes_on_content_revision():
    t1 = Task.from_create(
        TaskCreate(
            business_key="TASK-A",
            department=DepartmentType.ENGINEERING,
            sub_department="PWAY",
            work_type="TAMPING",
            description="Task A",
            station_from="ALP",
            station_to="BRV",
            track_segment_id="SEC-01-UP",
            chainage_start_km=5.0,
            chainage_end_km=8.0,
            duration_minutes=120,
            deadline_utc=datetime.fromisoformat("2026-10-18T23:59:59Z"),
        )
    )
    t1_modified = Task.from_create(
        TaskCreate(
            business_key="TASK-A",
            department=DepartmentType.ENGINEERING,
            sub_department="PWAY",
            work_type="TAMPING",
            description="Task A",
            station_from="ALP",
            station_to="BRV",
            track_segment_id="SEC-01-UP",
            chainage_start_km=5.0,
            chainage_end_km=8.0,
            duration_minutes=180,  # Changed duration from 120 to 180
            deadline_utc=datetime.fromisoformat("2026-10-18T23:59:59Z"),
        )
    )

    s1 = Snapshot(
        horizon_start_utc=datetime.fromisoformat("2026-10-12T00:00:00Z"),
        horizon_end_utc=datetime.fromisoformat("2026-10-18T23:59:59Z"),
        tasks=[t1],
    )
    s2 = Snapshot(
        horizon_start_utc=datetime.fromisoformat("2026-10-12T00:00:00Z"),
        horizon_end_utc=datetime.fromisoformat("2026-10-18T23:59:59Z"),
        tasks=[t1_modified],
    )

    assert s1.compute_canonical_hash() != s2.compute_canonical_hash()
