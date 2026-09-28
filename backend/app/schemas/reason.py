"""
Reason and Explainability schemas for Why and Why-Not diagnostics per Blueprint Sections 24-25.
"""
from typing import List, Optional, Any, Dict
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.enums import (
    DiagnosticReasonCode,
    ProofStatus,
    RepairActionType,
    RepairFeasibilityStatus,
)


class DiagnosticEvidenceFact(APIModel):
    """
    Deterministic factual evidence backing a why or why-not conclusion.
    """
    fact_key: str
    fact_label: str
    required_value: Any
    observed_value: Any
    units: Optional[str] = None
    source_record_id: Optional[str] = None
    rule_version: str = "v1.0"
    is_satisfied: bool


class ConflictCore(APIModel):
    """
    Sufficient conflict core identifying why a candidate or task could not be placed.
    """
    conflicting_tasks: List[str] = Field(default_factory=list)
    conflicting_trains: List[str] = Field(default_factory=list)
    exhausted_resources: List[str] = Field(default_factory=list)
    violated_rules: List[str] = Field(default_factory=list)


class CounterfactualComparison(APIModel):
    """
    Controlled comparative proof explaining why an alternative candidate was rejected or suboptimal.
    """
    alternate_candidate_id: str
    alternate_window_start: int
    alternate_window_end: int
    comparison_outcome: str  # "OBJECTIVE_SUBOPTIMAL", "CONFLICTING_TRAIN", "OVERLAPPING_LOCKED_POSSESSION"
    losing_objective_tier: Optional[str] = None  # e.g., "Tier 1: High Criticality", "Tier 2: Train Delay"
    penalty_delta: Optional[float] = None
    details: str


class RepairOption(APIModel):
    """
    Bounded, policy-permitted repair option.
    Never relaxes safety, protection, or mandatory operational commitments.
    """
    repair_id: str = Field(default_factory=lambda: f"REP-{uuid4().hex[:8].upper()}")
    action_type: RepairActionType
    description: str
    required_role: str  # e.g., "OPERATING_REVIEWER", "CHIEF_CONTROLLER", "SR_DEN"
    affected_records: List[str] = Field(default_factory=list)
    feasibility_status: RepairFeasibilityStatus = RepairFeasibilityStatus.VERIFIED_FEASIBLE
    objective_delta: Optional[float] = None
    target_parameter: Optional[str] = None
    proposed_value: Optional[str] = None
    is_trial_tested: bool = False
    trial_checker_passed: Optional[bool] = None


class WhyNotDiagnostic(APIModel):
    """
    Complete explanation for why a task was not scheduled in the plan.
    """
    task_id: str
    task_business_key: str
    plan_id: str
    snapshot_id: str
    reason_code: DiagnosticReasonCode
    proof_status: ProofStatus
    primary_cause_summary: str
    explanation_narrative: str
    facts: List[DiagnosticEvidenceFact] = Field(default_factory=list)
    conflict_core: ConflictCore = Field(default_factory=ConflictCore)
    permitted_repairs: List[RepairOption] = Field(default_factory=list)
    solver_time_budget_seconds: Optional[float] = None
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)


class WhySelectedDiagnostic(APIModel):
    """
    Admissibility and optimality explanation for a scheduled assignment.
    """
    assignment_id: str
    task_id: str
    plan_id: str
    admissibility_facts: List[DiagnosticEvidenceFact] = Field(default_factory=list)
    objective_contributions: Dict[str, float] = Field(default_factory=dict)
    primary_selection_rationale: str
    counterfactual_comparisons: List[CounterfactualComparison] = Field(default_factory=list)
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)


class TrialRepairRequest(APIModel):
    """
    Request to execute a non-publishable trial repair simulation.
    """
    plan_id: str
    task_id: str
    repair_id: str
    action_type: RepairActionType
    proposed_value: Optional[str] = None


class TrialRepairResult(APIModel):
    """
    Outcome of a non-publishable trial repair solve and independent checker run.
    """
    trial_id: str = Field(default_factory=lambda: f"TRL-{uuid4().hex[:8].upper()}")
    repair_id: str
    is_publishable: bool = False  # Strictly non-publishable
    checker_verdict: str  # "PASSED" or "FAILED"
    objective_before: float
    objective_after: float
    objective_improvement: float
    placed_task_ids: List[str] = Field(default_factory=list)
    remaining_conflicts: List[str] = Field(default_factory=list)
    runtime_ms: float
    simulated_assignments_count: int


class ApplyRepairRequest(APIModel):
    """
    Precondition-checked request to accept a repair and apply authorized input revisions.
    """
    plan_id: str
    task_id: str
    repair_id: str
    expected_plan_version: int
    authorized_by_role: str
    justification: str


class ApplyRepairResponse(APIModel):
    """
    Response acknowledging applied repair and scheduling a fresh normal solve job.
    """
    applied_repair_id: str
    new_snapshot_id: str
    new_job_id: str
    status: str
    message: str


# Legacy compatibility aliases
SuggestedRepair = RepairOption
Reason = WhyNotDiagnostic
