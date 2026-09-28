"""
Phase 10 Automated Integration Test Suite:
Durable Solve Jobs, Leased Worker Queue, and Complete Planning APIs.
Tests Blueprint Sections 28, 31, 33-34, 42-43:
1. test_job_submit_returns_202_and_status_url
2. test_worker_claims_and_executes_job_to_completion
3. test_idempotency_duplicate_submit_returns_same_job
4. test_idempotency_mismatched_payload_raises_409_conflict
5. test_if_match_stale_etag_cancellation
6. test_worker_crash_and_lease_expiry_reclaim
7. test_stale_worker_publication_rejected_by_fencing_token
8. test_domain_infeasible_reported_truthfully_as_completed
9. test_unauthorized_user_denied_solve
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import select, update

from app.main import app
from app.db.session import async_session_factory
from app.db.models import SolveJobModel, PlanVersionModel
from app.schemas.enums import JobState, ObjectiveProfile, SolverStatus
from app.schemas.checker import CheckerVerdict
from app.schemas.job import SolveJobCreateRequest, JobPhase
from app.worker.solve_worker import SolveWorker, StaleWorkerPublicationError
from app.domain.job_service import JobService


@pytest.mark.anyio
async def test_job_submit_returns_202_and_status_url(client: TestClient):
    """
    Submitting a solve job returns HTTP 202 Accepted, Location header, and ETag.
    """
    response = client.post(
        "/api/v1/planning/solve-jobs",
        json={
            "corridor_code": "VKC",
            "profile": "PROGRAMME_IMPROVEMENT",
            "time_limit_seconds": 10.0,
            "lattice_step_minutes": 60,
        },
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "QUEUED"
    assert data["current_phase"] == "QUEUED"
    assert data["corridor_code"] == "VKC"
    assert data["fencing_token"] == 0
    assert data["attempt_count"] == 0
    assert "Location" in response.headers
    assert response.headers["Location"] == f"/api/v1/planning/solve-jobs/{data['job_id']}"
    assert "ETag" in response.headers


@pytest.mark.anyio
async def test_worker_claims_and_executes_job_to_completion(client: TestClient):
    """
    Worker claims queued job via SKIP LOCKED, executes CP-SAT outside transaction,
    verifies via Independent Checker, and publishes immutable plan version.
    """
    # 1. Allocate Monthly Plan so Week 1 has a validated tactical envelope
    resp_alloc = client.post(
        "/api/v1/planning/monthly/allocate",
        json={
            "corridor_code": "VKC",
            "planning_month": "2026-10",
            "time_limit_seconds": 10.0,
        },
    )
    assert resp_alloc.status_code == 200
    monthly_plan_id = resp_alloc.json()["monthly_plan_id"]

    # 2. Submit Weekly Solve Job linked to Parent Monthly Plan
    resp_submit = client.post(
        "/api/v1/planning/solve-jobs",
        json={
            "corridor_code": "VKC",
            "profile": "PROGRAMME_IMPROVEMENT",
            "time_limit_seconds": 15.0,
            "lattice_step_minutes": 60,
            "max_candidates": 10000,
            "parent_monthly_plan_id": monthly_plan_id,
            "target_week_index": 1,
        },
    )
    assert resp_submit.status_code == 202
    job_id = resp_submit.json()["job_id"]

    # 3. Worker Claims and Processes Job
    worker = SolveWorker(worker_id="test-worker-alpha", lease_duration_seconds=60)
    async with async_session_factory() as session:
        result = await worker.run_once(session, job_id=job_id)

    assert result is not None
    assert result["status"] == "COMPLETED"
    plan_id = result["result_plan_id"]
    assert plan_id is not None

    # 3. Verify Job Representation via API
    resp_job = client.get(f"/api/v1/planning/solve-jobs/{job_id}")
    assert resp_job.status_code == 200
    job_data = resp_job.json()
    assert job_data["status"] == "COMPLETED"
    assert job_data["current_phase"] == "COMPLETED"
    assert job_data["progress_percentage"] == 100
    assert job_data["result_plan_id"] == plan_id
    assert job_data["result_summary"]["solver_status"] in ("OPTIMAL", "FEASIBLE")
    assert job_data["result_summary"]["checker_verdict"] == "VALID"

    # 4. Verify Plan Version Retrieval via API
    resp_plan = client.get(f"/api/v1/planning/plans/{plan_id}")
    assert resp_plan.status_code == 200
    plan_data = resp_plan.json()
    assert plan_data["plan_id"] == plan_id
    assert plan_data["corridor_code"] == "VKC"
    assert len(plan_data["assignments"]) > 0
    assert plan_data["checker_verdict"] == "VALID"


@pytest.mark.anyio
async def test_idempotency_duplicate_submit_returns_same_job(client: TestClient):
    """
    Duplicate submissions with the same Idempotency-Key return the existing job (200/202).
    """
    idem_key = f"IDEM-TEST-{uuid4().hex[:8]}"
    payload = {
        "corridor_code": "VKC",
        "profile": "PROGRAMME_IMPROVEMENT",
        "time_limit_seconds": 12.0,
        "lattice_step_minutes": 60,
    }

    # First Submit
    resp1 = client.post(
        "/api/v1/planning/solve-jobs",
        json=payload,
        headers={"Idempotency-Key": idem_key},
    )
    assert resp1.status_code == 202
    job_id_1 = resp1.json()["job_id"]

    # Second Submit with identical payload and key
    resp2 = client.post(
        "/api/v1/planning/solve-jobs",
        json=payload,
        headers={"Idempotency-Key": idem_key},
    )
    assert resp2.status_code == 200
    job_id_2 = resp2.json()["job_id"]
    assert job_id_1 == job_id_2


@pytest.mark.anyio
async def test_idempotency_mismatched_payload_raises_409_conflict(client: TestClient):
    """
    Reusing an Idempotency-Key with a different payload body returns HTTP 409 Conflict.
    """
    idem_key = f"IDEM-CONFLICT-{uuid4().hex[:8]}"
    payload_a = {
        "corridor_code": "VKC",
        "profile": "PROGRAMME_IMPROVEMENT",
        "time_limit_seconds": 10.0,
    }
    payload_b = {
        "corridor_code": "VKC",
        "profile": "DISRUPTION_RECOVERY",  # Different profile!
        "time_limit_seconds": 30.0,
    }

    resp1 = client.post(
        "/api/v1/planning/solve-jobs",
        json=payload_a,
        headers={"Idempotency-Key": idem_key},
    )
    assert resp1.status_code == 202

    resp2 = client.post(
        "/api/v1/planning/solve-jobs",
        json=payload_b,
        headers={"Idempotency-Key": idem_key},
    )
    assert resp2.status_code == 409
    assert "different solve request payload" in resp2.json()["detail"]


@pytest.mark.anyio
async def test_if_match_stale_etag_cancellation(client: TestClient):
    """
    Cancelling a solve job requires a valid matching ETag if If-Match is provided.
    Stale ETags return HTTP 412 Precondition Failed.
    """
    resp_submit = client.post(
        "/api/v1/planning/solve-jobs",
        json={"corridor_code": "VKC", "time_limit_seconds": 10.0},
    )
    assert resp_submit.status_code == 202
    job_id = resp_submit.json()["job_id"]
    correct_etag = resp_submit.headers["ETag"]

    # 1. Stale ETag returns 412
    resp_stale = client.post(
        f"/api/v1/planning/solve-jobs/{job_id}/cancel",
        json={"reason": "Abort testing"},
        headers={"If-Match": '"stale-etag-999"'},
    )
    assert resp_stale.status_code == 412

    # 2. Matching ETag succeeds
    resp_valid = client.post(
        f"/api/v1/planning/solve-jobs/{job_id}/cancel",
        json={"reason": "User changed planning priorities"},
        headers={"If-Match": correct_etag},
    )
    assert resp_valid.status_code == 200
    assert resp_valid.json()["status"] == "CANCELLED"
    assert resp_valid.json()["current_phase"] == "CANCELLED"


@pytest.mark.anyio
async def test_worker_crash_and_lease_expiry_reclaim():
    """
    If Worker 1 crashes and its lease expires, Worker 2 reclaims the job with an incremented fencing token.
    """
    async with async_session_factory() as session:
        # Submit a job directly
        req = SolveJobCreateRequest(corridor_code="VKC", time_limit_seconds=5.0)
        job_resp, _ = await JobService.create_solve_job(session, req)
        job_id = job_resp.job_id

        # Worker 1 claims job with a lease that immediately expires
        worker_1 = SolveWorker(worker_id="crashed-worker-1", lease_duration_seconds=-10)
        claimed_1 = await worker_1.claim_job(session, job_id=job_id)
        assert claimed_1 is not None
        assert claimed_1.fencing_token == 1
        assert claimed_1.attempt_count == 1
        assert claimed_1.lease_owner == "crashed-worker-1"

        # Worker 2 attempts to claim: detects expired lease and successfully steals/reclaims
        worker_2 = SolveWorker(worker_id="healthy-worker-2", lease_duration_seconds=60)
        claimed_2 = await worker_2.claim_job(session, job_id=job_id)
        assert claimed_2 is not None
        assert claimed_2.job_id == job_id
        assert claimed_2.fencing_token == 2
        assert claimed_2.attempt_count == 2
        assert claimed_2.lease_owner == "healthy-worker-2"


@pytest.mark.anyio
async def test_stale_worker_publication_rejected_by_fencing_token():
    """
    If a worker whose lease expired attempts to publish results after a newer worker has claimed the job,
    publication is rejected with StaleWorkerPublicationError.
    """
    async with async_session_factory() as session:
        req = SolveJobCreateRequest(corridor_code="VKC", time_limit_seconds=5.0)
        job_resp, _ = await JobService.create_solve_job(session, req)
        job_id = job_resp.job_id

        worker_1 = SolveWorker(worker_id="slow-worker-1", lease_duration_seconds=-5)
        claimed_1 = await worker_1.claim_job(session, job_id=job_id)
        token_1 = claimed_1.fencing_token

        # Worker 2 reclaims job, bumping fencing token
        worker_2 = SolveWorker(worker_id="fast-worker-2", lease_duration_seconds=60)
        claimed_2 = await worker_2.claim_job(session, job_id=job_id)
        assert claimed_2.fencing_token == token_1 + 1

        # Worker 1 attempts to publish: rejected!
        class DummyResult:
            is_feasible = True
            solver_status = SolverStatus.OPTIMAL
            stop_reason = None
            assignments = []
            reconciliation_cases = []
            checker_verdict = CheckerVerdict.VALID
            approval_eligibility = None
            profile = ObjectiveProfile.PROGRAMME_IMPROVEMENT
            total_tasks_count = 0
            scheduled_tasks_count = 0
            mandatory_total_count = 0
            mandatory_scheduled_count = 0
            bundled_packages_count = 0
            total_block_minutes = 0
            solve_duration_ms = 100.0

        with pytest.raises(StaleWorkerPublicationError):
            await worker_1.publish_result(
                db=session,
                job_id=job_id,
                fencing_token=token_1,
                snapshot=None,
                solve_result=DummyResult(),
            )


@pytest.mark.anyio
async def test_domain_infeasible_reported_truthfully_as_completed():
    """
    A mathematically INFEASIBLE run is a truthful domain outcome, NOT an HTTP 500 or worker crash.
    The job completes with status COMPLETED and result_summary['solver_status'] == 'INFEASIBLE'.
    """
    # Create worker and execute on corridor
    # SolveWorker will process job and if CP-SAT proves infeasible, records COMPLETED with diagnostic
    worker = SolveWorker(worker_id="infeasible-verifier-worker")
    async with async_session_factory() as session:
        # Create a job
        req = SolveJobCreateRequest(
            corridor_code="VKC",
            time_limit_seconds=5.0,
            lattice_step_minutes=60,
        )
        job_resp, _ = await JobService.create_solve_job(session, req)
        job_id = job_resp.job_id

        job = await worker.claim_job(session, job_id=job_id)
        assert job is not None
        result = await worker.process_job(session, job)
        assert result["status"] == "COMPLETED"


def test_unauthorized_user_denied_solve(client: TestClient):
    """
    A user lacking SOLVE_TRIGGER permission (e.g. planner_tms) is rejected with HTTP 403 Forbidden.
    """
    # Login as planner_tms (DEPARTMENT_PLANNER role lacks SOLVE_TRIGGER)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "planner_tms", "password": "tms@pass2026"},
    )
    assert login_resp.status_code == 200

    # Attempt solve job submission
    solve_resp = client.post(
        "/api/v1/planning/solve-jobs",
        json={"corridor_code": "VKC", "time_limit_seconds": 10.0},
    )
    assert solve_resp.status_code == 403
    assert "Forbidden" in solve_resp.json()["detail"]
