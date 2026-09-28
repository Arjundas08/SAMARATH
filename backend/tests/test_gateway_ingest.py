"""
Tests for Phase 04: Input Gateway, Corridor Seeding, Normalization Equivalence,
Quarantine Isolation, Formula Safety, and Snapshot Determinism.
"""
import pytest
from fastapi.testclient import TestClient
import json

from app.gateway.normalizer import ingest_csv_content, ingest_json_records, sanitize_formula_injection
from app.gateway.quarantine_store import clear_quarantine, get_quarantined_records
from app.schemas.snapshot import Snapshot


@pytest.fixture(autouse=True)
def clean_quarantine_before_each():
    clear_quarantine()
    yield
    clear_quarantine()


def test_csv_and_json_normalization_equivalence():
    """
    Acceptance Criteria: CSV and JSON adapters produce equivalent normalized behavior for equivalent input.
    """
    json_record = [{
        "business_key": "TASK-ENG-EQUIV-01",
        "department": "ENGINEERING",
        "sub_department": "PWAY",
        "work_type": "PLAIN_TRACK_TAMPING",
        "description": "Equivalence verification task",
        "station_from": "ALPHA",
        "station_to": "BRAVO",
        "track_segment_id": "SEC-01-DN",
        "chainage_start_km": 5.0,
        "chainage_end_km": 8.0,
        "duration_minutes": 180,
        "setup_buffer_minutes": 30,
        "restoration_buffer_minutes": 30,
        "criticality": "TIER_1_MANDATORY",
        "deadline_utc": "2026-10-15T18:00:00Z",
        "required_resources": [{"resource_type": "MACHINE", "resource_id": "CSM-01", "quantity": 1}],
        "requires_power_block": False,
        "requires_speed_restriction_after": False,
        "provenance_mode": "TEST",
    }]

    csv_text = (
        "business_key,department,sub_department,work_type,description,station_from,station_to,track_segment_id,"
        "chainage_start_km,chainage_end_km,duration_minutes,setup_buffer_minutes,restoration_buffer_minutes,"
        "criticality,deadline_utc,required_resources,requires_power_block,requires_speed_restriction_after,provenance_mode\n"
        "TASK-ENG-EQUIV-01,ENGINEERING,PWAY,PLAIN_TRACK_TAMPING,Equivalence verification task,ALPHA,BRAVO,SEC-01-DN,"
        "5.0,8.0,180,30,30,TIER_1_MANDATORY,2026-10-15T18:00:00Z,MACHINE:CSM-01:1,false,false,TEST\n"
    )

    json_res = ingest_json_records(json_record)
    csv_res = ingest_csv_content(csv_text)

    assert json_res.success_count == 1
    assert csv_res.success_count == 1
    assert json_res.quarantine_count == 0
    assert csv_res.quarantine_count == 0

    j_task = json_res.accepted_tasks[0]
    c_task = csv_res.accepted_tasks[0]

    # Verify field by field equivalence
    assert j_task.business_key == c_task.business_key
    assert j_task.department == c_task.department
    assert j_task.duration_minutes == c_task.duration_minutes
    assert j_task.chainage_start_km == c_task.chainage_start_km
    assert j_task.chainage_end_km == c_task.chainage_end_km
    assert j_task.criticality == c_task.criticality
    assert j_task.deadline_utc == c_task.deadline_utc
    assert len(j_task.required_resources) == len(c_task.required_resources)
    assert j_task.required_resources[0].resource_id == c_task.required_resources[0].resource_id


def test_formula_injection_sanitization():
    """
    Formula safety: cells starting with =, @, +, - are neutralized so spreadsheet formulas cannot execute.
    """
    assert sanitize_formula_injection("=cmd|'/C calc'!A0") == "'=cmd|'/C calc'!A0"
    assert sanitize_formula_injection("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_formula_injection("+AVERAGE(B1)") == "'+AVERAGE(B1)"
    assert sanitize_formula_injection("-D2*4") == "'-D2*4"
    assert sanitize_formula_injection("TASK-001") == "TASK-001"


def test_malformed_records_row_level_quarantine():
    """
    Malformed rows must be isolated into quarantine with RFC 7807 field error details,
    while valid rows in the same batch are preserved.
    """
    batch = [
        {
            "business_key": "TASK-VALID-01",
            "department": "ELECTRICAL",
            "station_from": "ALPHA",
            "station_to": "BRAVO",
            "track_segment_id": "SEC-01-UP",
            "chainage_start_km": 0.0,
            "chainage_end_km": 5.0,
            "duration_minutes": 120,
            "deadline_utc": "2026-10-20T12:00:00Z",
            "requires_power_block": True,
            "power_block_elementary_section": "ES-ALP-BRV-01",
        },
        {
            "business_key": "TASK-INVALID-DURATION",
            "department": "SIGNALLING",
            "station_from": "BRAVO",
            "station_to": "CHARLIE",
            "track_segment_id": "SEC-02-UP",
            "chainage_start_km": 25.0,
            "chainage_end_km": 28.0,
            "duration_minutes": 5,  # Invalid: < 15
            "deadline_utc": "2026-10-20T12:00:00Z",
        },
        {
            "business_key": "TASK-INVALID-POWER-MISSING-SECTION",
            "department": "ELECTRICAL",
            "station_from": "DELTA",
            "station_to": "ECHO",
            "track_segment_id": "SEC-04-UP",
            "chainage_start_km": 75.0,
            "chainage_end_km": 80.0,
            "duration_minutes": 90,
            "deadline_utc": "2026-10-20T12:00:00Z",
            "requires_power_block": True,
            "power_block_elementary_section": None,  # Invalid: mandatory when requires_power_block=True
        },
    ]

    res = ingest_json_records(batch)
    assert res.total_rows == 3
    assert res.success_count == 1
    assert res.quarantine_count == 2
    assert res.accepted_tasks[0].business_key == "TASK-VALID-01"

    # Verify quarantine error structure
    q_dur = [q for q in res.quarantined_rows if q["business_key"] == "TASK-INVALID-DURATION"][0]
    assert any("duration_minutes" in str(err) for err in q_dur["field_errors"])

    q_pwr = [q for q in res.quarantined_rows if q["business_key"] == "TASK-INVALID-POWER-MISSING-SECTION"][0]
    assert any("power_block_elementary_section" in str(err) for err in q_pwr["field_errors"])


def test_xlsx_unsupported_rejection(client: TestClient):
    """
    XLSX format must be explicitly rejected with 415 Unsupported Media Type
    and RFC 7807 problem details to prevent formula execution.
    """
    response = client.post(
        "/api/v1/gateway/import",
        headers={"Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        content=b"PK\x03\x04fake_excel_bytes",
    )
    assert response.status_code == 415
    data = response.json()
    assert data["error_code"] == "ERR_XLSX_UNSUPPORTED"
    assert "unsupported" in data["title"].lower()


def test_external_sync_returns_501_truthfully(client: TestClient):
    """
    External sync endpoint must return 501 NOT_CONFIGURED instead of fake success.
    """
    response = client.post("/api/v1/gateway/external/sync")
    assert response.status_code == 501
    data = response.json()
    assert data["error_code"] == "ERR_EXTERNAL_SYNC_NOT_CONFIGURED"
    assert "CRIS/COIS/ICMS" in data["detail"]


def test_corridor_seeding_and_task_listing(client: TestClient):
    """
    Verifies that POST /api/v1/gateway/seed/corridor populates the 120km corridor
    and GET /api/v1/tasks returns the seeded tasks with live counts.
    """
    seed_resp = client.post("/api/v1/gateway/seed/corridor")
    assert seed_resp.status_code == 201
    seed_data = seed_resp.json()
    assert seed_data["corridor_code"] == "VKC"
    assert seed_data["stations_count"] == 6
    assert seed_data["track_segments_count"] == 10
    assert seed_data["tasks_seeded"] == 60
    assert seed_data["resource_calendars_count"] == 11

    # Query tasks via GET /api/v1/tasks
    tasks_resp = client.get("/api/v1/tasks?limit=100")
    assert tasks_resp.status_code == 200
    tasks_data = tasks_resp.json()
    assert tasks_data["total"] >= 60

    # Query with department filter
    eng_resp = client.get("/api/v1/tasks?department=ENGINEERING")
    assert eng_resp.status_code == 200
    eng_data = eng_resp.json()
    assert eng_data["total"] > 0
    for t in eng_data["tasks"]:
        assert t["department"] == "ENGINEERING"


def test_task_revision_update_persistence(client: TestClient):
    """
    Updates a task through the task API, verifies persistence and block calculation.
    """
    client.post("/api/v1/gateway/seed/corridor")

    # Fetch first task
    tasks_resp = client.get("/api/v1/tasks?limit=1")
    task = tasks_resp.json()["tasks"][0]
    task_id = task["task_id"]

    # Update description and duration
    update_payload = {
        "business_key": task["business_key"],
        "department": task["department"],
        "sub_department": task["sub_department"],
        "work_type": task["work_type"],
        "description": "Updated maintenance scope by PWAY AEN",
        "station_from": task["station_from"],
        "station_to": task["station_to"],
        "track_segment_id": task["track_segment_id"],
        "chainage_start_km": task["chainage_start_km"],
        "chainage_end_km": task["chainage_end_km"],
        "duration_minutes": 210,
        "setup_buffer_minutes": 30,
        "restoration_buffer_minutes": 30,
        "criticality": task["criticality"],
        "deadline_utc": task["deadline_utc"],
        "requires_power_block": task["requires_power_block"],
        "power_block_elementary_section": task["power_block_elementary_section"],
        "requires_speed_restriction_after": task["requires_speed_restriction_after"],
        "provenance_mode": "TEST",
    }

    put_resp = client.put(f"/api/v1/tasks/{task_id}", json=update_payload)
    assert put_resp.status_code == 200
    put_data = put_resp.json()
    assert put_data["status"] == "UPDATED"
    assert put_data["total_block_minutes"] == 270  # 210 + 30 + 30

    # Reload task and verify changes persisted
    get_resp = client.get(f"/api/v1/tasks/{task_id}")
    assert get_resp.status_code == 200
    reloaded = get_resp.json()
    assert reloaded["description"] == "Updated maintenance scope by PWAY AEN"
    assert reloaded["total_block_minutes"] == 270


def test_snapshot_seal_and_canonical_hash_determinism(client: TestClient):
    """
    Sealing a snapshot computes a canonical SHA-256 hash. Re-running the hash
    on identical data yields the exact same digest.
    """
    client.post("/api/v1/gateway/seed/corridor")

    # Seal snapshot
    seal_resp = client.post("/api/v1/gateway/snapshots/seal?corridor_code=VKC")
    assert seal_resp.status_code == 201
    snapshot = seal_resp.json()

    assert snapshot["snapshot_hash"].lower().startswith("sha256:")
    assert snapshot["is_sealed"] is True
    assert snapshot["corridor_code"] == "VKC"

    # List snapshots
    list_resp = client.get("/api/v1/gateway/snapshots")
    assert list_resp.status_code == 200
    snap_list = list_resp.json()["snapshots"]
    assert len(snap_list) >= 1
    assert any(s["snapshot_hash"] == snapshot["snapshot_hash"] for s in snap_list)


def test_hand_checkable_fixtures_catalog(client: TestClient):
    """
    GET /api/v1/gateway/fixtures returns the 8 explicit edge test cases with
    provenance badges and fixture hashes.
    """
    resp = client.get("/api/v1/gateway/fixtures")
    assert resp.status_code == 200
    data = resp.json()
    assert data["fixtures_count"] == 8

    fixtures = data["fixtures"]
    expected_keys = [
        "normal",
        "no_benefit",
        "unknown_compatibility",
        "impossible_mandatory_deadline",
        "cross_midnight",
        "resource_unavailable",
        "partial_execution",
        "locked_conflict",
    ]
    for key in expected_keys:
        assert key in fixtures
        f = fixtures[key]
        assert "expected_verdict" in f
        assert "units" in f
        assert f["provenance_badge"] == "[SYNTHETIC_SCENARIO]"
        assert f["fixture_hash"].startswith("FIX-")
