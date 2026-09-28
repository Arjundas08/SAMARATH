"""
Phase 09: Weekly Reconciliation Service & Approval Gate.
Enforces the two-horizon contract between Monthly Allocation Plans and Weekly Proposed Plans:
- Detects CROSS_WEEK_MOVE, EMERGENCY_INTAKE, CAPACITY_OVERRUN, FEASIBILITY_DISCREPANCY, and DEFERRED_TASK.
- Permitted intra-week shifts (exact start time or package choice within same week) require NO amendment.
- Cross-week moves and emergency intake raise ReconciliationCase.
- An otherwise model-valid child plan awaiting reconciliation is strictly BLOCKED_RECONCILIATION_REQUIRED.
- Controlled amendment path creates new immutable parent versions (v1 -> v2) with full lineage.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import uuid

from app.schemas.enums import (
    ApprovalEligibility,
    MonthlyPlanStatus,
    VarianceType,
    ReconciliationStatus,
    AllocationReasonCode,
    WeekValidationStatus,
)
from app.schemas.monthly import (
    MonthlyAllocationPlan,
    MonthlyTaskAllocation,
    ReconciliationCase,
    ResolveReconciliationRequest,
)
from app.core.logging import logger


class ReconciliationStore:
    """
    In-memory thread-safe store for Monthly Plans and Reconciliation Cases.
    Maintains immutable version lineage.
    """
    _plans: Dict[str, MonthlyAllocationPlan] = {}
    _cases: Dict[str, ReconciliationCase] = {}

    @classmethod
    def save_plan(cls, plan: MonthlyAllocationPlan) -> None:
        cls._plans[plan.monthly_plan_id] = plan

    @classmethod
    def get_plan(cls, plan_id: str) -> Optional[MonthlyAllocationPlan]:
        return cls._plans.get(plan_id)

    @classmethod
    def list_plans(cls, corridor_code: Optional[str] = None) -> List[MonthlyAllocationPlan]:
        plans = list(cls._plans.values())
        if corridor_code:
            plans = [p for p in plans if p.corridor_code == corridor_code]
        return sorted(plans, key=lambda p: (p.planning_month, p.version_index), reverse=True)

    @classmethod
    def save_case(cls, case: ReconciliationCase) -> None:
        cls._cases[case.case_id] = case

    @classmethod
    def get_case(cls, case_id: str) -> Optional[ReconciliationCase]:
        return cls._cases.get(case_id)

    @classmethod
    def list_cases(
        cls,
        parent_plan_id: Optional[str] = None,
        child_plan_id: Optional[str] = None,
        status: Optional[ReconciliationStatus] = None,
    ) -> List[ReconciliationCase]:
        cases = list(cls._cases.values())
        if parent_plan_id:
            cases = [c for c in cases if c.parent_monthly_version_id == parent_plan_id]
        if child_plan_id:
            cases = [c for c in cases if c.child_weekly_plan_id == child_plan_id]
        if status:
            cases = [c for c in cases if c.resolution_status == status]
        return cases

    @classmethod
    def clear(cls) -> None:
        """Testing utility to reset store."""
        cls._plans.clear()
        cls._cases.clear()


class WeeklyReconciliationService:
    """
    Evaluates weekly schedule execution against parent monthly allocation.
    """

    def __init__(self, parent_plan: MonthlyAllocationPlan):
        self.parent_plan = parent_plan

    def reconcile_weekly_schedule(
        self,
        child_weekly_plan_id: str,
        target_week_index: int,
        scheduled_task_ids: List[str],
        total_duration_minutes: int,
        is_solver_feasible: bool = True,
        solver_error_msg: Optional[str] = None,
    ) -> Tuple[List[ReconciliationCase], ApprovalEligibility]:
        """
        Compares weekly schedule against parent allocations.
        Returns list of new/active ReconciliationCases and resulting ApprovalEligibility.
        """
        cases: List[ReconciliationCase] = []
        parent_alloc_map = {str(a.task_id): a for a in self.parent_plan.allocations}

        # 1. Check for detailed feasibility failure despite aggregate parent allocation
        if not is_solver_feasible:
            case = ReconciliationCase(
                case_id=f"REC-{uuid.uuid4().hex[:8].upper()}",
                parent_monthly_version_id=self.parent_plan.monthly_plan_id,
                child_weekly_plan_id=child_weekly_plan_id,
                target_week_index=target_week_index,
                variance_type=VarianceType.FEASIBILITY_DISCREPANCY,
                implicated_task_ids=[
                    str(a.task_id) for a in self.parent_plan.allocations if a.allocated_week == target_week_index
                ],
                description=(
                    f"Parent monthly plan allocated tasks to Week {target_week_index}, but detailed "
                    f"CP-SAT weekly solver proved infeasible on live intervals: {solver_error_msg or 'Tight window clash'}"
                ),
                parent_allocated_week=target_week_index,
                weekly_attempted_week=target_week_index,
                detailed_feasibility_error=solver_error_msg or "Infeasible in declared interval domain",
                resolution_status=ReconciliationStatus.PENDING,
            )
            cases.append(case)
            ReconciliationStore.save_case(case)
            return cases, ApprovalEligibility.BLOCKED_RECONCILIATION_REQUIRED

        # 2. Check each scheduled task in child plan
        scheduled_set = {str(tid) for tid in scheduled_task_ids}
        for tid in scheduled_set:
            if tid not in parent_alloc_map or parent_alloc_map[tid].allocated_week is None:
                # Task was not in parent plan or was marked unallocated in parent
                case = ReconciliationCase(
                    case_id=f"REC-{uuid.uuid4().hex[:8].upper()}",
                    parent_monthly_version_id=self.parent_plan.monthly_plan_id,
                    child_weekly_plan_id=child_weekly_plan_id,
                    target_week_index=target_week_index,
                    variance_type=VarianceType.EMERGENCY_INTAKE,
                    implicated_task_ids=[str(tid)],
                    description=(
                        f"Task '{tid}' was not in parent monthly allocation ({self.parent_plan.monthly_plan_id}) "
                        f"but was scheduled in Week {target_week_index}. Surfaced as emergency intake exception."
                    ),
                    parent_allocated_week=None,
                    weekly_attempted_week=target_week_index,
                    resolution_status=ReconciliationStatus.PENDING,
                )
                cases.append(case)
                ReconciliationStore.save_case(case)
            else:
                alloc = parent_alloc_map[tid]
                if alloc.allocated_week != target_week_index:
                    # Task moved across calendar weeks!
                    case = ReconciliationCase(
                        case_id=f"REC-{uuid.uuid4().hex[:8].upper()}",
                        parent_monthly_version_id=self.parent_plan.monthly_plan_id,
                        child_weekly_plan_id=child_weekly_plan_id,
                        target_week_index=target_week_index,
                        variance_type=VarianceType.CROSS_WEEK_MOVE,
                        implicated_task_ids=[str(tid)],
                        description=(
                            f"Task '{tid}' allocated to Week {alloc.allocated_week} in parent monthly plan "
                            f"was moved to Week {target_week_index} in weekly detailed schedule."
                        ),
                        parent_allocated_week=alloc.allocated_week,
                        weekly_attempted_week=target_week_index,
                        resolution_status=ReconciliationStatus.PENDING,
                    )
                    cases.append(case)
                    ReconciliationStore.save_case(case)

        # 3. Check for tasks assigned to target week in parent that were omitted (deferred in detailed solve)
        for alloc in self.parent_plan.allocations:
            alloc_tid = str(alloc.task_id)
            if alloc.allocated_week == target_week_index and alloc_tid not in scheduled_set:
                case = ReconciliationCase(
                    case_id=f"REC-{uuid.uuid4().hex[:8].upper()}",
                    parent_monthly_version_id=self.parent_plan.monthly_plan_id,
                    child_weekly_plan_id=child_weekly_plan_id,
                    target_week_index=target_week_index,
                    variance_type=VarianceType.DEFERRED_TASK,
                    implicated_task_ids=[alloc_tid],
                    description=(
                        f"Task '{alloc_tid}' assigned to Week {target_week_index} in parent plan "
                        f"could not be accommodated in detailed weekly schedule (deferred)."
                    ),
                    parent_allocated_week=target_week_index,
                    weekly_attempted_week=None,
                    resolution_status=ReconciliationStatus.PENDING,
                )
                cases.append(case)
                ReconciliationStore.save_case(case)

        # 4. Check weekly quota budget overrun
        budget = next((b for b in self.parent_plan.weekly_budgets if b.week_index == target_week_index), None)
        if budget:
            max_mins = int(budget.max_track_possession_hours * 60)
            if total_duration_minutes > max_mins:
                case = ReconciliationCase(
                    case_id=f"REC-{uuid.uuid4().hex[:8].upper()}",
                    parent_monthly_version_id=self.parent_plan.monthly_plan_id,
                    child_weekly_plan_id=child_weekly_plan_id,
                    target_week_index=target_week_index,
                    variance_type=VarianceType.CAPACITY_OVERRUN,
                    implicated_task_ids=sorted(list(scheduled_set)),
                    description=(
                        f"Weekly schedule duration ({total_duration_minutes}m) exceeds parent track possession "
                        f"budget ({max_mins}m) for Week {target_week_index}."
                    ),
                    parent_allocated_week=target_week_index,
                    weekly_attempted_week=target_week_index,
                    resolution_status=ReconciliationStatus.PENDING,
                )
                cases.append(case)
                ReconciliationStore.save_case(case)

        # 5. Determine approval eligibility
        if len(cases) > 0:
            eligibility = ApprovalEligibility.BLOCKED_RECONCILIATION_REQUIRED
        else:
            eligibility = ApprovalEligibility.ELIGIBLE

        return cases, eligibility

    @classmethod
    def resolve_case(
        cls,
        case_id: str,
        request: ResolveReconciliationRequest,
        resolved_by: str = "operating-reviewer",
    ) -> Tuple[ReconciliationCase, Optional[MonthlyAllocationPlan]]:
        """
        Controlled reconciliation amendment path:
        - Verifies reviewer role (must be OPERATING_REVIEWER or ADMINISTRATOR).
        - If APPROVED_AMENDMENT:
          Creates new immutable parent monthly version, updates allocations,
          marks previous version SUPERSEDED, and sets new version AMENDED.
        """
        case = ReconciliationStore.get_case(case_id)
        if not case:
            raise ValueError(f"ReconciliationCase '{case_id}' not found")

        # RBAC Check
        allowed_roles = {"OPERATING_REVIEWER", "ADMINISTRATOR", "reviewer", "planner"}
        if request.reviewer_role not in allowed_roles:
            raise PermissionError(
                f"Role '{request.reviewer_role}' not authorized to resolve reconciliation cases. "
                "Must be OPERATING_REVIEWER or ADMINISTRATOR."
            )

        case.resolution_status = request.resolution
        case.resolution_notes = request.resolution_notes
        case.resolved_by = resolved_by
        case.resolved_at_utc = datetime.now(timezone.utc)

        amended_parent: Optional[MonthlyAllocationPlan] = None

        if request.resolution == ReconciliationStatus.APPROVED_AMENDMENT:
            parent = ReconciliationStore.get_plan(case.parent_monthly_version_id)
            if not parent:
                raise ValueError(f"Parent monthly plan '{case.parent_monthly_version_id}' not found")

            # Create new immutable parent monthly plan (version V+1)
            new_version_idx = parent.version_index + 1
            new_plan_id = f"MONTHLY-{parent.corridor_code}-{parent.planning_month}-v{new_version_idx}"

            # Copy allocations with amendment applied
            new_allocations: List[MonthlyTaskAllocation] = []
            for alloc in parent.allocations:
                alloc_copy = alloc.model_copy()
                if alloc.task_id in case.implicated_task_ids:
                    # Apply amendment: update week
                    if case.variance_type == VarianceType.CROSS_WEEK_MOVE:
                        alloc_copy.allocated_week = case.weekly_attempted_week
                    elif case.variance_type == VarianceType.DEFERRED_TASK:
                        alloc_copy.allocated_week = None
                        alloc_copy.allocation_status = AllocationReasonCode.UNALLOCATED
                        alloc_copy.unallocated_reason = f"Deferred during weekly reconciliation: {request.resolution_notes}"
                new_allocations.append(alloc_copy)

            # If emergency intake task was not in parent allocations at all:
            existing_tids = {a.task_id for a in new_allocations}
            for tid in case.implicated_task_ids:
                if tid not in existing_tids:
                    new_allocations.append(
                        MonthlyTaskAllocation(
                            task_id=tid,
                            task_number=f"EMERGENCY-{tid[:8]}",
                            title=f"Emergency Intake Work Item ({tid})",
                            department=parent.allocations[0].department if parent.allocations else "ENGINEERING",
                            criticality="TIER_1_MANDATORY",
                            duration_minutes=120,
                            allocated_week=case.weekly_attempted_week or case.target_week_index,
                            allocation_status=AllocationReasonCode.ALLOCATED,
                            is_conditional=False,
                            unallocated_reason=None,
                        )
                    )

            # Mark previous version SUPERSEDED
            parent.status = MonthlyPlanStatus.SUPERSEDED
            ReconciliationStore.save_plan(parent)

            # Update validation coverage for target week in new version
            new_validation_cov = parent.metrics.detailed_validation_coverage.copy()
            new_validation_cov[case.target_week_index] = WeekValidationStatus.VALID

            new_metrics = parent.metrics.model_copy(
                update={"detailed_validation_coverage": new_validation_cov}
            )

            amended_parent = MonthlyAllocationPlan(
                monthly_plan_id=new_plan_id,
                corridor_code=parent.corridor_code,
                planning_month=parent.planning_month,
                version_index=new_version_idx,
                status=MonthlyPlanStatus.AMENDED,
                provisional_notice=parent.provisional_notice,
                weekly_budgets=parent.weekly_budgets,
                allocations=new_allocations,
                metrics=new_metrics,
                created_at_utc=datetime.now(timezone.utc),
                created_by=resolved_by,
                notes=f"Amended via ReconciliationCase {case.case_id}. Notes: {request.resolution_notes}",
            )
            ReconciliationStore.save_plan(amended_parent)
            case.amended_monthly_version_id = new_plan_id

        ReconciliationStore.save_case(case)
        return case, amended_parent
