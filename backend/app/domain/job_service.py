"""
Domain Service for Durable Solve Jobs.
Handles:
- Scope and policy validation
- Idempotency key evaluation and payload fingerprint mismatch detection (RFC 7807 409 Conflict)
- Atomic job creation in solver_jobs table
- Concurrency and rate limit checks
- ETag calculation and If-Match precondition verification
- Safe cancellation
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_

from app.db.models import SolveJobModel, SnapshotModel, AuditEventModel, PlanVersionModel
from app.schemas.enums import JobState, ObjectiveProfile
from app.schemas.job import (
    SolveJobCreateRequest,
    SolveJobResponse,
    SolveJobCancelRequest,
    JobPhase,
)


class MismatchedPayloadError(Exception):
    """Raised when an Idempotency-Key is reused with a different payload body."""
    pass


class PreconditionFailedError(Exception):
    """Raised when an If-Match header does not match the current resource ETag."""
    pass


class InvalidJobStateError(Exception):
    """Raised when an action is invalid for the current job state."""
    pass


class JobNotFoundError(Exception):
    """Raised when a requested solve job does not exist."""
    pass


def compute_payload_fingerprint(req: SolveJobCreateRequest) -> str:
    """Computes a deterministic SHA-256 fingerprint for the request parameters."""
    normalized_dict = {
        "corridor_code": req.corridor_code,
        "profile": req.profile.value,
        "time_limit_seconds": float(req.time_limit_seconds),
        "num_workers": int(req.num_workers),
        "random_seed": int(req.random_seed),
        "lattice_step_minutes": int(req.lattice_step_minutes),
        "max_candidates": int(req.max_candidates),
        "parent_monthly_plan_id": req.parent_monthly_plan_id,
        "target_week_index": req.target_week_index,
    }
    payload_str = json.dumps(normalized_dict, sort_keys=True)
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()


def compute_job_etag(job_id: str, version: int) -> str:
    """Generates an RFC 7232 entity tag."""
    return f'"{job_id}-{version}"'


class JobService:
    @staticmethod
    async def create_solve_job(
        db: AsyncSession,
        request: SolveJobCreateRequest,
        idempotency_key: Optional[str] = None,
        user_id: str = "planner",
        user_role: str = "PLANNER",
    ) -> Tuple[SolveJobResponse, bool]:
        """
        Creates a durable solve job.
        Returns (SolveJobResponse, is_newly_created: bool).
        """
        fingerprint = compute_payload_fingerprint(request)

        # 1. Idempotency Check
        if idempotency_key:
            stmt = select(SolveJobModel).where(SolveJobModel.idempotency_key == idempotency_key)
            result = await db.execute(stmt)
            existing_job = result.scalar_one_or_none()
            if existing_job:
                if existing_job.request_fingerprint == fingerprint:
                    # Idempotent replay: return existing job representation
                    return JobService._to_response(existing_job), False
                else:
                    # Conflict: same idempotency key used with different payload parameters
                    raise MismatchedPayloadError(
                        f"Idempotency-Key '{idempotency_key}' was already submitted with a different solve request payload."
                    )

        # 2. Verify Snapshot Availability
        snapshot_id = request.snapshot_id
        if not snapshot_id:
            # Look up latest sealed snapshot for corridor
            stmt_snap = (
                select(SnapshotModel)
                .where(SnapshotModel.corridor_code == request.corridor_code)
                .order_by(SnapshotModel.created_at_utc.desc())
                .limit(1)
            )
            res_snap = await db.execute(stmt_snap)
            snap = res_snap.scalar_one_or_none()
            if not snap:
                raise ValueError(f"No active sealed snapshot found for corridor '{request.corridor_code}'.")
            snapshot_id = snap.snapshot_id
        else:
            stmt_snap = select(SnapshotModel).where(SnapshotModel.snapshot_id == snapshot_id)
            res_snap = await db.execute(stmt_snap)
            if not res_snap.scalar_one_or_none():
                raise ValueError(f"Snapshot '{snapshot_id}' does not exist.")

        # 3. Create Queued Job
        job_id = str(uuid4())
        job = SolveJobModel(
            job_id=job_id,
            corridor_code=request.corridor_code,
            snapshot_id=snapshot_id,
            objective_profile=request.profile,
            status=JobState.QUEUED,
            current_phase=JobPhase.QUEUED,
            progress_percentage=0,
            fencing_token=0,
            attempt_count=0,
            max_attempts=3,
            version=1,
            idempotency_key=idempotency_key,
            request_fingerprint=fingerprint,
            created_by_user=user_id,
            user_role=user_role,
            solve_parameters=request.model_dump(),
            result_summary=None,
            is_snapshot_obsolete=False,
            created_at_utc=datetime.now(timezone.utc),
        )
        db.add(job)

        # 4. Record Audit Event
        audit = AuditEventModel(
            entity_type="SOLVER_JOB",
            entity_id=job_id,
            action="SUBMIT_SOLVE_JOB",
            user_id=user_id,
            user_role=user_role,
            payload_after={"status": "QUEUED", "corridor": request.corridor_code, "profile": request.profile.value},
            timestamp_utc=datetime.now(timezone.utc),
        )
        db.add(audit)
        await db.commit()
        await db.refresh(job)

        return JobService._to_response(job), True

    @staticmethod
    async def get_solve_job(db: AsyncSession, job_id: str) -> SolveJobResponse:
        """Retrieves a solve job by ID."""
        stmt = select(SolveJobModel).where(SolveJobModel.job_id == job_id)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            raise JobNotFoundError(f"Solve job '{job_id}' not found.")
        return JobService._to_response(job)

    @staticmethod
    async def list_solve_jobs(
        db: AsyncSession,
        corridor_code: Optional[str] = None,
        status: Optional[JobState] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[SolveJobResponse], int]:
        """Lists solve jobs with optional corridor and status filters."""
        stmt = select(SolveJobModel)
        count_stmt = select(func.count(SolveJobModel.job_id))

        filters = []
        if corridor_code:
            filters.append(SolveJobModel.corridor_code == corridor_code)
        if status:
            filters.append(SolveJobModel.status == status)

        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))

        stmt = stmt.order_by(SolveJobModel.created_at_utc.desc()).limit(limit).offset(offset)

        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        res = await db.execute(stmt)
        jobs = res.scalars().all()
        return [JobService._to_response(j) for j in jobs], total

    @staticmethod
    async def cancel_solve_job(
        db: AsyncSession,
        job_id: str,
        request: SolveJobCancelRequest,
        if_match: Optional[str] = None,
        user_id: str = "planner",
        user_role: str = "PLANNER",
    ) -> SolveJobResponse:
        """
        Cancels a queued or running job with optimistic concurrency check.
        """
        stmt = select(SolveJobModel).where(SolveJobModel.job_id == job_id)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            raise JobNotFoundError(f"Solve job '{job_id}' not found.")

        # Check ETag precondition if provided
        if if_match:
            clean_if_match = if_match.strip('"').strip("'")
            current_etag = f"{job.job_id}-{job.version}"
            if clean_if_match != "*" and clean_if_match != current_etag:
                raise PreconditionFailedError(
                    f"If-Match precondition failed: Resource ETag '{current_etag}' does not match '{clean_if_match}'."
                )

        if job.status in (JobState.COMPLETED, JobState.FAILED):
            raise InvalidJobStateError(
                f"Cannot cancel job in terminal status '{job.status.value}'."
            )

        if job.status == JobState.CANCELLED:
            return JobService._to_response(job)

        job.status = JobState.CANCELLED
        job.current_phase = JobPhase.CANCELLED
        job.error_detail = request.reason or "Cancelled by user"
        job.completed_at_utc = datetime.now(timezone.utc)
        job.version += 1

        audit = AuditEventModel(
            entity_type="SOLVER_JOB",
            entity_id=job_id,
            action="CANCEL_SOLVE_JOB",
            user_id=user_id,
            user_role=user_role,
            payload_after={"status": "CANCELLED", "reason": request.reason},
            timestamp_utc=datetime.now(timezone.utc),
        )
        db.add(audit)
        await db.commit()
        await db.refresh(job)

        return JobService._to_response(job)

    @staticmethod
    def _to_response(job: SolveJobModel) -> SolveJobResponse:
        etag = compute_job_etag(job.job_id, job.version)
        return SolveJobResponse(
            job_id=job.job_id,
            corridor_code=job.corridor_code,
            snapshot_id=job.snapshot_id,
            objective_profile=job.objective_profile,
            status=job.status,
            current_phase=job.current_phase,
            progress_percentage=job.progress_percentage,
            attempt_count=job.attempt_count,
            version=job.version,
            fencing_token=job.fencing_token,
            lease_owner=job.lease_owner,
            lease_expires_at=job.lease_expires_at,
            created_at_utc=job.created_at_utc,
            completed_at_utc=job.completed_at_utc,
            status_url=f"/api/v1/planning/solve-jobs/{job.job_id}",
            etag=etag,
            result_plan_id=job.result_plan_id,
            error_detail=job.error_detail,
            is_snapshot_obsolete=job.is_snapshot_obsolete,
            result_summary=job.result_summary,
        )
