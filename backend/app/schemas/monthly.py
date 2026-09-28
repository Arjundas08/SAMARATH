"""
Pydantic Schemas for Phase 09:
Monthly Allocation, Weekly Reconciliation, and Two-Horizon Contract.
Strictly typed; no unvalidated coercion.
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.enums import (
    DepartmentType,
    CriticalityTier,
    MonthlyPlanStatus,
    VarianceType,
    ReconciliationStatus,
    AllocationReasonCode,
    WeekValidationStatus,
)


class WeeklyQuotaBudget(BaseModel):
    week_index: int = Field(..., ge=1, le=5, description="Calendar week index within the planning month (1..4 or 5)")
    start_utc: datetime = Field(..., description="Inclusive UTC start timestamp of the calendar week")
    end_utc: datetime = Field(..., description="Exclusive UTC end timestamp of the calendar week")
    label: str = Field(..., description="Human-readable label, e.g. 'Week 1: Oct 01 - Oct 07'")
    max_track_possession_hours: float = Field(35.0, ge=0.0, description="Upper bound on total track possession hours")
    max_machine_hours: Dict[str, float] = Field(
        default_factory=dict,
        description="Upper bound on operating hours per specialized track machine (e.g. BCM-01: 20.0)",
    )
    max_crew_hours: Dict[str, float] = Field(
        default_factory=dict,
        description="Upper bound on shift hours per departmental crew",
    )


class MonthlyTaskAllocation(BaseModel):
    task_id: str = Field(..., description="Canonical task identifier")
    task_number: str = Field(..., description="Reference task number (e.g. ENG-W1-01)")
    title: str = Field(..., description="Work item title")
    department: DepartmentType
    criticality: CriticalityTier
    duration_minutes: int = Field(..., gt=0)
    allocated_week: Optional[int] = Field(None, ge=1, le=5, description="Assigned week index, or None if deferred/unallocated")
    allocation_status: AllocationReasonCode = Field(default=AllocationReasonCode.ALLOCATED)
    is_conditional: bool = Field(False, description="True if task has conditional readiness prerequisites")
    prerequisite_condition: Optional[str] = Field(None, description="Condition description (e.g. 'Steel girder delivery')")
    prerequisite_owner: Optional[str] = Field(None, description="Named department owner of prerequisite")
    ready_by_date: Optional[datetime] = Field(None, description="Hard readiness deadline")
    required_resources: List[str] = Field(default_factory=list)
    unallocated_reason: Optional[str] = Field(None, description="Explanation if task was not allocated")


class MonthlyAllocationMetrics(BaseModel):
    total_tasks: int
    mandatory_total: int
    mandatory_allocated: int
    mandatory_coverage_pct: float
    due_week_coverage_pct: float
    conditional_tasks_count: int
    deferred_tasks_count: int
    resource_pressure_by_week: Dict[int, Dict[str, float]] = Field(
        default_factory=dict,
        description="week_index -> {resource_id or 'track_possession': percent_of_budget_consumed}",
    )
    detailed_validation_coverage: Dict[int, WeekValidationStatus] = Field(
        default_factory=dict,
        description="week_index -> WeekValidationStatus indicating detailed checking state",
    )


class MonthlyAllocationPlan(BaseModel):
    monthly_plan_id: str = Field(..., description="Immutable identifier, e.g. 'MONTHLY-VKC-2026-10-v1'")
    corridor_code: str
    planning_month: str = Field(..., description="YYYY-MM format, e.g. '2026-10'")
    version_index: int = Field(1, ge=1, description="Sequential version counter for immutable lineage")
    status: MonthlyPlanStatus = Field(default=MonthlyPlanStatus.ALLOCATED_PROVISIONAL)
    provisional_notice: str = Field(
        default="ALLOCATED_PROVISIONAL: Aggregate budget feasibility is a necessary coarse condition and does not guarantee minute-level feasibility or operational conflict freedom.",
        description="Mandatory system disclosure on provisional nature of monthly allocation",
    )
    weekly_budgets: List[WeeklyQuotaBudget]
    allocations: List[MonthlyTaskAllocation]
    metrics: MonthlyAllocationMetrics
    created_at_utc: datetime
    created_by: str = "system-planner"
    notes: Optional[str] = None


class ReconciliationCase(BaseModel):
    case_id: str = Field(..., description="Unique reconciliation case identifier, e.g. 'REC-CASE-2026-10-W1-01'")
    parent_monthly_version_id: str = Field(..., description="Pinned parent monthly allocation plan ID")
    child_weekly_plan_id: str = Field(..., description="Child weekly proposed plan ID")
    target_week_index: int = Field(..., ge=1, le=5)
    variance_type: VarianceType
    implicated_task_ids: List[str]
    description: str
    parent_allocated_week: Optional[int] = None
    weekly_attempted_week: Optional[int] = None
    detailed_feasibility_error: Optional[str] = None
    resolution_status: ReconciliationStatus = Field(default=ReconciliationStatus.PENDING)
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at_utc: Optional[datetime] = None
    amended_monthly_version_id: Optional[str] = None


class MonthlyAllocationRequest(BaseModel):
    corridor_code: str = "VKC"
    planning_month: str = "2026-10"
    weekly_budgets: Optional[List[WeeklyQuotaBudget]] = None
    allow_carry_in: bool = True
    time_limit_seconds: float = 10.0


class ResolveReconciliationRequest(BaseModel):
    resolution: ReconciliationStatus
    reviewer_role: str = "OPERATING_REVIEWER"
    resolution_notes: str
    target_week_override: Optional[int] = None
