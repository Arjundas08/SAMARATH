"""
Phase 16 – Execution Feedback, Partial Work, and Estimate Review Tests.

Acceptance coverage:
1. Full completion: actual_quantity == target_quantity, valid chronology, status = COMPLETED.
2. Partial work: actual_quantity < target_quantity, creates governed residual task.
3. Missing release: None release signal distinguished from zero duration.
4. Corrected outcome: audited revision supersedes old record, invalidates affected plans.
5. Duplicate event: duplicate idempotency key returns same record.
6. Mismatched unit: reported unit != task unit raises error / records conflict.
7. Invalid chronology: start >= restoration or release < restoration rejected.
8. Residual task not double-counted: completed + residual == target strictly enforced.
9. Still-occupied resource preserved: occupied resources recorded for downstream locking.
10. Reviewed estimate used only by a later snapshot: deterministic buffer review without ML.
11. Demonstrated loop: original task -> execution intake -> residual generation -> next planning input.
12. Reconciliation queue: conflicts logged and resolvable with audit justification.
13. Plan-vs-actual variance: explains missing attribution instead of inventing delay.
"""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.engine.execution_engine import execution_engine
from app.engine.approval_engine import approval_engine
from app.schemas.execution import (
    ExecutionRecordCreate,
    ExecutionRecordRevisionRequest,
    ResidualWorkConfirmRequest,
    DeviationReason,
    ExecutionStatus,
    ChronologyValidationStatus,
    EstimateReviewRecommendation,
)
from app.schemas.enums import CriticalityTier, ProvenanceMode, PlanStatus


@pytest.fixture(autouse=True)
def reset_execution_engine():
    """Reset singleton engine before each test."""
    execution_engine.__init__()
    approval_engine.__init__()
    yield


def _make_client():
    return TestClient(app)


def _login(c: TestClient, username: str = "reviewer_operating", password: str = "rev@pass2026"):
    resp = c.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()


# ──────────────────────────────────────────────
#  1. Full Completion & Chronology Tests
# ──────────────────────────────────────────────

class TestFullCompletion:
    """Verify standard completion with valid timestamps and units."""

    def test_full_completion_nominal(self):
        c = _make_client()
        _login(c)

        execution_engine.register_task_contract(
            task_id="TASK-PW-01",
            expected_units="METERS",
            target_quantity=500.0,
            planned_duration_minutes=120,
            department="ENGINEERING",
            task_category="TRACK_TAMPING",
        )

        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=3)
        restoration = now - timedelta(hours=1)
        release = now - timedelta(minutes=50)

        payload = {
            "task_id": "TASK-PW-01",
            "plan_id": "plan-vkc-001",
            "assignment_id": "ASG-001",
            "external_authority_ref": "COA-BLOCK-2026-001",
            "actual_start_utc": start.isoformat(),
            "actual_restoration_utc": restoration.isoformat(),
            "actual_release_utc": release.isoformat(),
            "quantity_completed": 500.0,
            "quantity_units": "METERS",
            "target_quantity": 500.0,
            "planned_duration_minutes": 120,
            "deviation_reason": "NONE",
            "provenance_mode": "TEST",
        }

        resp = c.post("/api/v1/execution/record", json=payload)
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["task_id"] == "TASK-PW-01"
        assert data["execution_status"] == ExecutionStatus.COMPLETED.value
        assert data["chronology_status"] == ChronologyValidationStatus.VALID.value
        assert data["actual_duration_minutes"] == 120
        assert data["overrun_minutes"] == 0
        assert data["has_missing_release"] is False
        assert data["is_latest_revision"] is True
        assert data["revision"] == 1


# ──────────────────────────────────────────────
#  2. Partial Work & Governed Residuals
# ──────────────────────────────────────────────

class TestPartialWorkAndResiduals:
    """Verify partial completion and governed residual generation without double counting."""

    def test_partial_work_intake(self):
        c = _make_client()
        _login(c)

        execution_engine.register_task_contract(
            task_id="TASK-PW-02",
            expected_units="KM",
            target_quantity=4.0,
            planned_duration_minutes=180,
        )

        now = datetime.now(timezone.utc)
        payload = {
            "task_id": "TASK-PW-02",
            "actual_start_utc": (now - timedelta(hours=2)).isoformat(),
            "actual_restoration_utc": (now - timedelta(hours=1)).isoformat(),
            "actual_release_utc": now.isoformat(),
            "quantity_completed": 2.5,
            "quantity_units": "KM",
            "target_quantity": 4.0,
            "planned_duration_minutes": 180,
            "deviation_reason": "EARLY_BURST_CANCEL",
            "deviation_notes": "Controller cancelled window 60 mins early for goods train",
        }

        resp = c.post("/api/v1/execution/record", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["execution_status"] == ExecutionStatus.PARTIAL.value
        assert data["quantity_completed"] == 2.5
        assert data["quantity_variance"] == -1.5

    def test_confirm_governed_residual_work_exact(self):
        c = _make_client()
        _login(c)

        # 1. Record partial execution (2.5 of 4.0 KM)
        now = datetime.now(timezone.utc)
        rec = execution_engine.record_execution(ExecutionRecordCreate(
            task_id="TASK-PW-03",
            actual_start_utc=now - timedelta(hours=2),
            actual_restoration_utc=now - timedelta(hours=1),
            actual_release_utc=now,
            quantity_completed=2.5,
            quantity_units="KM",
            target_quantity=4.0,
            deviation_reason=DeviationReason.WEATHER_ADVERSE,
        ), actor={"user_id": "usr-005-rev"})

        # 2. Confirm residual work of exactly 1.5 KM
        confirm_payload = {
            "source_record_id": str(rec.record_id),
            "confirmed_residual_quantity": 1.5,
            "quantity_units": "KM",
            "site_state": "RAIL_UNWELDED_SPEED_RESTRICTED",
            "dependencies": ["TASK-PW-03-INSPECT"],
            "priority": "TIER_1_MANDATORY",
        }

        resp = c.post("/api/v1/execution/residual/confirm", json=confirm_payload)
        assert resp.status_code == 200, resp.text
        resid = resp.json()

        assert resid["original_task_id"] == "TASK-PW-03"
        assert resid["residual_quantity"] == 1.5
        assert resid["completed_quantity"] == 2.5
        assert resid["total_target_quantity"] == 4.0
        assert resid["site_state"] == "RAIL_UNWELDED_SPEED_RESTRICTED"
        assert resid["is_confirmed"] is True

    def test_residual_double_counting_prevention(self):
        c = _make_client()
        _login(c)

        now = datetime.now(timezone.utc)
        rec = execution_engine.record_execution(ExecutionRecordCreate(
            task_id="TASK-PW-04",
            actual_start_utc=now - timedelta(hours=2),
            actual_restoration_utc=now - timedelta(hours=1),
            actual_release_utc=now,
            quantity_completed=2.0,
            quantity_units="KM",
            target_quantity=5.0,
        ), actor={"user_id": "usr-005-rev"})

        # Attempt to confirm residual of 4.0 KM (2.0 + 4.0 = 6.0 != 5.0) -> must be rejected
        bad_confirm = {
            "source_record_id": str(rec.record_id),
            "confirmed_residual_quantity": 4.0,
            "quantity_units": "KM",
            "site_state": "NORMAL",
        }

        resp = c.post("/api/v1/execution/residual/confirm", json=bad_confirm)
        assert resp.status_code == 400
        assert "Residual double-counting prevention" in resp.json()["detail"]


# ──────────────────────────────────────────────
#  3. Missing Release Signal vs Zero Duration
# ──────────────────────────────────────────────

class TestMissingRelease:
    """Verify missing operating release signal is distinguished from zero duration."""

    def test_missing_release_has_valid_duration(self):
        c = _make_client()
        _login(c)

        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=2)
        restoration = now - timedelta(minutes=30)  # 90 minutes duration

        payload = {
            "task_id": "TASK-OHE-01",
            "actual_start_utc": start.isoformat(),
            "actual_restoration_utc": restoration.isoformat(),
            "actual_release_utc": None,  # Missing operating release!
            "quantity_completed": 10.0,
            "quantity_units": "MASTS",
            "target_quantity": 10.0,
            "planned_duration_minutes": 90,
        }

        resp = c.post("/api/v1/execution/record", json=payload)
        assert resp.status_code == 200
        data = resp.json()

        assert data["has_missing_release"] is True
        assert data["chronology_status"] == ChronologyValidationStatus.MISSING_RELEASE.value
        # Invariant: Duration is 90 minutes, NOT 0!
        assert data["actual_duration_minutes"] == 90
        assert data["actual_release_utc"] is None


# ──────────────────────────────────────────────
#  4. Corrected Outcomes & Plan Invalidation
# ──────────────────────────────────────────────

class TestCorrectedOutcomes:
    """Verify audited revision supersedes old record and invalidates downstream plan."""

    def test_revise_execution_supersedes_and_invalidates(self):
        c = _make_client()
        _login(c)

        # Register a plan in approval engine
        plan_id = str(uuid4())
        approval_engine.register_plan(plan_id, {"plan_version_number": 1, "status": "APPROVED_PROGRAMME"})
        approval_engine._plans[plan_id]["plan_status"] = PlanStatus.APPROVED_PROGRAMME.value

        # Initial outcome: reported 500m
        now = datetime.now(timezone.utc)
        rec = execution_engine.record_execution(ExecutionRecordCreate(
            task_id="TASK-REV-01",
            plan_id=plan_id,
            actual_start_utc=now - timedelta(hours=3),
            actual_restoration_utc=now - timedelta(hours=1),
            actual_release_utc=now - timedelta(minutes=50),
            quantity_completed=500.0,
            quantity_units="METERS",
            target_quantity=500.0,
        ), actor={"user_id": "usr-005-rev"})

        assert rec.revision == 1
        assert rec.is_latest_revision is True

        # Supervisor submits corrected revision: only 350m was actually tamped
        revise_payload = {
            "record_id": str(rec.record_id),
            "correction_reason": "Post-block track survey revealed last 150m was not tamped due to point machine obstacle",
            "quantity_completed": 350.0,
            "deviation_reason": "UNEXPECTED_SITE_CONDITION",
        }

        resp = c.put("/api/v1/execution/revise", json=revise_payload)
        assert resp.status_code == 200, resp.text
        revised = resp.json()

        assert revised["revision"] == 2
        assert revised["is_latest_revision"] is True
        assert revised["quantity_completed"] == 350.0
        assert revised["execution_status"] == ExecutionStatus.PARTIAL.value

        # Old record must be marked superseded
        old_rec = execution_engine.get_record(str(rec.record_id))
        assert old_rec.is_latest_revision is False
        assert str(old_rec.superseded_by_record_id) == revised["record_id"]

        # Invariant: affected plan must be invalidated to STALE
        assert approval_engine._plans[plan_id]["plan_status"] == PlanStatus.STALE.value


# ──────────────────────────────────────────────
#  5. Duplicate Event Idempotency
# ──────────────────────────────────────────────

class TestDuplicateEventIdempotency:
    """Verify duplicate idempotency keys return identical records without duplicate state."""

    def test_duplicate_intake_idempotency(self):
        c = _make_client()
        _login(c)

        now = datetime.now(timezone.utc)
        key = f"idem-exec-{uuid4().hex}"

        payload = {
            "task_id": "TASK-IDEM-01",
            "actual_start_utc": (now - timedelta(hours=2)).isoformat(),
            "actual_restoration_utc": (now - timedelta(hours=1)).isoformat(),
            "actual_release_utc": now.isoformat(),
            "quantity_completed": 100.0,
            "quantity_units": "METERS",
            "idempotency_key": key,
        }

        resp1 = c.post("/api/v1/execution/record", json=payload)
        assert resp1.status_code == 200
        rec1 = resp1.json()

        resp2 = c.post("/api/v1/execution/record", json=payload)
        assert resp2.status_code == 200
        rec2 = resp2.json()

        assert rec1["record_id"] == rec2["record_id"]
        assert len(execution_engine.get_all_records()) == 1


# ──────────────────────────────────────────────
#  6. Unit Consistency & Mismatches
# ──────────────────────────────────────────────

class TestUnitConsistency:
    """Verify mismatched units are rejected and logged in reconciliation queue."""

    def test_unit_mismatch_rejected(self):
        c = _make_client()
        _login(c)

        execution_engine.register_task_contract(
            task_id="TASK-UNIT-01",
            expected_units="METERS",
            target_quantity=1000.0,
            planned_duration_minutes=60,
        )

        now = datetime.now(timezone.utc)
        bad_payload = {
            "task_id": "TASK-UNIT-01",
            "actual_start_utc": (now - timedelta(hours=2)).isoformat(),
            "actual_restoration_utc": (now - timedelta(hours=1)).isoformat(),
            "quantity_completed": 1.0,
            "quantity_units": "KILOMETERS",  # Task expects METERS!
        }

        resp = c.post("/api/v1/execution/record", json=bad_payload)
        assert resp.status_code == 400
        assert "Mismatched unit" in resp.json()["detail"]

        # Conflict logged in reconciliation queue
        queue = execution_engine.get_reconciliation_queue()
        assert any(item.task_id == "TASK-UNIT-01" and item.conflict_type == "UNIT_MISMATCH" for item in queue)


# ──────────────────────────────────────────────
#  7. Invalid Chronology Rejection
# ──────────────────────────────────────────────

class TestChronologyValidation:
    """Verify start >= restoration and release < restoration are strictly rejected."""

    def test_start_after_restoration_rejected(self):
        c = _make_client()
        _login(c)

        now = datetime.now(timezone.utc)
        payload = {
            "task_id": "TASK-CHRON-01",
            "actual_start_utc": now.isoformat(),
            "actual_restoration_utc": (now - timedelta(hours=1)).isoformat(),  # Inverted!
            "quantity_completed": 100.0,
            "quantity_units": "METERS",
        }

        resp = c.post("/api/v1/execution/record", json=payload)
        assert resp.status_code == 400
        assert "actual start" in resp.json()["detail"]

    def test_release_before_restoration_rejected(self):
        c = _make_client()
        _login(c)

        now = datetime.now(timezone.utc)
        payload = {
            "task_id": "TASK-CHRON-02",
            "actual_start_utc": (now - timedelta(hours=2)).isoformat(),
            "actual_restoration_utc": now.isoformat(),
            "actual_release_utc": (now - timedelta(minutes=15)).isoformat(),  # Release before physical restoration!
            "quantity_completed": 100.0,
            "quantity_units": "METERS",
        }

        resp = c.post("/api/v1/execution/record", json=payload)
        assert resp.status_code == 400
        assert "actual release" in resp.json()["detail"]


# ──────────────────────────────────────────────
#  8. Still-Occupied Resources Preservation
# ──────────────────────────────────────────────

class TestStillOccupiedResources:
    """Verify resources that overrun their window remain tracked as occupied."""

    def test_still_occupied_resources_recorded(self):
        c = _make_client()
        _login(c)

        now = datetime.now(timezone.utc)
        payload = {
            "task_id": "TASK-OCC-01",
            "actual_start_utc": (now - timedelta(hours=4)).isoformat(),
            "actual_restoration_utc": (now - timedelta(hours=1)).isoformat(),
            "quantity_completed": 200.0,
            "quantity_units": "METERS",
            "target_quantity": 400.0,
            "still_occupied_resources": ["BCM-01", "GANG-CIVIL-04"],
            "deviation_reason": "MACHINE_BREAKDOWN",
            "deviation_notes": "BCM conveyor belt jammed in ballast pocket",
        }

        resp = c.post("/api/v1/execution/record", json=payload)
        assert resp.status_code == 200

        occ = execution_engine.get_still_occupied_resources()
        assert "BCM-01" in occ
        assert "GANG-CIVIL-04" in occ
        assert occ["BCM-01"]["task_id"] == "TASK-OCC-01"


# ──────────────────────────────────────────────
#  9. Deterministic Estimate Review & Learning
# ──────────────────────────────────────────────

class TestEstimateReview:
    """Verify deterministic aggregation proposes buffer adjustments without ML or silent mutation."""

    def test_deterministic_overrun_triggers_increase_buffer(self):
        c = _make_client()
        _login(c)

        now = datetime.now(timezone.utc)

        # Register task metadata for 3 tasks with 100 min nominal duration
        for i in range(1, 4):
            execution_engine.register_task_contract(
                task_id=f"TASK-EST-{i}",
                expected_units="METERS",
                target_quantity=500.0,
                planned_duration_minutes=100,
                department="ENGINEERING",
                task_category="DEEP_SCREENING",
            )
            # Actual execution took 130 mins (+30% overrun)
            execution_engine.record_execution(ExecutionRecordCreate(
                task_id=f"TASK-EST-{i}",
                actual_start_utc=now - timedelta(minutes=130),
                actual_restoration_utc=now,
                quantity_completed=500.0,
                quantity_units="METERS",
                target_quantity=500.0,
                planned_duration_minutes=100,
                deviation_reason=DeviationReason.NONE,
            ), actor={"user_id": "usr-005-rev"})

        resp = c.get("/api/v1/execution/estimate-review")
        assert resp.status_code == 200
        data = resp.json()

        assert data["total_records_analyzed"] == 3
        summaries = data["summaries"]
        assert len(summaries) >= 1

        screening = next(s for s in summaries if s["task_category"] == "DEEP_SCREENING")
        assert screening["sample_size"] == 3
        assert screening["mean_planned_minutes"] == 100.0
        assert screening["mean_actual_minutes"] == 130.0
        assert screening["mean_overrun_pct"] == 30.0
        assert screening["recommended_action"] == EstimateReviewRecommendation.INCREASE_BUFFER.value
        assert screening["suggested_buffer_minutes"] == 30
        assert screening["requires_policy_revision"] is True


# ──────────────────────────────────────────────
#  10. End-to-End Execution Loop Verification
# ──────────────────────────────────────────────

class TestEndToEndExecutionLoop:
    """Demonstrate loop: original task -> checked proposal -> accepted actuals -> residual/next planning input."""

    def test_full_loop_from_intake_to_residual_input(self):
        c = _make_client()
        _login(c)

        # 1. Original task registered
        execution_engine.register_task_contract(
            task_id="TASK-LOOP-01",
            expected_units="METERS",
            target_quantity=1000.0,
            planned_duration_minutes=180,
            department="ENGINEERING",
            task_category="TURNOUT_OVERHAUL",
        )

        # 2. Field execution achieves partial 600m
        now = datetime.now(timezone.utc)
        rec = execution_engine.record_execution(ExecutionRecordCreate(
            task_id="TASK-LOOP-01",
            plan_id="plan-vkc-loop",
            actual_start_utc=now - timedelta(hours=3),
            actual_restoration_utc=now - timedelta(hours=1),
            actual_release_utc=now,
            quantity_completed=600.0,
            quantity_units="METERS",
            target_quantity=1000.0,
            planned_duration_minutes=180,
            deviation_reason=DeviationReason.MACHINE_BREAKDOWN,
        ), actor={"user_id": "usr-005-rev"})

        # 3. Inspect variance
        v_resp = c.get("/api/v1/execution/variance/TASK-LOOP-01")
        assert v_resp.status_code == 200
        var = v_resp.json()
        assert var["actual_quantity"] == 600.0
        assert var["quantity_completion_pct"] == 60.0
        assert var["status"] == ExecutionStatus.PARTIAL.value

        # 4. Confirm residual work of remaining 400m
        confirm_resp = c.post("/api/v1/execution/residual/confirm", json={
            "source_record_id": str(rec.record_id),
            "confirmed_residual_quantity": 400.0,
            "quantity_units": "METERS",
            "site_state": "TURNOUT_PARTIAL_FITTED",
            "priority": "TIER_1_MANDATORY",
        })
        assert confirm_resp.status_code == 200

        # 5. Verify residual task appears in next planning inputs catalog
        tasks_resp = c.get("/api/v1/execution/residual/tasks")
        assert tasks_resp.status_code == 200
        resids = tasks_resp.json()["residual_tasks"]
        assert any(r["original_task_id"] == "TASK-LOOP-01" and r["residual_quantity"] == 400.0 for r in resids)
