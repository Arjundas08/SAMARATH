"""
Phase 14: Calculated Metrics, Fair Comparison & Stress Scenarios Schemas.
Blueprint Sections: 26, 37-40.

Provides schemas for:
- Versioned, mathematically defensible plan metric calculation.
- Interval union infrastructure occupation (no double-counting).
- Zero-denominator resilience ('N/A' / None).
- Fair comparison with aligned denominators and unequal-coverage warnings.
- Fixed-plan stress testing with 4 versioned perturbations.
- Separate adaptive recovery re-solving benchmarks.
- Pinned provenance (snapshot, plan, rule/policy, calculator, domain).
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


CALCULATOR_VERSION = "1.4.0"


class StressScenarioType(str, Enum):
    WORK_DURATION_INCREASE = "WORK_DURATION_INCREASE"
    LATE_RESOURCE_ARRIVAL = "LATE_RESOURCE_ARRIVAL"
    SHIFTED_GOODS_FORECAST = "SHIFTED_GOODS_FORECAST"
    URGENT_UNPLANNED_WORK = "URGENT_UNPLANNED_WORK"


class UnscheduledReasonCategory(str, Enum):
    CURFEW_EXCEEDED = "CURFEW_EXCEEDED"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"
    TRACK_WINDOW_INSUFFICIENT = "TRACK_WINDOW_INSUFFICIENT"
    TRAIN_CONFLICT = "TRAIN_CONFLICT"
    SAFETY_BUFFER_VIOLATION = "SAFETY_BUFFER_VIOLATION"
    DEADLINE_EXPIRED = "DEADLINE_EXPIRED"
    DEPENDENCY_UNMET = "DEPENDENCY_UNMET"
    OTHER = "OTHER"


class OnTimeCoverageMetrics(BaseModel):
    """
    On-time coverage metrics distinguishing mandatory, critical, and routine tasks.
    """
    total_tasks_in_scope: int = Field(..., description="Total task candidates in snapshot")
    total_tasks_scheduled: int = Field(..., description="Tasks assigned a valid window")
    total_tasks_unscheduled: int = Field(..., description="Tasks omitted or unscheduled")
    overall_coverage_pct: Optional[float] = Field(None, description="% of tasks scheduled (None if 0 tasks)")

    # Mandatory tasks (strictly non-negotiable safety/regulatory)
    mandatory_tasks_total: int = Field(..., description="Total mandatory tasks in scope")
    mandatory_tasks_scheduled: int = Field(..., description="Mandatory tasks successfully scheduled")
    mandatory_on_time_coverage_pct: Optional[float] = Field(None, description="% mandatory scheduled on-time")

    # Critical tasks (high operational priority)
    critical_tasks_total: int = Field(..., description="Total critical tasks in scope")
    critical_tasks_scheduled: int = Field(..., description="Critical tasks successfully scheduled")
    critical_on_time_coverage_pct: Optional[float] = Field(None, description="% critical scheduled on-time")

    # Routine tasks
    routine_tasks_total: int = Field(0)
    routine_tasks_scheduled: int = Field(0)

    # Lateness metrics
    permitted_lateness_count: int = Field(0, description="Tasks scheduled past soft target but within permitted lateness")
    permitted_lateness_total_minutes: int = Field(0, description="Cumulative permitted lateness minutes")
    unpermitted_lateness_count: int = Field(0, description="Tasks scheduled after strict deadline (violations)")

    # Breakdown of unscheduled reasons
    unscheduled_by_reason: Dict[str, int] = Field(default_factory=dict, description="Counts per UnscheduledReasonCategory")


class SegmentUnionOccupation(BaseModel):
    """
    Occupation of a single track segment calculated as the interval union
    of all overlapping maintenance activities, NOT the sum of durations.
    """
    segment_id: str
    segment_code: str
    corridor_code: str
    total_horizon_minutes: int = Field(..., description="Total planning horizon minutes for this segment")
    fixed_closure_minutes: int = Field(0, description="Commercial train / curfew closures (shown separately)")
    maintenance_union_minutes: int = Field(..., description="Union duration of maintenance occupations")
    maintenance_sum_minutes: int = Field(..., description="Raw sum of task durations (for comparison/audit)")
    overlap_savings_minutes: int = Field(..., description="Sum minus Union: minutes saved via co-utilization")
    net_available_minutes: int = Field(..., description="Horizon minus (fixed + maintenance union)")
    utilization_pct: Optional[float] = Field(None, description="Maintenance union as % of horizon (None if 0)")


class InfrastructureOccupationMetrics(BaseModel):
    """
    Network-wide infrastructure occupation calculated via interval unions.
    """
    total_corridor_horizon_minutes: int = Field(..., description="Sum of segment horizons across scope")
    total_fixed_closures_minutes: int = Field(0, description="Commercial traffic / locked curfews")
    total_maintenance_union_minutes: int = Field(..., description="Union of maintenance occupations across all segments")
    total_maintenance_sum_minutes: int = Field(..., description="Sum of individual task durations across all segments")
    total_co_utilization_savings_minutes: int = Field(..., description="Sum minus Union across network")
    network_utilization_pct: Optional[float] = Field(None, description="Total union as % of network capacity")
    segments: List[SegmentUnionOccupation] = Field(default_factory=list)


class QualityAndTimingMetrics(BaseModel):
    """
    Plan quality, lock preservation, and solver timing metrics.
    """
    lock_preservation_pct: Optional[float] = Field(None, description="% of hard locks strictly preserved")
    hard_locks_total: int = Field(0)
    hard_locks_preserved: int = Field(0)
    hard_locks_violated: int = Field(0)
    explanation_coverage_pct: Optional[float] = Field(None, description="% of decisions with formal auditable rationale")

    # Timings
    run_time_ms: float = Field(0.0, description="Total end-to-end execution time in milliseconds")
    model_generation_ms: float = Field(0.0, description="CP-SAT / Lattice generation time")
    solve_time_ms: float = Field(0.0, description="Core solver branch-and-bound / SAT time")
    checker_time_ms: float = Field(0.0, description="Independent verification and invariant check time")

    # Domain size
    variables_count: int = Field(0, description="Number of decision variables in solver model")
    constraints_count: int = Field(0, description="Number of constraints in solver model")
    lattice_nodes_count: int = Field(0, description="Total candidate lattice nodes evaluated")


class CalculatedPlanMetrics(BaseModel):
    """
    Root pinned metrics report for a specific plan version.
    No release KPI may be stored as an editable demo constant.
    """
    metric_report_id: str
    plan_id: str
    plan_version: int
    corridor_code: str
    snapshot_id: str

    # Pinned Provenance
    calculator_version: str = CALCULATOR_VERSION
    rule_policy_version: str
    domain_version: str
    calculated_at: str
    hardware_tag: str = Field(
        ...,
        description="Hardware execution environment (e.g. 'AMD Ryzen 7 / Intel Xeon' or 'Untested target')"
    )

    # Metric Groups
    coverage: OnTimeCoverageMetrics
    occupation: InfrastructureOccupationMetrics
    quality_and_timing: QualityAndTimingMetrics

    # Scope disclosure
    scope_disclosure: str = Field(
        ...,
        description="Explicit statement of horizon, workload, and excluded assumptions"
    )


class FairComparisonRequest(BaseModel):
    """
    Request to perform a fair comparison between a baseline plan and candidate plan.
    """
    corridor_code: str
    baseline_plan_id: str
    candidate_plan_id: str
    declared_domain_version: Optional[str] = None


class FairComparisonResult(BaseModel):
    """
    Defensible fair comparison between baseline (e.g. greedy/incumbent) and candidate (optimizer).
    Displays coverage before occupation gain.
    Never fabricates improvement against invalid or zero baseline.
    """
    comparison_id: str
    corridor_code: str
    baseline_plan_id: str
    candidate_plan_id: str
    baseline_is_valid: bool = Field(..., description="Whether baseline plan satisfied all hard rules")
    candidate_is_valid: bool = Field(..., description="Whether candidate plan satisfied all hard rules")

    # Aligned Scope Checks
    same_workload: bool = Field(..., description="Both plans evaluated on identical task candidates")
    same_horizon: bool = Field(..., description="Both plans evaluated on identical time window")
    same_resources: bool = Field(..., description="Both plans evaluated on identical resource pool")
    has_unequal_coverage: bool = Field(..., description="True if baseline and candidate scheduled different numbers of tasks")
    unequal_coverage_warning: Optional[str] = Field(
        None,
        description="Mandatory warning if plans have unequal coverage: a lower-coverage plan cannot appear superior for using less track"
    )

    # Coverage comparison (DISPLAYED FIRST)
    baseline_coverage_pct: Optional[float]
    candidate_coverage_pct: Optional[float]
    coverage_delta_pct: Optional[float]
    mandatory_coverage_delta_pct: Optional[float]

    # Occupation comparison (DISPLAYED SECOND)
    baseline_union_occupation_minutes: int
    candidate_union_occupation_minutes: int
    occupation_savings_minutes: int
    occupation_savings_pct: Optional[float]

    # Detailed metrics
    baseline_metrics: CalculatedPlanMetrics
    candidate_metrics: CalculatedPlanMetrics

    # Objective Evaluation
    summary_verdict: str = Field(
        ...,
        description="Defensible plain-language verdict (e.g. 'OPTIMIZER_SUPERIOR', 'NO_BENEFIT', 'OPTIMIZER_UNDERPERFORMED', 'BASELINE_INVALID')"
    )
    is_optimizer_underperforming: bool = Field(False)
    calculated_at: str


class StressPerturbation(BaseModel):
    """
    A declared, versioned stress perturbation for testing fixed-plan robustness.
    """
    perturbation_id: str
    scenario_type: StressScenarioType
    target_entity_type: str = Field(..., description="'TASK', 'RESOURCE', 'TRAIN', 'WINDOW'")
    target_entity_id: str
    magnitude_minutes: int = Field(..., description="Duration increase, late arrival delay, or shift minutes")
    description: str


class SingleScenarioResult(BaseModel):
    """
    Outcome of evaluating an unchanged plan against a single perturbation scenario.
    """
    scenario_id: str
    scenario_type: StressScenarioType
    scenario_name: str
    passed: bool = Field(..., description="Whether the unchanged plan survived without constraint violations")
    first_violation_reason: Optional[str] = Field(None, description="First rule broken if failed")
    all_violation_reasons: List[str] = Field(default_factory=list)
    worst_excess_minutes: int = Field(0, description="Maximum minutes exceeding window, curfew, or buffer")
    mandatory_tasks_affected: int = Field(0, description="Count of mandatory tasks compromised")
    is_rule_change_invalidation: bool = Field(
        False,
        description="True if failure stems from structural rule/topology invalidation rather than duration shift"
    )


class FixedPlanStressReport(BaseModel):
    """
    Full stress test report for an unchanged plan across versioned test scenarios.
    NOTE: Scenario pass share is explicitly displayed as a count ('8 of 10'),
    NOT as a pseudo-calibrated reliability probability.
    """
    stress_test_id: str
    plan_id: str
    corridor_code: str
    total_scenarios_tested: int
    passed_scenarios_count: int
    failed_scenarios_count: int
    pass_display: str = Field(..., description="Format: 'X of Y passed' (Count only, not probability)")
    scenarios: List[SingleScenarioResult]
    tested_at: str
    hardware_tag: str
    scope_disclosure: str = Field(
        default="Fixed-plan stress test evaluates unchanged assignments against declared perturbations. "
                "Scenario pass count is an uncalibrated scenario count, not an operational reliability probability."
    )


class AdaptiveStressRecoveryResult(BaseModel):
    """
    Separate experiment from fixed-plan stress: replanner execution under perturbed snapshot.
    Do not blend fixed-plan resilience and recovery success into one misleading score.
    """
    experiment_id: str
    baseline_plan_id: str
    scenario_type: StressScenarioType
    perturbation_description: str
    fixed_plan_survived: bool
    replan_attempted: bool
    replan_succeeded: bool
    replan_runtime_ms: float
    replan_plan_id: Optional[str]
    replan_churn_score: Optional[float]
    recovered_mandatory_coverage_pct: Optional[float]
    summary: str
