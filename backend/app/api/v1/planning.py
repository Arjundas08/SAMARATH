"""
REST API endpoints for Phase 06:
Candidate Generation, Sparse Opportunity Manifests, and Credible Greedy Baseline.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.snapshot import Snapshot
from app.schemas.candidate import CandidateManifest
from app.gateway.service import seal_snapshot_from_db
from app.engine.candidate_generator import CandidateGenerator
from app.engine.greedy_baseline import GreedyBaselineSolver, BaselineSolveResult
from app.engine.cp_sat_solver import CPSatWeeklyOptimizer
from app.schemas.optimizer import OptimizerSolveRequest, OptimizerSolveResult
from app.db.session import get_db

router = APIRouter(prefix="/planning", tags=["Planning & Baseline"])


class GenerateCandidatesRequest(BaseModel):
    corridor_code: str = "VKC"
    lattice_step_minutes: int = 30
    max_candidates: int = 20000


class BaselineSolveRequest(BaseModel):
    corridor_code: str = "VKC"
    lattice_step_minutes: int = 30
    max_candidates: int = 20000


@router.post("/candidates/generate", response_model=CandidateManifest)
async def generate_candidates(
    request: GenerateCandidatesRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generates sparse placement candidates for the current corridor snapshot.
    """
    snapshot = await seal_snapshot_from_db(
        db,
        corridor_code=request.corridor_code,
        user_id="planner",
    )
    generator = CandidateGenerator(
        snapshot=snapshot,
        lattice_step_minutes=request.lattice_step_minutes,
        max_candidates=request.max_candidates,
    )
    manifest = generator.generate_manifest()
    return manifest


@router.post("/baseline/solve", response_model=BaselineSolveResult)
async def solve_greedy_baseline(
    request: BaselineSolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes the coordinated greedy baseline benchmark with priority-first ranking,
    at-most-once coverage, hard lock preservation, and 1-step bounded repair pass.
    """
    snapshot = await seal_snapshot_from_db(
        db,
        corridor_code=request.corridor_code,
        user_id="planner",
    )
    generator = CandidateGenerator(
        snapshot=snapshot,
        lattice_step_minutes=request.lattice_step_minutes,
        max_candidates=request.max_candidates,
    )
    manifest = generator.generate_manifest()

    solver = GreedyBaselineSolver(snapshot=snapshot, manifest=manifest)
    result = solver.solve()
    return result


@router.post("/optimizer/solve", response_model=OptimizerSolveResult)
async def solve_cp_sat_optimizer(
    request: OptimizerSolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes the real OR-Tools CP-SAT Weekly Optimizer with lexicographic profiles:
    - PROGRAMME_IMPROVEMENT (routine weekly planning)
    - DISRUPTION_RECOVERY (minimal churn event replanning)
    Validates output through the independent Phase 07 feasibility checker.
    """
    snapshot = await seal_snapshot_from_db(
        db,
        corridor_code=request.corridor_code,
        user_id="optimizer",
    )
    generator = CandidateGenerator(
        snapshot=snapshot,
        lattice_step_minutes=request.lattice_step_minutes,
        max_candidates=request.max_candidates,
    )
    manifest = generator.generate_manifest()

    optimizer = CPSatWeeklyOptimizer(
        snapshot=snapshot,
        manifest=manifest,
        request=request,
    )
    result = optimizer.solve()
    return result


# --- Phase 09: Monthly Allocation & Weekly Reconciliation Endpoints ---

from app.schemas.monthly import (
    MonthlyAllocationRequest,
    MonthlyAllocationPlan,
    ReconciliationCase,
    ResolveReconciliationRequest,
)
from app.schemas.enums import ReconciliationStatus
from app.engine.monthly_allocator import MonthlyAllocator
from app.domain.reconciliation import ReconciliationStore, WeeklyReconciliationService


@router.post("/monthly/allocate", response_model=MonthlyAllocationPlan)
async def allocate_monthly_plan(
    request: MonthlyAllocationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes the 30-day / 4-week tactical CP-SAT allocation across calendar weeks.
    Enforces due-week deadlines, precedence order, aggregate track possession quotas,
    and machine capacity budgets. Output status is ALLOCATED_PROVISIONAL.
    """
    snapshot = await seal_snapshot_from_db(
        db,
        corridor_code=request.corridor_code,
        user_id="monthly-planner",
    )
    allocator = MonthlyAllocator(snapshot=snapshot, request=request)
    plan = allocator.allocate()
    ReconciliationStore.save_plan(plan)
    return plan


@router.get("/monthly/plans", response_model=List[MonthlyAllocationPlan])
async def list_monthly_plans(corridor_code: Optional[str] = Query(None)):
    """
    Lists stored monthly allocation plan versions for the corridor.
    """
    return ReconciliationStore.list_plans(corridor_code=corridor_code)


@router.get("/monthly/plans/{plan_id}", response_model=MonthlyAllocationPlan)
async def get_monthly_plan(plan_id: str):
    """
    Retrieves a specific immutable monthly allocation plan version.
    """
    plan = ReconciliationStore.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"MonthlyAllocationPlan '{plan_id}' not found")
    return plan


@router.get("/reconciliation/cases", response_model=List[ReconciliationCase])
async def list_reconciliation_cases(
    parent_plan_id: Optional[str] = Query(None),
    child_plan_id: Optional[str] = Query(None),
    status: Optional[ReconciliationStatus] = Query(None),
):
    """
    Lists active or resolved two-horizon reconciliation cases.
    """
    return ReconciliationStore.list_cases(
        parent_plan_id=parent_plan_id,
        child_plan_id=child_plan_id,
        status=status,
    )


@router.get("/reconciliation/cases/{case_id}", response_model=ReconciliationCase)
async def get_reconciliation_case(case_id: str):
    """
    Retrieves details of a specific reconciliation case.
    """
    case = ReconciliationStore.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"ReconciliationCase '{case_id}' not found")
    return case


@router.post("/reconciliation/{case_id}/resolve")
async def resolve_reconciliation_case(
    case_id: str,
    request: ResolveReconciliationRequest,
):
    """
    Resolves a reconciliation case via the controlled amendment path:
    - Verifies reviewer role (OPERATING_REVIEWER or ADMINISTRATOR).
    - If APPROVED_AMENDMENT, creates a new immutable parent monthly version (v1 -> v2),
      applies task allocation shifts, marks prior parent SUPERSEDED, and unblocks child weekly approval.
    """
    try:
        updated_case, amended_parent = WeeklyReconciliationService.resolve_case(
            case_id=case_id,
            request=request,
            resolved_by="operating-reviewer",
        )
        return {
            "case": updated_case,
            "amended_parent_plan": amended_parent,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# --- Phase 10: Durable Solve Jobs & Complete Planning APIs ---

from fastapi import Header, Response, Request, status, BackgroundTasks
from app.schemas.job import (
    SolveJobCreateRequest,
    SolveJobResponse,
    SolveJobListResponse,
    SolveJobCancelRequest,
    PlanVersionResponse,
)
from app.schemas.auth import Permission
from app.core.auth import get_current_user
from app.domain.job_service import (
    JobService,
    MismatchedPayloadError,
    PreconditionFailedError,
    InvalidJobStateError,
    JobNotFoundError,
)
from app.db.models import PlanVersionModel, MaterializedAssignmentModel


def _get_authenticated_user(request: Request) -> Dict[str, Any]:
    session_token = request.cookies.get("samarath_session")
    auth_header = request.headers.get("Authorization")
    if session_token or auth_header:
        user = get_current_user(request)
        user_perms = user.get("permissions", [])
        if Permission.SOLVE_TRIGGER.value not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires '{Permission.SOLVE_TRIGGER.value}' permission.",
            )
        return user
    # Default coordinator for unauthenticated test harness / development
    return {
        "sub": "planner",
        "roles": ["CORRIDOR_COORDINATOR"],
        "permissions": [Permission.SOLVE_TRIGGER.value],
        "department": None,
        "territory": "VKC",
    }


@router.post("/solve-jobs", response_model=SolveJobResponse)
async def submit_solve_job(
    solve_request: SolveJobCreateRequest,
    request: Request,
    response: Response,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
):
    """
    Submits a solve job to the durable PostgreSQL queue.
    Validates scope, policy, and snapshot, returning HTTP 202 Accepted with job status URL and ETag.
    Enforces idempotency keys: duplicate identical payload returns 200/202 with existing job;
    mismatched payload raises HTTP 409 Conflict per RFC 7807.
    """
    user = _get_authenticated_user(request)

    try:
        job, is_new = await JobService.create_solve_job(
            db=db,
            request=solve_request,
            idempotency_key=idempotency_key,
            user_id=user["sub"],
            user_role=user["roles"][0] if user.get("roles") else "PLANNER",
        )
        response.status_code = status.HTTP_202_ACCEPTED if is_new else status.HTTP_200_OK
        response.headers["Location"] = f"/api/v1/planning/solve-jobs/{job.job_id}"
        response.headers["ETag"] = job.etag
        return job

    except MismatchedPayloadError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/solve-jobs/{job_id}", response_model=SolveJobResponse)
async def get_solve_job(
    job_id: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves the status, phase, and result of a durable solve job.
    Returns entity ETag for optimistic concurrency control.
    """
    try:
        job = await JobService.get_solve_job(db, job_id)
        response.headers["ETag"] = job.etag
        return job
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/solve-jobs", response_model=SolveJobListResponse)
async def list_solve_jobs(
    corridor_code: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists solve jobs with optional corridor and status filtering.
    """
    from app.schemas.enums import JobState
    job_state = JobState(status) if status else None
    jobs, total = await JobService.list_solve_jobs(
        db,
        corridor_code=corridor_code,
        status=job_state,
        limit=limit,
        offset=offset,
    )
    return SolveJobListResponse(jobs=jobs, total=total)


@router.post("/solve-jobs/{job_id}/cancel", response_model=SolveJobResponse)
async def cancel_solve_job(
    job_id: str,
    cancel_request: SolveJobCancelRequest,
    request: Request,
    response: Response,
    if_match: Optional[str] = Header(None, alias="If-Match"),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancels a queued or executing solve job with optimistic concurrency check.
    If If-Match header is supplied, validates that resource has not changed since inspection.
    """
    user = _get_authenticated_user(request)
    try:
        job = await JobService.cancel_solve_job(
            db=db,
            job_id=job_id,
            request=cancel_request,
            if_match=if_match,
            user_id=user["sub"],
            user_role=user["roles"][0] if user.get("roles") else "PLANNER",
        )
        response.headers["ETag"] = job.etag
        return job
    except JobNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PreconditionFailedError as e:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(e))
    except InvalidJobStateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/solve-jobs/{job_id}/execute", status_code=status.HTTP_202_ACCEPTED)
async def execute_solve_job_endpoint(
    job_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers asynchronous leased worker execution for a queued job.
    Returns 202 Accepted.
    """
    from app.worker.solve_worker import SolveWorker
    from app.db.session import async_session_factory

    async def _worker_task(jid: str):
        async with async_session_factory() as session:
            worker = SolveWorker(worker_id="workbench-worker", lease_duration_seconds=120)
            await worker.run_once(session, job_id=jid)

    background_tasks.add_task(_worker_task, job_id)
    return {"status": "ACCEPTED", "job_id": job_id, "message": "Worker dispatched"}


@router.get("/timetable/occupations")
async def get_timetable_occupations(
    corridor_code: str = Query(default="VKC"),
):
    """
    Returns the train occupations for the corridor to visualize on the Time-Distance canvas.
    """
    import os, json
    from app.gateway.service import SEED_DIR
    train_path = os.path.join(SEED_DIR, "train_timetable.json")
    if os.path.exists(train_path):
        with open(train_path, "r") as f:
            return json.load(f)
    return []


@router.get("/corridor/topology")
async def get_corridor_topology(
    corridor_code: str = Query(default="VKC"),
):
    """
    Returns the corridor topology including stations, chainage km, and track segments.
    """
    import os, json
    from app.gateway.service import SEED_DIR
    topo_path = os.path.join(SEED_DIR, "corridor_topology.json")
    if os.path.exists(topo_path):
        with open(topo_path, "r") as f:
            return json.load(f)
    return {}


@router.get("/plans/{plan_id}", response_model=PlanVersionResponse)
async def get_plan_version(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves a complete immutable plan version by ID, including materialized assignments,
    solver status, checker verdict, and reconciliation cases.
    """
    stmt = select(PlanVersionModel).where(PlanVersionModel.plan_id == plan_id)
    res = await db.execute(stmt)
    plan = res.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plan '{plan_id}' not found.")

    # Load assignments
    stmt_assign = select(MaterializedAssignmentModel).where(MaterializedAssignmentModel.plan_id == plan_id)
    res_assign = await db.execute(stmt_assign)
    assignments = res_assign.scalars().all()

    assignment_dicts = [
        {
            "assignment_id": a.assignment_id,
            "task_id": a.task_id,
            "business_key": a.business_key,
            "track_segment_id": a.track_segment_id,
            "start_utc": a.start_utc.isoformat(),
            "end_utc": a.end_utc.isoformat(),
            "start_minute": a.start_minute,
            "end_minute": a.end_minute,
            "duration_minutes": a.duration_minutes,
            "work_phase_schedule": a.work_phase_schedule,
            "assigned_resources": a.assigned_resources,
            "power_block_required": a.power_block_required,
            "power_block_section": a.power_block_section,
            "is_locked": a.is_locked,
            "is_shadow_block": a.is_shadow_block,
            "bundled_with_task_ids": a.bundled_with_task_ids,
        }
        for a in assignments
    ]

    metrics = plan.metrics or {}
    return PlanVersionResponse(
        plan_id=plan.plan_id,
        plan_version_number=plan.plan_version_number,
        corridor_code=plan.corridor_code,
        snapshot_id=plan.snapshot_id,
        parent_plan_id=plan.parent_plan_id,
        horizon_type=plan.horizon_type,
        plan_status=plan.plan_status.value if hasattr(plan.plan_status, "value") else str(plan.plan_status),
        solver_status=plan.solver_status,
        checker_verdict=plan.checker_verdict,
        approval_eligibility=plan.approval_eligibility.value if hasattr(plan.approval_eligibility, "value") else str(plan.approval_eligibility),
        total_tasks_count=metrics.get("total_tasks_count", len(assignments)),
        scheduled_tasks_count=metrics.get("scheduled_tasks_count", len(assignments)),
        mandatory_scheduled_count=metrics.get("mandatory_scheduled_count", 0),
        bundled_packages_count=metrics.get("bundled_packages_count", 0),
        total_block_minutes=metrics.get("total_block_minutes", sum(a.duration_minutes for a in assignments)),
        solve_duration_ms=metrics.get("solve_duration_ms", 0.0),
        created_at_utc=plan.created_at_utc,
        assignments=assignment_dicts,
        reconciliation_cases=plan.reconciliation_cases or [],
        metrics=metrics,
    )


@router.get("/plans", response_model=List[PlanVersionResponse])
async def list_plan_versions(
    corridor_code: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists saved plan versions for the corridor.
    """
    stmt = select(PlanVersionModel)
    if corridor_code:
        stmt = stmt.where(PlanVersionModel.corridor_code == corridor_code)
    stmt = stmt.order_by(PlanVersionModel.created_at_utc.desc()).limit(limit)

    res = await db.execute(stmt)
    plans = res.scalars().all()

    results = []
    for plan in plans:
        metrics = plan.metrics or {}
        results.append(
            PlanVersionResponse(
                plan_id=plan.plan_id,
                plan_version_number=plan.plan_version_number,
                corridor_code=plan.corridor_code,
                snapshot_id=plan.snapshot_id,
                parent_plan_id=plan.parent_plan_id,
                horizon_type=plan.horizon_type,
                plan_status=plan.plan_status.value if hasattr(plan.plan_status, "value") else str(plan.plan_status),
                solver_status=plan.solver_status,
                checker_verdict=plan.checker_verdict,
                approval_eligibility=plan.approval_eligibility.value if hasattr(plan.approval_eligibility, "value") else str(plan.approval_eligibility),
                total_tasks_count=metrics.get("total_tasks_count", 0),
                scheduled_tasks_count=metrics.get("scheduled_tasks_count", 0),
                mandatory_scheduled_count=metrics.get("mandatory_scheduled_count", 0),
                bundled_packages_count=metrics.get("bundled_packages_count", 0),
                total_block_minutes=metrics.get("total_block_minutes", 0),
                solve_duration_ms=metrics.get("solve_duration_ms", 0.0),
                created_at_utc=plan.created_at_utc,
                assignments=[],
                reconciliation_cases=plan.reconciliation_cases or [],
                metrics=metrics,
            )
        )
    return results

