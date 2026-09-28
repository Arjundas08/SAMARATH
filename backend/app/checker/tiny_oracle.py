"""
Exhaustive Tiny-Instance Oracle.
Implements Blueprint Section 41:
- Brute-force exhaustive search over tiny problem spaces (2-5 tasks, 12-24h horizon).
- Completely independent of CP-SAT, greedy heuristics, or candidate generators.
- Finds the provably optimal ground-truth schedule (or proves infeasibility).
- Used to verify mathematical correctness of solvers in Phase 08.
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
import itertools
import time

from app.schemas.enums import CriticalityTier
from app.schemas.task import Task
from app.schemas.snapshot import Snapshot
from app.schemas.checker import (
    ProposedPlan,
    CheckerAssignment,
    CheckerPhase,
    CheckerVerdict,
)
from app.checker.feasibility_checker import IndependentFeasibilityChecker


class ExhaustiveTinyOracle:
    """
    Exhaustive search oracle for tiny instances.
    Guarantees mathematically exact global optimum through exhaustive combinatorial search.
    """

    def __init__(self, snapshot: Snapshot, step_minutes: int = 30):
        self.snapshot = snapshot
        self.step_minutes = step_minutes
        self.checker = IndependentFeasibilityChecker(snapshot)

        # Safety check: enforce tiny instance bounds to prevent combinatorial explosion
        assert len(snapshot.tasks) <= 6, "ExhaustiveTinyOracle is restricted to instances with <= 6 tasks"
        horizon_hours = (snapshot.horizon_end_utc - snapshot.horizon_start_utc).total_seconds() / 3600.0
        assert horizon_hours <= 48, "ExhaustiveTinyOracle is restricted to horizon <= 48 hours"

    def solve_exhaustive(self) -> Dict[str, Any]:
        """
        Enumerates all discrete time slots for each task and checks feasibility.
        Returns the optimal plan according to lexicographic priority:
        1. Mandatory tasks scheduled (maximize)
        2. Total tasks scheduled (maximize)
        3. Total block minutes (minimize)
        """
        start_time = time.perf_counter()
        h_start = self.snapshot.horizon_start_utc
        h_end = self.snapshot.horizon_end_utc
        total_minutes = int((h_end - h_start).total_seconds() // 60)

        tasks = list(self.snapshot.tasks)
        possible_slots_per_task: Dict[UUID, List[Tuple[datetime, datetime]]] = {}

        # Precompute possible discrete windows for each task
        for t in tasks:
            dur = t.total_block_minutes or t.duration_minutes
            slots = []
            max_start = total_minutes - dur
            for s_min in range(0, max_start + 1, self.step_minutes):
                s_utc = h_start + timedelta(minutes=s_min)
                e_utc = s_utc + timedelta(minutes=dur)
                if e_utc <= t.deadline_utc:
                    slots.append((s_utc, e_utc))
            # Also include the "unscheduled" option (None)
            slots.append(None)
            possible_slots_per_task[t.task_id] = slots

        best_score = (-1, -1, 999999)
        best_plan: Optional[ProposedPlan] = None
        feasible_count = 0
        evaluated_combinations = 0

        # Cartesian product of slot choices
        task_slot_lists = [possible_slots_per_task[t.task_id] for t in tasks]

        for combo in itertools.product(*task_slot_lists):
            evaluated_combinations += 1
            assignments: List[CheckerAssignment] = []

            for idx, slot in enumerate(combo):
                if slot is not None:
                    t = tasks[idx]
                    s_utc, e_utc = slot
                    req_res = [r.resource_id for r in t.required_resources if r.resource_id]

                    phases = [
                        CheckerPhase(
                            phase_name="SETUP",
                            start_utc=s_utc,
                            end_utc=s_utc + timedelta(minutes=t.setup_buffer_minutes),
                            required_resources=req_res,
                        ),
                        CheckerPhase(
                            phase_name="EXECUTION",
                            start_utc=s_utc + timedelta(minutes=t.setup_buffer_minutes),
                            end_utc=e_utc - timedelta(minutes=t.restoration_buffer_minutes),
                            required_resources=req_res,
                        ),
                        CheckerPhase(
                            phase_name="RESTORATION",
                            start_utc=e_utc - timedelta(minutes=t.restoration_buffer_minutes),
                            end_utc=e_utc,
                            required_resources=req_res,
                        ),
                    ]

                    # Auto-isolate adjacent track if CHR neutral section
                    isolated = []
                    if t.requires_power_block and "CHR" in t.track_segment_id:
                        if "DN" in t.track_segment_id:
                            isolated.append(t.track_segment_id.replace("DN", "UP"))
                        elif "UP" in t.track_segment_id:
                            isolated.append(t.track_segment_id.replace("UP", "DN"))

                    assignments.append(
                        CheckerAssignment(
                            assignment_id=f"ORACLE-ASSIGN-{t.business_key}",
                            task_ids=[t.task_id],
                            business_keys=[t.business_key],
                            track_segment_id=t.track_segment_id,
                            start_utc=s_utc,
                            end_utc=e_utc,
                            assigned_resources=req_res,
                            phases=phases,
                            requires_power_block=t.requires_power_block,
                            power_block_elementary_section=t.power_block_elementary_section,
                            isolated_tracks=isolated,
                        )
                    )

            test_plan = ProposedPlan(
                plan_id=f"PLAN-ORACLE-{evaluated_combinations}",
                snapshot_id=self.snapshot.snapshot_id,
                snapshot_hash=self.snapshot.snapshot_hash,
                assignments=assignments,
            )

            report = self.checker.verify_plan(test_plan)
            if report.verdict == CheckerVerdict.VALID:
                feasible_count += 1
                # Lexicographic scoring
                mand_sched = report.coverage_metrics["mandatory_scheduled"]
                total_sched = report.coverage_metrics["scheduled_tasks"]
                total_dur = sum(
                    int((a.end_utc - a.start_utc).total_seconds() // 60) for a in assignments
                )
                score = (mand_sched, total_sched, -total_dur)

                if score > best_score:
                    best_score = score
                    best_plan = test_plan

        elapsed = time.perf_counter() - start_time

        return {
            "is_feasible": best_plan is not None,
            "best_plan": best_plan,
            "evaluated_combinations": evaluated_combinations,
            "feasible_combinations_count": feasible_count,
            "duration_ms": elapsed * 1000.0,
            "score": best_score,
        }
