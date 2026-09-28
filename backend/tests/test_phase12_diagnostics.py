"""
Phase 12 Automated Integration Test Suite:
Evidence-Backed Why, Why-Not Diagnostics, and Bounded Repair Engine.
Tests Blueprint Sections 24, 25, 31, and 32:

1. test_why_not_diagnostic_unplaced_task_facts
2. test_why_selected_diagnostic_scheduled_assignment
3. test_trial_repair_simulation_non_publishable
4. test_apply_repair_with_precondition_concurrency
5. test_search_incomplete_truthfulness_timeout
6. test_input_blocked_readiness_distinction
7. test_repair_safety_invariant
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import async_session_factory
from app.db.models import PlanVersionModel, TaskModel, MaterializedAssignmentModel, SnapshotModel
from app.schemas.enums import DiagnosticReasonCode, ProofStatus, RepairActionType, PlanStatus
from app.worker.solve_worker import SolveWorker

_CACHED_PLAN_ID = None


async def get_or_create_executed_plan(client: TestClient) -> str:
    """
    Submits and executes a real solve job once, caching the resulting plan ID across tests.
    """
    global _CACHED_PLAN_ID
    if _CACHED_PLAN_ID is not None:
        return _CACHED_PLAN_ID

    res = client.post(
        "/api/v1/planning/solve-jobs",
        json={
            "corridor_code": "VKC",
            "profile": "PROGRAMME_IMPROVEMENT",
            "time_limit_seconds": 10.0,
            "lattice_step_minutes": 60,
        },
    )
    assert res.status_code == 202
    job_id = res.json()["job_id"]

    worker = SolveWorker(worker_id="test-diag-worker", lease_duration_seconds=30)
    async with async_session_factory() as session:
        await worker.run_once(session, job_id=job_id)

    job_res = client.get(f"/api/v1/planning/solve-jobs/{job_id}")
    assert job_res.status_code == 200
    job_data = job_res.json()
    assert job_data["status"] == "COMPLETED"
    assert job_data["result_plan_id"] is not None

    _CACHED_PLAN_ID = job_data["result_plan_id"]
    return _CACHED_PLAN_ID


@pytest.mark.anyio
async def test_why_not_diagnostic_unplaced_task_facts(client: TestClient):
    """
    Evaluates Why-Not diagnostic for an unplaced demand.
    Verifies typed reason code, factual evidence, and allowlisted repairs.
    """
    plan_id = await get_or_create_executed_plan(client)

    tasks_res = client.get("/api/v1/tasks?limit=50")
    assert tasks_res.status_code == 200
    all_tasks = tasks_res.json()["tasks"]
    assert len(all_tasks) > 0

    plan_res = client.get(f"/api/v1/planning/plans/{plan_id}")
    assert plan_res.status_code == 200
    placed_task_ids = {a["task_id"] for a in plan_res.json()["assignments"]}

    unplaced = next((t for t in all_tasks if t["task_id"] not in placed_task_ids), all_tasks[0])
    task_id = unplaced["task_id"]

    res = client.get(f"/api/v1/planning/diagnostics/why-not/{plan_id}/{task_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["task_id"] == task_id
    assert data["plan_id"] == plan_id
    assert data["reason_code"] in [
        DiagnosticReasonCode.INPUT_BLOCKED.value,
        DiagnosticReasonCode.CANDIDATE_REJECTED.value,
        DiagnosticReasonCode.NO_CANDIDATE_IN_DOMAIN.value,
        DiagnosticReasonCode.MODEL_INFEASIBLE.value,
        DiagnosticReasonCode.FEASIBLE_BUT_UNSELECTED.value,
        DiagnosticReasonCode.SEARCH_INCOMPLETE.value,
    ]
    assert data["proof_status"] in [
        ProofStatus.PROVEN_CONSTRAINED.value,
        ProofStatus.PROVEN_SUBOPTIMAL.value,
        ProofStatus.EMPIRICALLY_CONFLICTING.value,
        ProofStatus.INCONCLUSIVE.value,
    ]
    assert len(data["primary_cause_summary"]) > 0
    assert len(data["explanation_narrative"]) > 0
    assert isinstance(data["facts"], list)
    assert isinstance(data["conflict_core"], dict)

    for rep in data["permitted_repairs"]:
        assert rep["action_type"] in [
            RepairActionType.MOVE_OPTIONAL_UNLOCKED_WORK.value,
            RepairActionType.SUBSTITUTE_RESOURCE.value,
            RepairActionType.ALTERNATE_PACKAGE_WINDOW.value,
            RepairActionType.REQUEST_PARENT_WEEK_AMENDMENT.value,
        ]


@pytest.mark.anyio
async def test_why_selected_diagnostic_scheduled_assignment(client: TestClient):
    """
    Evaluates Why diagnostic for a scheduled assignment.
    Verifies admissibility facts, objective contribution, and counterfactuals.
    """
    plan_id = await get_or_create_executed_plan(client)
    plan_res = client.get(f"/api/v1/planning/plans/{plan_id}")
    assert plan_res.status_code == 200
    assignments = plan_res.json()["assignments"]
    assert len(assignments) > 0

    asn = assignments[0]
    assignment_id = asn["assignment_id"]

    res = client.get(f"/api/v1/planning/diagnostics/why/{plan_id}/{assignment_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["assignment_id"] == assignment_id
    assert len(data["admissibility_facts"]) >= 3
    assert "criticality_weight" in data["objective_contributions"]
    assert "productive_possession_minutes" in data["objective_contributions"]
    assert "total_score_contribution" in data["objective_contributions"]
    assert len(data["counterfactual_comparisons"]) >= 1

    cf = data["counterfactual_comparisons"][0]
    assert cf["comparison_outcome"] in ["OBJECTIVE_SUBOPTIMAL", "CONFLICTING_TRAIN", "OVERLAPPING_LOCKED_POSSESSION"]


@pytest.mark.anyio
async def test_trial_repair_simulation_non_publishable(client: TestClient):
    """
    Simulates a non-publishable trial repair.
    Verifies that is_publishable is False and independent checker runs.
    """
    plan_id = await get_or_create_executed_plan(client)
    tasks_res = client.get("/api/v1/tasks?limit=5")
    task_id = tasks_res.json()["tasks"][0]["task_id"]

    req = {
        "plan_id": plan_id,
        "task_id": task_id,
        "repair_id": "REP-TRIAL-001",
        "action_type": "MOVE_OPTIONAL_UNLOCKED_WORK",
        "proposed_value": "+120m",
    }

    res = client.post("/api/v1/planning/diagnostics/repairs/trial", json=req)
    assert res.status_code == 200
    data = res.json()

    assert data["repair_id"] == "REP-TRIAL-001"
    assert data["is_publishable"] is False  # STRICT: never publishable
    assert data["checker_verdict"] in ["VALID", "PASSED", "INVALID", "FAILED"]
    assert data["runtime_ms"] > 0
    assert data["simulated_assignments_count"] > 0


@pytest.mark.anyio
async def test_apply_repair_with_precondition_concurrency(client: TestClient):
    """
    Verifies that applying a repair checks plan version concurrency (ETag)
    and submits a fresh normal solve job.
    """
    plan_id = await get_or_create_executed_plan(client)
    tasks_res = client.get("/api/v1/tasks?limit=5")
    task_id = tasks_res.json()["tasks"][0]["task_id"]

    # 1. Matching version -> Success
    valid_req = {
        "plan_id": plan_id,
        "task_id": task_id,
        "repair_id": "REP-APPLY-001",
        "expected_plan_version": 1,
        "authorized_by_role": "OPERATING_REVIEWER",
        "justification": "Approved shifting conflicting unlocked work to low-density window.",
    }

    res = client.post("/api/v1/planning/diagnostics/repairs/apply", json=valid_req)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "QUEUED"
    assert data["new_job_id"] is not None

    # 2. Mismatched version -> HTTP 412 Precondition Failed
    stale_req = {
        "plan_id": plan_id,
        "task_id": task_id,
        "repair_id": "REP-APPLY-002",
        "expected_plan_version": 999,  # Mismatched!
        "authorized_by_role": "OPERATING_REVIEWER",
        "justification": "Stale attempt",
    }
    stale_res = client.post("/api/v1/planning/diagnostics/repairs/apply", json=stale_req)
    assert stale_res.status_code == 412


@pytest.mark.anyio
async def test_search_incomplete_truthfulness_timeout(client: TestClient):
    """
    Verifies that a solver timeout is truthfully reported as SEARCH_INCOMPLETE
    with INCONCLUSIVE proof status, and NEVER as a physical impossibility.
    """
    plan_uid = f"plan-timeout-{uuid4().hex[:8]}"
    async with async_session_factory() as session:
        timed_out_plan = PlanVersionModel(
            plan_id=plan_uid,
            plan_version_number=1,
            corridor_code="VKC",
            snapshot_id="SNAP-VKC-SEED-W1",
            horizon_type="WEEKLY",
            plan_status=PlanStatus.DRAFT_PROPOSAL,
            solver_status="TIMED_OUT",
            metrics={},
        )
        session.add(timed_out_plan)
        await session.commit()

    tasks_res = client.get("/api/v1/tasks?limit=1")
    task_id = tasks_res.json()["tasks"][0]["task_id"]

    res = client.get(f"/api/v1/planning/diagnostics/why-not/{plan_uid}/{task_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["reason_code"] == DiagnosticReasonCode.SEARCH_INCOMPLETE.value
    assert data["proof_status"] == ProofStatus.INCONCLUSIVE.value
    assert "time budget" in data["primary_cause_summary"].lower()


@pytest.mark.anyio
async def test_input_blocked_readiness_distinction(client: TestClient):
    """
    Verifies that a task failing readiness certifications is diagnosed as
    INPUT_BLOCKED and PROVEN_CONSTRAINED.
    """
    plan_id = await get_or_create_executed_plan(client)

    # Create an unready task with missing certifications
    unready_task_id = f"task-unready-{uuid4().hex[:8]}"
    async with async_session_factory() as session:
        t = TaskModel(
            task_id=unready_task_id,
            business_key=f"TEST-UNREADY-{uuid4().hex[:4]}",
            department="ENGINEERING",
            sub_department="PERMANENT_WAY",
            work_type="TRACK_RENEWAL",
            description="Test unready task for diagnostics",
            station_from="ALP",
            station_to="BRV",
            criticality="TIER_2_SPEED_RESTRICTION",
            track_segment_id="SEC-01-UP",
            chainage_start_km=0.0,
            chainage_end_km=10.0,
            duration_minutes=180,
            total_block_minutes=240,
            deadline_utc=datetime(2026, 10, 20, 0, 0),
            preferred_windows=[],
            required_resources=[{"resource_id": "MACH-UNAVAILABLE-99", "resource_type": "MACHINE", "quantity": 1}],
            requires_power_block=False,
        )
        session.add(t)
        await session.commit()

    res = client.get(f"/api/v1/planning/diagnostics/why-not/{plan_id}/{unready_task_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["reason_code"] == DiagnosticReasonCode.INPUT_BLOCKED.value
    assert data["proof_status"] == ProofStatus.PROVEN_CONSTRAINED.value
    assert "readiness" in data["primary_cause_summary"].lower()


@pytest.mark.anyio
async def test_repair_safety_invariant(client: TestClient):
    """
    Verifies that all generated repair options strictly adhere to the allowlisted
    bounded repair catalogue and never propose safety or isolation relaxations.
    """
    plan_id = await get_or_create_executed_plan(client)
    tasks_res = client.get("/api/v1/tasks?limit=10")
    for t in tasks_res.json()["tasks"]:
        res = client.get(f"/api/v1/planning/diagnostics/why-not/{plan_id}/{t['task_id']}")
        if res.status_code == 200:
            diag = res.json()
            for r in diag.get("permitted_repairs", []):
                assert r["action_type"] in [
                    "MOVE_OPTIONAL_UNLOCKED_WORK",
                    "SUBSTITUTE_RESOURCE",
                    "ALTERNATE_PACKAGE_WINDOW",
                    "REQUEST_PARENT_WEEK_AMENDMENT",
                ]
                desc = r["description"].lower()
                assert "disable safety" not in desc
                assert "bypass isolation" not in desc
                assert "ignore headway" not in desc
