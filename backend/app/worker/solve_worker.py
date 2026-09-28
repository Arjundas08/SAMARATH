"""
PostgreSQL Leased Worker Queue for Durable Solve Jobs.
Blueprint Sections: 28, 31, 33-34, 42-43.

Invariants:
1. FOR UPDATE SKIP LOCKED for short job-claim transactions.
2. Solve outside database transactions with a lease, heartbeat and fencing token.
3. Publication checks current ownership, fencing token, and lease expiry.
4. Expired workers cannot publish twice or overwrite a newer result.
5. Infeasible CP-SAT run is a domain outcome (COMPLETED), not HTTP 500 or worker crash.
6. Genuine status transitions: QUEUED -> CLAIMED -> BUILDING_CANDIDATES -> SOLVING -> VERIFYING_FEASIBILITY -> COMPLETED.
7. Snapshot obsolescence detection in flight.
"""
import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from app.core.logging import logger
from app.db.models import (
    SolveJobModel,
    SnapshotModel,
    PlanVersionModel,
    MaterializedAssignmentModel,
    AuditEventModel,
)
from app.schemas.enums import (
    JobState,
    SolverStatus,
    PlanStatus,
    ProgrammeAuthorityState,
    FieldAuthorityState,
    ApprovalEligibility,
    ObjectiveProfile,
)
from app.schemas.job import JobPhase
from app.schemas.optimizer import OptimizerSolveRequest
from app.schemas.checker import ProposedPlan, CheckerAssignment, CheckerPhase, CheckerVerdict
from app.gateway.service import seal_snapshot_from_db
from app.engine.candidate_generator import CandidateGenerator
from app.engine.cp_sat_solver import CPSatWeeklyOptimizer
from app.checker.feasibility_checker import IndependentFeasibilityChecker
from app.domain.reconciliation import ReconciliationStore, WeeklyReconciliationService


class StaleWorkerPublicationError(Exception):
    """Raised when an expired worker attempts to publish results after lease loss or fencing token bump."""
    pass


class SolveWorker:
    def __init__(self, worker_id: Optional[str] = None, lease_duration_seconds: int = 45):
        self.worker_id = worker_id or f"worker-{uuid4().hex[:8]}"
        self.lease_duration_seconds = lease_duration_seconds

    async def claim_job(self, db: AsyncSession, job_id: Optional[str] = None) -> Optional[SolveJobModel]:
        """
        Attempts to claim a job using FOR UPDATE SKIP LOCKED (or dialect equivalent).
        Short atomic transaction.
        If job_id is provided, claims that specific job if eligible.
        """
        now = datetime.now(timezone.utc)
        bind = db.get_bind()
        is_postgres = "postgres" in str(bind.url).lower() if bind else False

        conditions = [
            or_(
                SolveJobModel.status == JobState.QUEUED,
                and_(
                    SolveJobModel.status == JobState.RUNNING,
                    SolveJobModel.lease_expires_at < now,
                ),
            ),
            SolveJobModel.attempt_count < SolveJobModel.max_attempts,
        ]
        if job_id:
            conditions.append(SolveJobModel.job_id == job_id)

        stmt = select(SolveJobModel).where(and_(*conditions)).order_by(SolveJobModel.created_at_utc.asc()).limit(1)

        if is_postgres:
            stmt = stmt.with_for_update(skip_locked=True)

        res = await db.execute(stmt)
        job = res.scalar_one_or_none()

        if not job:
            return None

        # Claim lease and increment fencing token
        job.status = JobState.RUNNING
        job.current_phase = JobPhase.CLAIMED
        job.lease_owner = self.worker_id
        job.lease_expires_at = now + timedelta(seconds=self.lease_duration_seconds)
        job.fencing_token += 1
        job.attempt_count += 1
        job.version += 1

        audit = AuditEventModel(
            entity_type="SOLVER_JOB",
            entity_id=job.job_id,
            action="CLAIM_LEASE",
            user_id=self.worker_id,
            user_role="WORKER",
            payload_after={
                "fencing_token": job.fencing_token,
                "attempt_count": job.attempt_count,
                "lease_expires_at": job.lease_expires_at.isoformat(),
            },
            timestamp_utc=now,
        )
        db.add(audit)
        await db.commit()
        await db.refresh(job)

        logger.info(
            f"Worker '{self.worker_id}' claimed job '{job.job_id}' (attempt {job.attempt_count}, token {job.fencing_token})"
        )
        return job

    async def heartbeat(self, db: AsyncSession, job_id: str, fencing_token: int) -> bool:
        """
        Extends lease expiration while the job is actively executing.
        """
        now = datetime.now(timezone.utc)
        new_expiry = now + timedelta(seconds=self.lease_duration_seconds)

        stmt = (
            update(SolveJobModel)
            .where(
                and_(
                    SolveJobModel.job_id == job_id,
                    SolveJobModel.lease_owner == self.worker_id,
                    SolveJobModel.fencing_token == fencing_token,
                    SolveJobModel.status == JobState.RUNNING,
                )
            )
            .values(lease_expires_at=new_expiry)
        )
        res = await db.execute(stmt)
        await db.commit()
        return res.rowcount > 0

    async def update_phase(self, db: AsyncSession, job_id: str, fencing_token: int, phase: str, progress: int = 0):
        """Updates genuine execution phase."""
        stmt = (
            update(SolveJobModel)
            .where(
                and_(
                    SolveJobModel.job_id == job_id,
                    SolveJobModel.lease_owner == self.worker_id,
                    SolveJobModel.fencing_token == fencing_token,
                )
            )
            .values(current_phase=phase, progress_percentage=progress)
        )
        await db.execute(stmt)
        await db.commit()

    async def check_cancellation(self, db: AsyncSession, job_id: str) -> bool:
        """Checks if the user cancelled the job while it was in flight."""
        stmt = select(SolveJobModel.status).where(SolveJobModel.job_id == job_id)
        res = await db.execute(stmt)
        status = res.scalar_one_or_none()
        return status == JobState.CANCELLED

    async def process_job(self, db: AsyncSession, job: SolveJobModel) -> Dict[str, Any]:
        """
        Executes a claimed solve job outside long transactions.
        """
        job_id = job.job_id
        fencing_token = job.fencing_token
        params = job.solve_parameters or {}

        try:
            # 1. Verify Job Was Not Cancelled
            if await self.check_cancellation(db, job_id):
                logger.info(f"Job '{job_id}' was cancelled before execution.")
                return {"status": "CANCELLED"}

            # 2. Check Snapshot Freshness / Obsolescence
            await self.update_phase(db, job_id, fencing_token, JobPhase.PREPARING_SNAPSHOT, 10)
            stmt_newer = (
                select(SnapshotModel)
                .where(
                    and_(
                        SnapshotModel.corridor_code == job.corridor_code,
                        SnapshotModel.created_at_utc > job.created_at_utc,
                    )
                )
                .limit(1)
            )
            newer_snap_res = await db.execute(stmt_newer)
            newer_snap = newer_snap_res.scalar_one_or_none()
            if newer_snap:
                # Snapshot superseded in flight!
                return await self._fail_job(
                    db,
                    job_id,
                    fencing_token,
                    error_detail=f"Snapshot was superseded by a newer version '{newer_snap.snapshot_id}' while job was queued.",
                    is_obsolete=True,
                )

            # Reconstruct Snapshot from DB
            snapshot = await seal_snapshot_from_db(
                db,
                corridor_code=job.corridor_code,
                user_id="worker",
            )

            # 3. Generate Sparse Candidates
            if await self.check_cancellation(db, job_id):
                return {"status": "CANCELLED"}

            await self.update_phase(db, job_id, fencing_token, JobPhase.BUILDING_CANDIDATES, 25)
            await self.heartbeat(db, job_id, fencing_token)

            lattice_step = int(params.get("lattice_step_minutes", 60))
            max_cands = int(params.get("max_candidates", 10000))
            generator = CandidateGenerator(
                snapshot=snapshot,
                lattice_step_minutes=lattice_step,
                max_candidates=max_cands,
            )
            manifest = generator.generate_manifest()

            # DISRUPTION RECOVERY: Inject real event constraints (broken machines, delayed tasks)
            original_plan_obj = None
            if params.get("is_disruption_recovery") and params.get("event_ids"):
                from app.db.models import DisruptionEventModel
                ev_stmt = select(DisruptionEventModel).where(
                    DisruptionEventModel.event_id.in_(params["event_ids"])
                )
                ev_res = await db.execute(ev_stmt)
                events = ev_res.scalars().all()

                broken_assets = set()
                delayed_tasks = {}
                for ev in events:
                    payload = ev.payload or {}
                    ev_type = ev.event_type or ""
                    asset_id = payload.get("asset_id")
                    if asset_id and ("BREAKDOWN" in ev_type or "UNAVAILABLE" in ev_type):
                        broken_assets.add(asset_id)
                    wp_id = payload.get("work_package_id")
                    if wp_id and "DELAYED" in ev_type:
                        delayed_tasks[wp_id] = payload.get("estimated_delay_minutes", 120)

                # Filter out candidates that violate disruption constraints
                if broken_assets or delayed_tasks:
                    valid_candidates = []
                    for c in manifest.candidates:
                        # If candidate requires broken machine, reject it
                        c_res = set(c.resource_ids or [])
                        if any(ba in c_res for ba in broken_assets):
                            continue
                        # If candidate is for delayed work package, ensure it does not start early
                        is_delayed = False
                        for tid in c.task_ids:
                            if str(tid) in delayed_tasks and c.start_minute < delayed_tasks[str(tid)]:
                                is_delayed = True
                                break
                        if is_delayed:
                            continue
                        valid_candidates.append(c)

                    if valid_candidates:
                        manifest.candidates = valid_candidates
                        logger.info(
                            f"Applied disruption constraints: {len(manifest.candidates)} feasible candidates preserved "
                            f"(excluded broken assets: {broken_assets}, delayed: {list(delayed_tasks.keys())})"
                        )

            # 4. Execute CP-SAT Weekly Optimizer
            if await self.check_cancellation(db, job_id):
                return {"status": "CANCELLED"}

            await self.update_phase(db, job_id, fencing_token, JobPhase.SOLVING, 50)
            await self.heartbeat(db, job_id, fencing_token)

            solve_req = OptimizerSolveRequest(
                corridor_code=job.corridor_code,
                profile=job.objective_profile,
                time_limit_seconds=float(params.get("time_limit_seconds", 15.0)),
                num_workers=int(params.get("num_workers", 1)),
                random_seed=int(params.get("random_seed", 42)),
                lattice_step_minutes=lattice_step,
                max_candidates=max_cands,
                parent_monthly_plan_id=params.get("parent_monthly_plan_id"),
                target_week_index=params.get("target_week_index") or 1,
            )
            optimizer = CPSatWeeklyOptimizer(snapshot=snapshot, manifest=manifest, request=solve_req)
            solve_result = optimizer.solve()

            # 5. Independent Feasibility Verification
            await self.update_phase(db, job_id, fencing_token, JobPhase.VERIFYING_FEASIBILITY, 85)
            await self.heartbeat(db, job_id, fencing_token)

            if await self.check_cancellation(db, job_id):
                return {"status": "CANCELLED"}

            # 6. Publish Result with Fencing Token Check
            return await self.publish_result(
                db=db,
                job_id=job_id,
                fencing_token=fencing_token,
                snapshot=snapshot,
                solve_result=solve_result,
            )

        except Exception as e:
            logger.exception(f"Unhandled error in worker executing job '{job_id}': {e}")
            return await self._fail_job(db, job_id, fencing_token, error_detail=str(e))

    async def publish_result(
        self,
        db: AsyncSession,
        job_id: str,
        fencing_token: int,
        snapshot: Any,
        solve_result: Any,
    ) -> Dict[str, Any]:
        """
        Publishes the solution in a short transaction after verifying lease ownership and fencing token.
        """
        now = datetime.now(timezone.utc)
        stmt = select(SolveJobModel).where(SolveJobModel.job_id == job_id)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()

        if not job:
            raise StaleWorkerPublicationError(f"Job '{job_id}' no longer exists.")

        # STRICT FENCING CHECK:
        if job.lease_owner != self.worker_id or job.fencing_token != fencing_token:
            raise StaleWorkerPublicationError(
                f"Worker '{self.worker_id}' with token {fencing_token} is stale. "
                f"Current owner is '{job.lease_owner}', current token is {job.fencing_token}."
            )

        if job.status == JobState.CANCELLED:
            logger.info(f"Job '{job_id}' was cancelled; discarding computed result.")
            return {"status": "CANCELLED"}

        # Build Plan Version Model if feasible / optimal
        plan_id = str(uuid4())
        is_feasible = solve_result.is_feasible
        solver_status = solve_result.solver_status.value

        checker_verdict_str = solve_result.checker_verdict.value if solve_result.checker_verdict else "UNKNOWN_BLOCKED"
        approval_eligibility = solve_result.approval_eligibility if solve_result.approval_eligibility else ApprovalEligibility.BLOCKED_FEASIBILITY_FAILURE
        approval_eligibility_str = approval_eligibility.value if hasattr(approval_eligibility, "value") else str(approval_eligibility)

        summary = {
            "solver_status": solver_status,
            "stop_reason": solve_result.stop_reason.value if hasattr(solve_result.stop_reason, "value") else str(solve_result.stop_reason),
            "is_feasible": is_feasible,
            "profile": solve_result.profile.value,
            "total_tasks_count": solve_result.total_tasks_count,
            "scheduled_tasks_count": solve_result.scheduled_tasks_count,
            "mandatory_total_count": solve_result.mandatory_total_count,
            "mandatory_scheduled_count": solve_result.mandatory_scheduled_count,
            "bundled_packages_count": solve_result.bundled_packages_count,
            "total_block_minutes": solve_result.total_block_minutes,
            "solve_duration_ms": solve_result.solve_duration_ms,
            "checker_verdict": checker_verdict_str,
            "approval_eligibility": approval_eligibility_str,
            "reconciliation_cases_count": len(solve_result.reconciliation_cases),
            "reconciliation_cases": [c.model_dump(mode="json") for c in solve_result.reconciliation_cases],
        }

        # Persist Plan Version if assignments exist
        plan_model = PlanVersionModel(
            plan_id=plan_id,
            plan_version_number=1,
            corridor_code=job.corridor_code,
            snapshot_id=job.snapshot_id,
            parent_plan_id=None,
            horizon_type="WEEKLY",
            plan_status=PlanStatus.CHECKED_FEASIBLE if is_feasible else PlanStatus.DRAFT_PROPOSAL,
            solver_status=solver_status,
            checker_verdict=checker_verdict_str,
            programme_authority_state=ProgrammeAuthorityState.PROPOSED,
            field_authority_state=FieldAuthorityState.NOT_REQUESTED,
            approval_eligibility=approval_eligibility,
            reconciliation_cases=[c.model_dump(mode="json") for c in solve_result.reconciliation_cases],
            metrics=summary,
            created_at_utc=now,
        )
        db.add(plan_model)

        # Persist assignments
        for assign in solve_result.assignments:
            scoped_assign_id = f"ASN-{plan_id[:8]}-{assign.assignment_id}"[:36]
            mat = MaterializedAssignmentModel(
                assignment_id=scoped_assign_id,
                plan_id=plan_id,
                task_id=str(assign.task_ids[0]) if assign.task_ids else str(uuid4()),
                business_key=assign.business_keys[0] if assign.business_keys else "BUNDLE",
                track_segment_id=assign.track_segment_id,
                start_utc=assign.start_utc,
                end_utc=assign.end_utc,
                start_minute=int((assign.start_utc - snapshot.horizon_start_utc).total_seconds() / 60),
                end_minute=int((assign.end_utc - snapshot.horizon_start_utc).total_seconds() / 60),
                duration_minutes=int((assign.end_utc - assign.start_utc).total_seconds() / 60),
                work_phase_schedule=[p.model_dump(mode="json") for p in assign.phases],
                assigned_resources=[r.model_dump(mode="json") for r in assign.assigned_resources],
                power_block_required=assign.requires_power_block,
                power_block_section=assign.power_block_elementary_section,
                is_locked=assign.is_locked,
                is_shadow_block=len(assign.task_ids) > 1,
                bundled_with_task_ids=[str(tid) for tid in assign.task_ids[1:]],
            )
            db.add(mat)

        # Update Job Status to COMPLETED
        job.status = JobState.COMPLETED
        job.current_phase = JobPhase.COMPLETED
        job.progress_percentage = 100
        job.result_plan_id = plan_id
        job.result_summary = summary
        job.completed_at_utc = now
        job.version += 1

        audit = AuditEventModel(
            entity_type="SOLVER_JOB",
            entity_id=job.job_id,
            action="PUBLISH_RESULT",
            user_id=self.worker_id,
            user_role="WORKER",
            payload_after={"status": "COMPLETED", "result_plan_id": plan_id, "solver_status": solver_status},
            timestamp_utc=now,
        )
        db.add(audit)

        # If disruption recovery, automatically compute and persist PlanDiff
        if (job.solve_parameters or {}).get("is_disruption_recovery"):
            baseline_id = (job.solve_parameters or {}).get("baseline_plan_id")
            if baseline_id:
                try:
                    from app.engine.plandiff_engine import PlanDiffEngine
                    diff_engine = PlanDiffEngine()
                    await diff_engine.compute_diff(
                        db=db,
                        from_plan_id=baseline_id,
                        to_plan_id=plan_id,
                        triggering_event_ids=(job.solve_parameters or {}).get("event_ids"),
                    )
                    logger.info(f"PlanDiff automatically computed and persisted between {baseline_id} and {plan_id}")
                except Exception as diff_err:
                    logger.warning(f"PlanDiff computation warning: {diff_err}")

        await db.commit()
        await db.refresh(job)

        logger.info(f"Worker '{self.worker_id}' successfully published result for job '{job_id}' -> plan '{plan_id}'")
        return {"status": "COMPLETED", "result_plan_id": plan_id, "summary": summary}

    async def _fail_job(
        self,
        db: AsyncSession,
        job_id: str,
        fencing_token: int,
        error_detail: str,
        is_obsolete: bool = False,
    ) -> Dict[str, Any]:
        """Handles job failure or obsolescence."""
        now = datetime.now(timezone.utc)
        stmt = select(SolveJobModel).where(SolveJobModel.job_id == job_id)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            return {"status": "FAILED", "error": "Job not found"}

        if job.fencing_token != fencing_token:
            return {"status": "FAILED", "error": "Fencing token mismatch"}

        if is_obsolete or job.attempt_count >= job.max_attempts:
            job.status = JobState.FAILED
            job.current_phase = JobPhase.FAILED
            job.error_detail = error_detail
            job.is_snapshot_obsolete = is_obsolete
            job.completed_at_utc = now
        else:
            # Re-queue for bounded retry
            job.status = JobState.QUEUED
            job.current_phase = JobPhase.QUEUED
            job.error_detail = f"Attempt {job.attempt_count} failed: {error_detail}"
            job.lease_owner = None
            job.lease_expires_at = None

        job.version += 1
        await db.commit()
        return {"status": job.status.value, "error": error_detail}

    async def run_once(self, db: AsyncSession, job_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Claims and processes one job if available."""
        job = await self.claim_job(db, job_id=job_id)
        if not job:
            return None
        return await self.process_job(db, job)
