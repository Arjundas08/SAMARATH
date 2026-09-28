"""
Real CP-SAT Weekly Optimizer and Lexicographic Profiles.
Implements Blueprint Sections 17, 18, 19, 22, 23, 27, 42:
- Finite-placement Boolean formulation: one Boolean per candidate.
- At-most-once task coverage, mandatory equality, and hard lock preservation.
- Sparse track collision constraints and discrete-event resource capacity limits.
- Bounded multi-stage lexicographic solving with time budgeting.
- Profiles: PROGRAMME_IMPROVEMENT and DISRUPTION_RECOVERY.
- Automatic independent post-solve verification via Phase 07 Feasibility Checker.
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import time
from ortools.sat.python import cp_model

from app.schemas.enums import (
    CriticalityTier,
    ObjectiveProfile,
    SolverStatus,
    StopReason,
    ResourceType,
    ApprovalEligibility,
)
from app.schemas.task import Task
from app.schemas.snapshot import Snapshot, LockedCommitment
from app.schemas.candidate import PlacementCandidate, CandidateManifest
from app.schemas.checker import (
    ProposedPlan,
    CheckerAssignment,
    CheckerPhase,
    CheckerReport,
    CheckerVerdict,
)
from app.schemas.optimizer import (
    OptimizerSolveRequest,
    OptimizerSolveResult,
    OptimizerStageMetric,
)
from app.checker.feasibility_checker import IndependentFeasibilityChecker
from app.engine.greedy_baseline import GreedyBaselineSolver


class CPSatWeeklyOptimizer:
    """
    Real OR-Tools CP-SAT Weekly Maintenance Optimizer.
    """

    def __init__(
        self,
        snapshot: Snapshot,
        manifest: CandidateManifest,
        request: OptimizerSolveRequest,
    ):
        self.snapshot = snapshot
        self.manifest = manifest
        self.request = request
        self.h_start = snapshot.horizon_start_utc
        self.h_end = snapshot.horizon_end_utc
        self.tasks_by_id: Dict[UUID, Task] = {t.task_id: t for t in snapshot.tasks}
        self.checker = IndependentFeasibilityChecker(snapshot)

    def solve(self) -> OptimizerSolveResult:
        wall_start = time.perf_counter()
        time_budget_sec = max(1.0, float(self.request.time_limit_seconds))

        candidates = self.manifest.candidates
        tasks = self.snapshot.tasks

        # Quick infeasibility check for mandatory tasks
        mandatory_tasks = [t for t in tasks if t.criticality == CriticalityTier.TIER_1_MANDATORY]
        candidates_by_task: Dict[UUID, List[PlacementCandidate]] = defaultdict(list)
        for c in candidates:
            for tid in c.task_ids:
                candidates_by_task[tid].append(c)

        for mt in mandatory_tasks:
            if not candidates_by_task.get(mt.task_id):
                # No candidates exist for a mandatory task -> infeasible
                return OptimizerSolveResult(
                    solver_status=SolverStatus.INFEASIBLE,
                    stop_reason=StopReason.INFEASIBILITY_PROVEN,
                    is_feasible=False,
                    profile=self.request.profile,
                    total_tasks_count=len(tasks),
                    scheduled_tasks_count=0,
                    mandatory_total_count=len(mandatory_tasks),
                    mandatory_scheduled_count=0,
                    bundled_packages_count=0,
                    total_block_minutes=0,
                    solve_duration_ms=(time.perf_counter() - wall_start) * 1000.0,
                    stage_metrics=[
                        OptimizerStageMetric(
                            stage_index=1,
                            stage_name="MANDATORY_FEASIBILITY_CHECK",
                            objective_unit="status",
                            status="INFEASIBLE_NO_CANDIDATE_FOR_MANDATORY_TASK",
                            duration_ms=(time.perf_counter() - wall_start) * 1000.0,
                        )
                    ],
                    metadata={"error": f"Mandatory task {mt.business_key} has 0 eligible placement candidates"},
                )

        # Build CP-SAT Model
        model = cp_model.CpModel()

        # 1. Decision Variables
        # x[c.candidate_id] in {0, 1}
        x: Dict[str, cp_model.IntVar] = {}
        intervals: Dict[str, cp_model.IntervalVar] = {}
        for c in candidates:
            x[c.candidate_id] = model.NewBoolVar(f"x_{c.candidate_id}")
            intervals[c.candidate_id] = model.NewOptionalIntervalVar(
                start=c.start_minute,
                size=c.duration_minutes,
                end=c.end_minute,
                is_present=x[c.candidate_id],
                name=f"iv_{c.candidate_id}",
            )

        # u[task_id] in {0, 1}
        u: Dict[UUID, cp_model.IntVar] = {}
        for t in tasks:
            u[t.task_id] = model.NewBoolVar(f"u_{t.task_id}")

        # 2. Coverage Constraints: sum_{c covering t} x[c] == u[t] <= 1
        for t in tasks:
            cands_for_t = candidates_by_task.get(t.task_id, [])
            if cands_for_t:
                model.Add(sum(x[c.candidate_id] for c in cands_for_t) == u[t.task_id])
            else:
                model.Add(u[t.task_id] == 0)

        # 3. Mandatory Tasks Equality: u[t] == 1
        for mt in mandatory_tasks:
            model.Add(u[mt.task_id] == 1)

        # 4. Hard Lock Commitments Equality
        for lock in self.snapshot.locked_commitments:
            lock_min = int((lock.start_utc - self.h_start).total_seconds() // 60)
            matching_cands = [
                c for c in candidates_by_task.get(lock.task_id, [])
                if c.start_minute == lock_min
            ]
            if matching_cands:
                # Must select exactly one matching candidate
                model.Add(sum(x[c.candidate_id] for c in matching_cands) == 1)
            else:
                # Lock cannot be met -> INFEASIBLE
                return OptimizerSolveResult(
                    solver_status=SolverStatus.INFEASIBLE,
                    stop_reason=StopReason.INFEASIBILITY_PROVEN,
                    is_feasible=False,
                    profile=self.request.profile,
                    total_tasks_count=len(tasks),
                    scheduled_tasks_count=0,
                    mandatory_total_count=len(mandatory_tasks),
                    mandatory_scheduled_count=0,
                    bundled_packages_count=0,
                    total_block_minutes=0,
                    solve_duration_ms=(time.perf_counter() - wall_start) * 1000.0,
                    metadata={"error": f"Hard lock {lock.commitment_id} has no matching candidate"},
                )

        # 5. Track Segment Non-Overlap Constraints via Sparse Optional Intervals
        track_intervals: Dict[str, List[cp_model.IntervalVar]] = defaultdict(list)
        for c in candidates:
            all_tracks = [c.track_segment_id] + c.isolated_tracks
            for trk in set(all_tracks):
                track_intervals[trk].append(intervals[c.candidate_id])

        for trk, iv_list in track_intervals.items():
            model.AddNoOverlap(iv_list)

        # 6. Resource Capacity Constraints via Sparse Intervals
        res_intervals: Dict[str, List[cp_model.IntervalVar]] = defaultdict(list)
        for c in candidates:
            for r in c.assigned_resources:
                res_intervals[r].append(intervals[c.candidate_id])

        for r_id, iv_list in res_intervals.items():
            cap = 2 if "SUPERVISOR" in r_id.upper() or "SUP-" in r_id.upper() else 1
            if cap == 1:
                model.AddNoOverlap(iv_list)
            else:
                demands = [1] * len(iv_list)
                model.AddCumulative(iv_list, demands, cap)

        # Warmstart hint injection via greedy baseline
        if self.request.profile != ObjectiveProfile.DISRUPTION_RECOVERY:
            try:
                baseline = GreedyBaselineSolver(self.snapshot, self.manifest)
                b_res = baseline.solve()
                if b_res.is_feasible:
                    chosen_cids = {a.candidate_id for a in b_res.assignments}
                    covered_tids = {tid for a in b_res.assignments for tid in a.task_ids}
                    for c in candidates:
                        model.AddHint(x[c.candidate_id], 1 if c.candidate_id in chosen_cids else 0)
                    for t in tasks:
                        model.AddHint(u[t.task_id], 1 if t.task_id in covered_tids else 0)
            except Exception:
                pass

        # 7. Lexicographic Multi-Stage Objective Solving
        stage_metrics: List[OptimizerStageMetric] = []
        best_solution: Dict[str, int] = {}
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = self.request.num_workers
        solver.parameters.random_seed = self.request.random_seed

        if self.request.profile == ObjectiveProfile.DISRUPTION_RECOVERY:
            # Profile: DISRUPTION_RECOVERY
            # Stage 1: Maximize mandatory tasks (already enforced by hard equality)
            # Stage 2: Minimize deviation from original plan
            orig_plan = self.request.original_plan
            orig_starts: Dict[UUID, int] = {}
            if orig_plan:
                for a in orig_plan.assignments:
                    for tid in a.task_ids:
                        s_min = int((a.start_utc - self.h_start).total_seconds() // 60)
                        orig_starts[tid] = s_min

            churn_terms = []
            for c in candidates:
                for tid in c.task_ids:
                    if tid in orig_starts:
                        orig_m = orig_starts[tid]
                        # Reschedule cost = time shift in units of 15m + movement fixed fee (100)
                        shift = abs(c.start_minute - orig_m) // 15
                        move_penalty = 0 if shift == 0 else (100 + shift)
                        churn_terms.append(x[c.candidate_id] * move_penalty)

            # Penalty for cancelling previously scheduled tasks
            for tid, _ in orig_starts.items():
                if tid in u:
                    churn_terms.append((1 - u[tid]) * 1000)

            # Stage 1: Minimize Churn
            time_remaining = max(1.0, time_budget_sec - (time.perf_counter() - wall_start))
            solver.parameters.max_time_in_seconds = time_remaining
            s1_start = time.perf_counter()
            model.Minimize(sum(churn_terms))
            s1_status = solver.Solve(model)
            s1_dur = (time.perf_counter() - s1_start) * 1000.0

            if s1_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                best_churn = int(solver.ObjectiveValue())
                best_solution = {c.candidate_id: solver.Value(x[c.candidate_id]) for c in candidates}
                stage_metrics.append(
                    OptimizerStageMetric(
                        stage_index=1,
                        stage_name="MINIMIZE_SCHEDULE_CHURN",
                        objective_unit="penalty_points",
                        best_objective_value=best_churn,
                        best_bound=int(solver.BestObjectiveBound()) if s1_status == cp_model.OPTIMAL else None,
                        status="OPTIMAL" if s1_status == cp_model.OPTIMAL else "FEASIBLE",
                        duration_ms=s1_dur,
                    )
                )
                if s1_status == cp_model.OPTIMAL:
                    model.Add(sum(churn_terms) <= best_churn)

                # Stage 2: Minimize total block minutes
                time_remaining = max(1.0, time_budget_sec - (time.perf_counter() - wall_start))
                solver.parameters.max_time_in_seconds = time_remaining
                s2_start = time.perf_counter()
                total_duration_expr = sum(x[c.candidate_id] * c.duration_minutes for c in candidates)
                model.Minimize(total_duration_expr)
                s2_status = solver.Solve(model)
                s2_dur = (time.perf_counter() - s2_start) * 1000.0
                if s2_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                    best_solution = {c.candidate_id: solver.Value(x[c.candidate_id]) for c in candidates}
                    stage_metrics.append(
                        OptimizerStageMetric(
                            stage_index=2,
                            stage_name="MINIMIZE_TOTAL_BLOCK_MINUTES",
                            objective_unit="minutes",
                            best_objective_value=int(solver.ObjectiveValue()),
                            best_bound=int(solver.BestObjectiveBound()) if s2_status == cp_model.OPTIMAL else None,
                            status="OPTIMAL" if s2_status == cp_model.OPTIMAL else "FEASIBLE",
                            duration_ms=s2_dur,
                        )
                    )
            else:
                return self._build_infeasible_or_timeout_result(s1_status, wall_start, stage_metrics)

        else:
            # Profile: PROGRAMME_IMPROVEMENT
            # Stage 1: Maximize Priority Work (Tier 2 weight 10, Tier 3 weight 1)
            priority_expr = sum(
                u[t.task_id] * (10 if t.criticality == CriticalityTier.TIER_2_SPEED_RESTRICTION else 1)
                for t in tasks
                if t.criticality != CriticalityTier.TIER_1_MANDATORY
            )

            time_remaining = max(1.0, time_budget_sec - (time.perf_counter() - wall_start))
            solver.parameters.max_time_in_seconds = time_remaining
            s1_start = time.perf_counter()
            model.Maximize(priority_expr)
            s1_status = solver.Solve(model)
            s1_dur = (time.perf_counter() - s1_start) * 1000.0

            if s1_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                best_priority = int(solver.ObjectiveValue())
                best_solution = {c.candidate_id: solver.Value(x[c.candidate_id]) for c in candidates}
                stage_metrics.append(
                    OptimizerStageMetric(
                        stage_index=1,
                        stage_name="MAXIMIZE_HIGH_PRIORITY_TASKS",
                        objective_unit="priority_score",
                        best_objective_value=best_priority,
                        best_bound=int(solver.BestObjectiveBound()) if s1_status == cp_model.OPTIMAL else None,
                        status="OPTIMAL" if s1_status == cp_model.OPTIMAL else "FEASIBLE",
                        duration_ms=s1_dur,
                    )
                )
                if s1_status == cp_model.OPTIMAL:
                    model.Add(priority_expr >= best_priority)

                # Stage 2: Maximize Bundled Packages
                time_remaining = max(1.0, time_budget_sec - (time.perf_counter() - wall_start))
                solver.parameters.max_time_in_seconds = time_remaining
                s2_start = time.perf_counter()
                bundle_expr = sum(x[c.candidate_id] for c in candidates if len(c.task_ids) > 1)
                model.Maximize(bundle_expr)
                s2_status = solver.Solve(model)
                s2_dur = (time.perf_counter() - s2_start) * 1000.0

                if s2_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                    best_bundles = int(solver.ObjectiveValue())
                    best_solution = {c.candidate_id: solver.Value(x[c.candidate_id]) for c in candidates}
                    stage_metrics.append(
                        OptimizerStageMetric(
                            stage_index=2,
                            stage_name="MAXIMIZE_BUNDLED_PACKAGES",
                            objective_unit="packages_count",
                            best_objective_value=best_bundles,
                            best_bound=int(solver.BestObjectiveBound()) if s2_status == cp_model.OPTIMAL else None,
                            status="OPTIMAL" if s2_status == cp_model.OPTIMAL else "FEASIBLE",
                            duration_ms=s2_dur,
                        )
                    )
                    if s2_status == cp_model.OPTIMAL:
                        model.Add(bundle_expr >= best_bundles)

                    # Stage 3: Minimize Total Possession Block Minutes
                    time_remaining = max(1.0, time_budget_sec - (time.perf_counter() - wall_start))
                    solver.parameters.max_time_in_seconds = time_remaining
                    s3_start = time.perf_counter()
                    total_dur_expr = sum(x[c.candidate_id] * c.duration_minutes for c in candidates)
                    model.Minimize(total_dur_expr)
                    s3_status = solver.Solve(model)
                    s3_dur = (time.perf_counter() - s3_start) * 1000.0
                    if s3_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                        best_solution = {c.candidate_id: solver.Value(x[c.candidate_id]) for c in candidates}
                        stage_metrics.append(
                            OptimizerStageMetric(
                                stage_index=3,
                                stage_name="MINIMIZE_POSSESSION_MINUTES",
                                objective_unit="minutes",
                                best_objective_value=int(solver.ObjectiveValue()),
                                best_bound=int(solver.BestObjectiveBound()) if s3_status == cp_model.OPTIMAL else None,
                                status="OPTIMAL" if s3_status == cp_model.OPTIMAL else "FEASIBLE",
                                duration_ms=s3_dur,
                            )
                        )
            else:
                return self._build_infeasible_or_timeout_result(s1_status, wall_start, stage_metrics)

        # 8. Extract Assignments from Qualified Incumbent
        chosen_candidates: List[PlacementCandidate] = [
            c for c in candidates
            if best_solution.get(c.candidate_id, 0) == 1
        ]

        assignments: List[CheckerAssignment] = []
        for c in chosen_candidates:
            phases = [
                CheckerPhase(
                    phase_name="SETUP",
                    start_utc=c.start_utc,
                    end_utc=c.start_utc + timedelta(minutes=15),
                    required_resources=c.assigned_resources,
                ),
                CheckerPhase(
                    phase_name="EXECUTION",
                    start_utc=c.start_utc + timedelta(minutes=15),
                    end_utc=c.end_utc - timedelta(minutes=15),
                    required_resources=c.assigned_resources,
                ),
                CheckerPhase(
                    phase_name="RESTORATION",
                    start_utc=c.end_utc - timedelta(minutes=15),
                    end_utc=c.end_utc,
                    required_resources=c.assigned_resources,
                ),
            ]

            assignments.append(
                CheckerAssignment(
                    assignment_id=f"OPT-ASSIGN-{c.candidate_id}",
                    task_ids=c.task_ids,
                    business_keys=c.business_keys,
                    track_segment_id=c.track_segment_id,
                    start_utc=c.start_utc,
                    end_utc=c.end_utc,
                    assigned_resources=c.assigned_resources,
                    phases=phases,
                    requires_power_block=c.requires_power_block,
                    power_block_elementary_section=c.power_block_elementary_section,
                    isolated_tracks=c.isolated_tracks,
                    is_locked=c.is_locked,
                )
            )

        # 9. Verify through Independent Feasibility Checker (Phase 07)
        plan = ProposedPlan(
            plan_id=f"PLAN-CP-SAT-{int(datetime.now(timezone.utc).timestamp())}",
            corridor_code=self.snapshot.corridor_code,
            snapshot_id=self.snapshot.snapshot_id,
            snapshot_hash=self.snapshot.snapshot_hash,
            assignments=assignments,
            metadata={"solver": "OR-TOOLS-CP-SAT", "profile": self.request.profile.value},
        )
        checker_report = self.checker.verify_plan(plan)

        scheduled_task_ids = {tid for c in chosen_candidates for tid in c.task_ids}
        mand_sched_count = sum(1 for mt in mandatory_tasks if mt.task_id in scheduled_task_ids)
        bundled_count = sum(1 for c in chosen_candidates if len(c.task_ids) > 1)
        total_duration = sum(c.duration_minutes for c in chosen_candidates)
        elapsed_ms = (time.perf_counter() - wall_start) * 1000.0
        is_optimal = bool(stage_metrics and all(m.status == "OPTIMAL" for m in stage_metrics))

        # Phase 09 Two-Horizon Reconciliation
        reconciliation_cases = []
        approval_eligibility = ApprovalEligibility.ELIGIBLE
        if self.request.parent_monthly_plan_id:
            from app.domain.reconciliation import ReconciliationStore, WeeklyReconciliationService
            parent_plan = ReconciliationStore.get_plan(self.request.parent_monthly_plan_id)
            if parent_plan:
                recon_service = WeeklyReconciliationService(parent_plan)
                reconciliation_cases, approval_eligibility = recon_service.reconcile_weekly_schedule(
                    child_weekly_plan_id=plan.plan_id,
                    target_week_index=self.request.target_week_index,
                    scheduled_task_ids=list(scheduled_task_ids),
                    total_duration_minutes=total_duration,
                    is_solver_feasible=checker_report.verdict == CheckerVerdict.VALID,
                    solver_error_msg=None if checker_report.verdict == CheckerVerdict.VALID else str([v.violation_type for v in checker_report.violations]),
                )

        return OptimizerSolveResult(
            solver_status=SolverStatus.OPTIMAL if is_optimal else SolverStatus.FEASIBLE,
            stop_reason=StopReason.OPTIMAL_PROVEN if is_optimal else StopReason.TIME_LIMIT_REACHED,
            is_feasible=checker_report.verdict == CheckerVerdict.VALID,
            profile=self.request.profile,
            total_tasks_count=len(tasks),
            scheduled_tasks_count=len(scheduled_task_ids),
            mandatory_total_count=len(mandatory_tasks),
            mandatory_scheduled_count=mand_sched_count,
            bundled_packages_count=bundled_count,
            total_block_minutes=total_duration,
            solve_duration_ms=elapsed_ms,
            stage_metrics=stage_metrics,
            assignments=assignments,
            checker_verdict=checker_report.verdict,
            checker_report=checker_report,
            is_truncated=self.manifest.is_truncated,
            parent_monthly_plan_id=self.request.parent_monthly_plan_id,
            target_week_index=self.request.target_week_index if self.request.parent_monthly_plan_id else None,
            reconciliation_cases=reconciliation_cases,
            approval_eligibility=approval_eligibility,
            metadata={
                "candidate_count": len(candidates),
                "num_workers": self.request.num_workers,
                "random_seed": self.request.random_seed,
                "model_evidence_set": checker_report.model_evidence_set,
            },
        )

    def _build_infeasible_or_timeout_result(
        self,
        status: int,
        wall_start: float,
        stage_metrics: List[OptimizerStageMetric],
    ) -> OptimizerSolveResult:
        elapsed_ms = (time.perf_counter() - wall_start) * 1000.0
        mandatory_tasks = [t for t in self.snapshot.tasks if t.criticality == CriticalityTier.TIER_1_MANDATORY]

        rec_cases = []
        eligibility = ApprovalEligibility.BLOCKED_CHECK_FAILED
        if self.request.parent_monthly_plan_id:
            from app.domain.reconciliation import ReconciliationStore, WeeklyReconciliationService
            parent_plan = ReconciliationStore.get_plan(self.request.parent_monthly_plan_id)
            if parent_plan:
                recon_service = WeeklyReconciliationService(parent_plan)
                rec_cases, eligibility = recon_service.reconcile_weekly_schedule(
                    child_weekly_plan_id=f"PLAN-CP-SAT-{int(datetime.now(timezone.utc).timestamp())}",
                    target_week_index=self.request.target_week_index,
                    scheduled_task_ids=[],
                    total_duration_minutes=0,
                    is_solver_feasible=False,
                    solver_error_msg=(
                        "CP-SAT proved mathematically infeasible under mandatory constraints in declared domain"
                        if status == cp_model.INFEASIBLE
                        else f"CP-SAT time limit reached ({self.request.time_limit_seconds}s)"
                    ),
                )

        if status == cp_model.INFEASIBLE:
            return OptimizerSolveResult(
                solver_status=SolverStatus.INFEASIBLE,
                stop_reason=StopReason.INFEASIBILITY_PROVEN,
                is_feasible=False,
                profile=self.request.profile,
                total_tasks_count=len(self.snapshot.tasks),
                scheduled_tasks_count=0,
                mandatory_total_count=len(mandatory_tasks),
                mandatory_scheduled_count=0,
                bundled_packages_count=0,
                total_block_minutes=0,
                solve_duration_ms=elapsed_ms,
                stage_metrics=stage_metrics,
                parent_monthly_plan_id=self.request.parent_monthly_plan_id,
                target_week_index=self.request.target_week_index if self.request.parent_monthly_plan_id else None,
                reconciliation_cases=rec_cases,
                approval_eligibility=eligibility,
            )
        else:
            return OptimizerSolveResult(
                solver_status=SolverStatus.TIME_LIMIT,
                stop_reason=StopReason.TIME_LIMIT_REACHED,
                is_feasible=False,
                profile=self.request.profile,
                total_tasks_count=len(self.snapshot.tasks),
                scheduled_tasks_count=0,
                mandatory_total_count=len(mandatory_tasks),
                mandatory_scheduled_count=0,
                bundled_packages_count=0,
                total_block_minutes=0,
                solve_duration_ms=elapsed_ms,
                stage_metrics=stage_metrics,
                parent_monthly_plan_id=self.request.parent_monthly_plan_id,
                target_week_index=self.request.target_week_index if self.request.parent_monthly_plan_id else None,
                reconciliation_cases=rec_cases,
                approval_eligibility=eligibility,
            )
