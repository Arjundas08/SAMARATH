"""
Schemas for CP-SAT Weekly Optimizer and Lexicographic Profiles.
Implements Blueprint Sections 17, 18, 19, 22, 23, 27, 42.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.common import APIModel, utc_now
from app.schemas.enums import ObjectiveProfile, SolverStatus, StopReason, ApprovalEligibility
from app.schemas.checker import ProposedPlan, CheckerAssignment, CheckerReport, CheckerVerdict
from app.schemas.monthly import ReconciliationCase


class OptimizerStageMetric(APIModel):
    stage_index: int
    stage_name: str
    objective_unit: str
    best_objective_value: Optional[int] = None
    best_bound: Optional[int] = None
    status: str
    duration_ms: float


class OptimizerSolveRequest(APIModel):
    corridor_code: str = "VKC"
    profile: ObjectiveProfile = ObjectiveProfile.PROGRAMME_IMPROVEMENT
    time_limit_seconds: float = 15.0
    num_workers: int = 1  # Deterministic single-worker default
    random_seed: int = 42
    lattice_step_minutes: int = 30
    max_candidates: int = 10000
    original_plan: Optional[ProposedPlan] = None  # Required for DISRUPTION_RECOVERY
    parent_monthly_plan_id: Optional[str] = None  # Two-horizon parent monthly version
    target_week_index: Optional[int] = 1


class OptimizerSolveResult(APIModel):
    solver_status: SolverStatus
    stop_reason: StopReason
    is_feasible: bool
    profile: ObjectiveProfile
    total_tasks_count: int
    scheduled_tasks_count: int
    mandatory_total_count: int
    mandatory_scheduled_count: int
    bundled_packages_count: int
    total_block_minutes: int
    solve_duration_ms: float
    stage_metrics: List[OptimizerStageMetric] = Field(default_factory=list)
    assignments: List[CheckerAssignment] = Field(default_factory=list)
    checker_verdict: Optional[CheckerVerdict] = None
    checker_report: Optional[CheckerReport] = None
    is_truncated: bool = False
    parent_monthly_plan_id: Optional[str] = None
    target_week_index: Optional[int] = None
    reconciliation_cases: List[ReconciliationCase] = Field(default_factory=list)
    approval_eligibility: ApprovalEligibility = ApprovalEligibility.ELIGIBLE
    metadata: Dict[str, Any] = Field(default_factory=dict)
