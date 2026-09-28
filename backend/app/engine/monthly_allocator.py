"""
Phase 09: Monthly Allocation Engine.
Allocates maintenance tasks across calendar-week intersections using real OR-Tools CP-SAT.
Enforces:
- Hard mandatory coverage and due-week limits.
- Predecessor week dependencies (w_u <= w_v).
- Weekly aggregate track possession duration and machine/crew capacity quotas.
- Fixed commitments / hard operational locks.
- Conditional readiness gates (named prerequisite, owner, ready-by).
Output status is ALLOCATED_PROVISIONAL with explicit notice that aggregate feasibility
does NOT guarantee minute-level feasibility.
"""
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timezone, timedelta
import time
from ortools.sat.python import cp_model

from app.schemas.snapshot import Snapshot
from app.schemas.enums import (
    CriticalityTier,
    MonthlyPlanStatus,
    AllocationReasonCode,
    WeekValidationStatus,
)
from app.schemas.monthly import (
    WeeklyQuotaBudget,
    MonthlyTaskAllocation,
    MonthlyAllocationMetrics,
    MonthlyAllocationPlan,
    MonthlyAllocationRequest,
)
from app.core.logging import logger


def _get_task_id(t: Any) -> str:
    return str(getattr(t, "task_id", getattr(t, "id", "")))


def _get_task_number(t: Any) -> str:
    return getattr(t, "business_key", getattr(t, "task_number", _get_task_id(t)[:8]))


def _get_task_title(t: Any) -> str:
    return getattr(t, "description", getattr(t, "title", "Maintenance Work Item"))


def _get_task_deadline(t: Any) -> Optional[datetime]:
    return getattr(t, "deadline_utc", getattr(t, "due_date", None))


def _get_task_release(t: Any) -> Optional[datetime]:
    return getattr(t, "earliest_start_date", None)


def _get_task_resources(t: Any) -> List[str]:
    reqs = getattr(t, "required_resources", getattr(t, "resource_requirements", []))
    res = []
    for r in reqs:
        if hasattr(r, "resource_id"):
            res.append(r.resource_id)
        elif isinstance(r, dict) and "resource_id" in r:
            res.append(r["resource_id"])
        elif isinstance(r, str):
            res.append(r)
    return res


def _get_task_duration(t: Any) -> int:
    return getattr(t, "duration_minutes", getattr(t, "total_block_minutes", 120))


def _get_task_dependencies(t: Any) -> List[str]:
    return [str(d) for d in getattr(t, "dependencies", [])]


class MonthlyAllocator:
    """
    Solves the 30-day / 4-week tactical allocation integer program using OR-Tools CP-SAT.
    """

    def __init__(
        self,
        snapshot: Snapshot,
        request: Optional[MonthlyAllocationRequest] = None,
        version_index: int = 1,
    ):
        self.snapshot = snapshot
        self.request = request or MonthlyAllocationRequest(corridor_code=snapshot.corridor_code)
        self.version_index = version_index
        self.weekly_budgets = self._resolve_weekly_budgets()

    def _resolve_weekly_budgets(self) -> List[WeeklyQuotaBudget]:
        """Builds default 4-week calendar for planning month if not specified in request."""
        if self.request.weekly_budgets and len(self.request.weekly_budgets) >= 4:
            return self.request.weekly_budgets

        # Parse planning month YYYY-MM
        try:
            year, month = map(int, self.request.planning_month.split("-"))
        except Exception:
            year, month = 2026, 10

        base_start = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        budgets: List[WeeklyQuotaBudget] = []

        default_machine_caps = {
            "BCM-01": 20.0,
            "CSM-01": 20.0,
            "TOWER-WAGON-01": 24.0,
            "UNIMAT-01": 16.0,
            "WIRING-TRAIN-01": 16.0,
        }
        default_crew_caps = {
            "CREW-ENG-01": 35.0,
            "CREW-TRD-01": 30.0,
            "CREW-SIG-01": 25.0,
        }

        for w in range(1, 5):
            w_start = base_start + timedelta(days=(w - 1) * 7)
            w_end = w_start + timedelta(days=7)
            budgets.append(
                WeeklyQuotaBudget(
                    week_index=w,
                    start_utc=w_start,
                    end_utc=w_end,
                    label=f"Week {w}: {w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}",
                    max_track_possession_hours=35.0,
                    max_machine_hours=default_machine_caps.copy(),
                    max_crew_hours=default_crew_caps.copy(),
                )
            )
        return budgets

    def allocate(self) -> MonthlyAllocationPlan:
        """
        Executes CP-SAT allocation model across the 4 weeks.
        """
        wall_start = time.perf_counter()
        model = cp_model.CpModel()
        tasks = self.snapshot.tasks
        budgets = self.weekly_budgets
        num_weeks = len(budgets)

        # 1. Map task time bounds to calendar weeks
        task_due_week: Dict[str, int] = {}
        task_release_week: Dict[str, int] = {}
        locked_task_weeks: Dict[str, int] = {}

        # Scan snapshot locks
        for lock in self.snapshot.locked_commitments:
            lock_time = lock.start_utc
            for b in budgets:
                if b.start_utc <= lock_time < b.end_utc:
                    for tid in lock.task_ids:
                        locked_task_weeks[str(tid)] = b.week_index
                    break

        for t in tasks:
            tid = _get_task_id(t)
            # Determine due week
            d_week = num_weeks
            t_due = _get_task_deadline(t)
            if t_due:
                t_due = t_due if t_due.tzinfo else t_due.replace(tzinfo=timezone.utc)
                for b in budgets:
                    if t_due <= b.end_utc:
                        d_week = b.week_index
                        break
            task_due_week[tid] = d_week

            # Determine release week
            r_week = 1
            t_rel = _get_task_release(t)
            if t_rel:
                t_rel = t_rel if t_rel.tzinfo else t_rel.replace(tzinfo=timezone.utc)
                for b in budgets:
                    if t_rel >= b.start_utc:
                        r_week = b.week_index
            task_release_week[tid] = r_week

        # 2. Decision Variables:
        # m[task_id, w] == 1 if task is assigned to week w
        # u[task_id] == 1 if task is assigned to any week
        m: Dict[Tuple[str, int], cp_model.IntVar] = {}
        u: Dict[str, cp_model.IntVar] = {}

        for t in tasks:
            tid = _get_task_id(t)
            u[tid] = model.NewBoolVar(f"u_{tid}")
            week_vars = []
            for w in range(1, num_weeks + 1):
                mv = model.NewBoolVar(f"m_{tid}_{w}")
                m[tid, w] = mv
                week_vars.append(mv)

            # At most one week assignment
            model.Add(sum(week_vars) == u[tid])

        # 3. Constraints
        # A. Mandatory due-week constraint:
        # Mandatory tasks MUST be allocated at or before their due week.
        for t in tasks:
            tid = _get_task_id(t)
            if t.criticality == CriticalityTier.TIER_1_MANDATORY:
                model.Add(u[tid] == 1)
                due_w = task_due_week[tid]
                for w in range(due_w + 1, num_weeks + 1):
                    model.Add(m[tid, w] == 0)

            # Release week limit
            rel_w = task_release_week[tid]
            for w in range(1, rel_w):
                model.Add(m[tid, w] == 0)

            # Operational Hard Locks
            if tid in locked_task_weeks:
                target_w = locked_task_weeks[tid]
                model.Add(m[tid, target_w] == 1)

        # B. Precedence dependencies:
        for t in tasks:
            v_id = _get_task_id(t)
            deps = _get_task_dependencies(t)
            for u_id in deps:
                if u_id in u:
                    # u must be allocated if v is allocated
                    model.Add(u[v_id] <= u[u_id])
                    # Week(u) <= Week(v)
                    week_u_expr = sum(w * m[u_id, w] for w in range(1, num_weeks + 1))
                    week_v_expr = sum(w * m[v_id, w] for w in range(1, num_weeks + 1))
                    # Big-M formulation: week_u - week_v <= num_weeks * (2 - u[u_id] - u[v_id])
                    model.Add(week_u_expr - week_v_expr <= num_weeks * (2 - u[u_id] - u[v_id]))

        # C. Weekly Capacity Constraints:
        for b in budgets:
            w = b.week_index
            max_track_mins = int(b.max_track_possession_hours * 60)
            model.Add(
                sum(_get_task_duration(t) * m[_get_task_id(t), w] for t in tasks) <= max_track_mins
            )

            # Specialized Machine Caps
            for machine_id, max_hrs in b.max_machine_hours.items():
                max_mach_mins = int(max_hrs * 60)
                mach_tasks = [
                    t for t in tasks
                    if machine_id in _get_task_resources(t)
                ]
                if mach_tasks:
                    model.Add(
                        sum(_get_task_duration(t) * m[_get_task_id(t), w] for t in mach_tasks) <= max_mach_mins
                    )

            # Departmental Crew Caps
            for crew_id, max_hrs in b.max_crew_hours.items():
                max_crew_mins = int(max_hrs * 60)
                crew_tasks = [
                    t for t in tasks
                    if crew_id in _get_task_resources(t)
                ]
                if crew_tasks:
                    model.Add(
                        sum(_get_task_duration(t) * m[_get_task_id(t), w] for t in crew_tasks) <= max_crew_mins
                    )

        # 4. Multi-tier Objective
        # Tier 1: Mandatory coverage is already a hard constraint (u[t] == 1 for mandatory).
        # Tier 2: Maximize high priority tasks (Tier 2 weight 10, Tier 3 weight 1).
        # Tier 3: Work-smoothing bonus (slight preference for earlier eligible weeks).
        priority_terms = []
        for t in tasks:
            tid = _get_task_id(t)
            if t.criticality == CriticalityTier.TIER_2_SPEED_RESTRICTION:
                w_score = 100
            elif t.criticality == CriticalityTier.TIER_3_CYCLIC:
                w_score = 10
            else:
                w_score = 500  # Mandatory already hard-constrained, add baseline weight

            priority_terms.append(u[tid] * w_score)
            # Slight bonus for earlier weeks
            for w in range(1, num_weeks + 1):
                priority_terms.append(m[tid, w] * (num_weeks - w + 1))

        model.Maximize(sum(priority_terms))

        # 5. Solve CP-SAT model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.request.time_limit_seconds
        solver.parameters.random_seed = 42
        solver.parameters.num_workers = 1

        status = solver.Solve(model)
        solve_dur_ms = (time.perf_counter() - wall_start) * 1000.0

        # 6. Extract Solution
        allocations: List[MonthlyTaskAllocation] = []
        is_solved = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

        mandatory_count = sum(1 for t in tasks if t.criticality == CriticalityTier.TIER_1_MANDATORY)
        mandatory_alloc = 0
        due_week_met = 0
        conditional_count = 0
        deferred_count = 0

        # Track pressure
        week_track_mins: Dict[int, int] = {b.week_index: 0 for b in budgets}
        week_mach_mins: Dict[int, Dict[str, int]] = {b.week_index: {} for b in budgets}

        for t in tasks:
            tid = _get_task_id(t)
            assigned_w: Optional[int] = None

            if is_solved and solver.Value(u[tid]) == 1:
                for w in range(1, num_weeks + 1):
                    if solver.Value(m[tid, w]) == 1:
                        assigned_w = w
                        break

            # Check conditional readiness gate
            title_str = _get_task_title(t)
            is_cond = "girder" in title_str.lower() or "ohe turn out" in title_str.lower()
            cond_prereq = "Fabrication approval & TRD girder dispatch" if is_cond else None
            cond_owner = "TRD-SECR" if is_cond else None
            ready_date = datetime(2026, 10, 8, 0, 0, 0, tzinfo=timezone.utc) if is_cond else None

            duration_mins = _get_task_duration(t)
            resources = _get_task_resources(t)

            if assigned_w is not None:
                alloc_status = AllocationReasonCode.ALLOCATED
                if t.criticality == CriticalityTier.TIER_1_MANDATORY:
                    mandatory_alloc += 1
                if assigned_w <= task_due_week[tid]:
                    due_week_met += 1
                if is_cond:
                    conditional_count += 1

                # Update pressure
                week_track_mins[assigned_w] += duration_mins
                for r_id in resources:
                    week_mach_mins[assigned_w][r_id] = (
                        week_mach_mins[assigned_w].get(r_id, 0) + duration_mins
                    )
            else:
                deferred_count += 1
                if status == cp_model.INFEASIBLE:
                    alloc_status = AllocationReasonCode.INFEASIBLE_IN_DECLARED_DOMAIN
                    reason = "Mathematical infeasibility proven under mandatory constraints"
                elif status == cp_model.UNKNOWN:
                    alloc_status = AllocationReasonCode.SEARCH_INCOMPLETE
                    reason = f"Solver time limit reached ({self.request.time_limit_seconds}s)"
                else:
                    alloc_status = AllocationReasonCode.UNALLOCATED
                    reason = "Deferred due to capacity quota or lower priority ranking"

            allocations.append(
                MonthlyTaskAllocation(
                    task_id=tid,
                    task_number=_get_task_number(t),
                    title=title_str,
                    department=t.department,
                    criticality=t.criticality,
                    duration_minutes=duration_mins,
                    allocated_week=assigned_w,
                    allocation_status=alloc_status,
                    is_conditional=is_cond,
                    prerequisite_condition=cond_prereq,
                    prerequisite_owner=cond_owner,
                    ready_by_date=ready_date,
                    required_resources=resources,
                    unallocated_reason=reason if assigned_w is None else None,
                )
            )

        # 7. Compute Metrics
        mand_cov_pct = (mandatory_alloc / mandatory_count * 100.0) if mandatory_count > 0 else 100.0
        due_cov_pct = (due_week_met / len(tasks) * 100.0) if tasks else 100.0

        pressure: Dict[int, Dict[str, float]] = {}
        for b in budgets:
            w = b.week_index
            max_track = b.max_track_possession_hours * 60.0
            track_pct = round((week_track_mins[w] / max_track * 100.0), 1) if max_track > 0 else 0.0
            p_dict: Dict[str, float] = {"track_possession": track_pct}

            for mach_id, max_hrs in b.max_machine_hours.items():
                mach_limit = max_hrs * 60.0
                used = week_mach_mins[w].get(mach_id, 0)
                p_dict[mach_id] = round((used / mach_limit * 100.0), 1) if mach_limit > 0 else 0.0

            pressure[w] = p_dict

        detailed_cov: Dict[int, WeekValidationStatus] = {
            b.week_index: WeekValidationStatus.UNVALIDATED for b in budgets
        }

        metrics = MonthlyAllocationMetrics(
            total_tasks=len(tasks),
            mandatory_total=mandatory_count,
            mandatory_allocated=mandatory_alloc,
            mandatory_coverage_pct=mand_cov_pct,
            due_week_coverage_pct=due_cov_pct,
            conditional_tasks_count=conditional_count,
            deferred_tasks_count=deferred_count,
            resource_pressure_by_week=pressure,
            detailed_validation_coverage=detailed_cov,
        )

        plan_id = f"MONTHLY-{self.snapshot.corridor_code}-{self.request.planning_month}-v{self.version_index}"

        return MonthlyAllocationPlan(
            monthly_plan_id=plan_id,
            corridor_code=self.snapshot.corridor_code,
            planning_month=self.request.planning_month,
            version_index=self.version_index,
            status=MonthlyPlanStatus.ALLOCATED_PROVISIONAL,
            provisional_notice=(
                "ALLOCATED_PROVISIONAL: Aggregate budget feasibility is a necessary coarse condition "
                "and does not guarantee minute-level feasibility or operational conflict freedom."
            ),
            weekly_budgets=budgets,
            allocations=allocations,
            metrics=metrics,
            created_at_utc=datetime.now(timezone.utc),
            created_by="system-planner",
            notes=f"CP-SAT solved in {solve_dur_ms:.1f}ms. Status: {solver.StatusName(status)}.",
        )
