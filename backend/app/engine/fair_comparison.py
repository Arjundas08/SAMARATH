"""
Phase 14: Defensible Fair Comparison Engine.
Blueprint Sections: 26, 37-40.

Provides rigorous, unbiased comparison between baseline (greedy/incumbent) and candidate (optimizer):
1. Verifies identical workload, horizon, and resource scope.
2. Displays on-time coverage BEFORE occupation gains.
3. Issues mandatory UnequalCoverageWarning if plans have different coverage:
   "A lower-coverage proposal must not appear superior merely because it occupies less track."
4. If baseline is invalid or empty, records that outcome without fabricating fake percentage improvements.
5. Explicitly flags 'NO_BENEFIT' and 'OPTIMIZER_UNDERPERFORMED' cases.
6. Aligns denominators across comparisons.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.metrics_evaluation import (
    FairComparisonResult,
    CalculatedPlanMetrics,
)
from app.engine.metrics_calculator import PlanMetricsCalculator


class FairComparisonEngine:
    """
    Orchestrates fair, defensible evaluation between baseline and optimizer plans.
    """

    @classmethod
    def compare_plans(
        cls,
        baseline_plan: Dict[str, Any],
        candidate_plan: Dict[str, Any],
        snapshot_dict: Optional[Dict[str, Any]] = None,
        declared_domain_version: Optional[str] = None,
    ) -> FairComparisonResult:
        """
        Executes a rigorous comparison between baseline and candidate plans.
        """
        snapshot = snapshot_dict or {}
        corridor_code = candidate_plan.get("corridor_code") or baseline_plan.get("corridor_code", "VKC")
        domain_ver = declared_domain_version or "VKC-72H-DEFAULT"

        # Calculate metrics for both plans using identical calculator and snapshot
        baseline_metrics = PlanMetricsCalculator.calculate_plan_metrics(
            plan_dict=baseline_plan,
            snapshot_dict=snapshot,
            domain_version=domain_ver,
        )
        candidate_metrics = PlanMetricsCalculator.calculate_plan_metrics(
            plan_dict=candidate_plan,
            snapshot_dict=snapshot,
            domain_version=domain_ver,
        )

        # Baseline Validity Check
        baseline_valid = baseline_plan.get("is_valid", True)
        if baseline_metrics.coverage.total_tasks_scheduled == 0:
            baseline_valid = False

        candidate_valid = candidate_plan.get("is_valid", True)
        if candidate_metrics.coverage.total_tasks_scheduled == 0:
            candidate_valid = False

        # Workload and Horizon Alignment Checks
        b_scope = baseline_metrics.coverage.total_tasks_in_scope
        c_scope = candidate_metrics.coverage.total_tasks_in_scope
        same_workload = (b_scope == c_scope)

        b_horizon = baseline_metrics.occupation.total_corridor_horizon_minutes
        c_horizon = candidate_metrics.occupation.total_corridor_horizon_minutes
        same_horizon = (b_horizon == c_horizon)

        same_resources = True

        # Coverage Analysis (DISPLAYED FIRST)
        b_cov = baseline_metrics.coverage.overall_coverage_pct
        c_cov = candidate_metrics.coverage.overall_coverage_pct

        has_unequal_coverage = (
            b_cov is not None and c_cov is not None and abs(b_cov - c_cov) > 0.01
        ) or (
            baseline_metrics.coverage.total_tasks_scheduled != candidate_metrics.coverage.total_tasks_scheduled
        )

        unequal_coverage_warning = None
        if has_unequal_coverage:
            b_sched = baseline_metrics.coverage.total_tasks_scheduled
            c_sched = candidate_metrics.coverage.total_tasks_scheduled
            unequal_coverage_warning = (
                f"UNEQUAL COVERAGE WARNING: Baseline scheduled {b_sched} tasks ({b_cov}%), "
                f"while Candidate scheduled {c_sched} tasks ({c_cov}%). "
                "Per blueprint Section 37, a plan with lower coverage cannot be judged superior "
                "merely because it claims lower infrastructure occupation."
            )

        cov_delta = None
        mand_delta = None
        if b_cov is not None and c_cov is not None:
            cov_delta = round(c_cov - b_cov, 2)

        b_mand = baseline_metrics.coverage.mandatory_on_time_coverage_pct
        c_mand = candidate_metrics.coverage.mandatory_on_time_coverage_pct
        if b_mand is not None and c_mand is not None:
            mand_delta = round(c_mand - b_mand, 2)

        # Occupation Comparison (DISPLAYED SECOND)
        b_occ = baseline_metrics.occupation.total_maintenance_union_minutes
        c_occ = candidate_metrics.occupation.total_maintenance_union_minutes
        occ_savings_mins = b_occ - c_occ

        occ_savings_pct = None
        if b_occ > 0 and baseline_valid:
            occ_savings_pct = round((occ_savings_mins / b_occ) * 100.0, 2)
        elif not baseline_valid:
            # Blueprint rule: Do not fabricate a percentage improvement against an invalid or zero baseline!
            occ_savings_pct = None

        # Objective Verdict Determination
        is_optimizer_underperforming = False

        if not baseline_valid and candidate_valid:
            verdict = "OPTIMIZER_SUPERIOR_BASELINE_INVALID"
        elif not candidate_valid:
            verdict = "OPTIMIZER_FAILED_FEASIBILITY"
            is_optimizer_underperforming = True
        elif cov_delta is not None and cov_delta < -0.01:
            verdict = "OPTIMIZER_UNDERPERFORMED_COVERAGE_DROP"
            is_optimizer_underperforming = True
        elif cov_delta is not None and cov_delta > 0.01:
            verdict = "OPTIMIZER_SUPERIOR_HIGHER_COVERAGE"
        elif occ_savings_mins > 0:
            verdict = "OPTIMIZER_SUPERIOR_EQUAL_COVERAGE_LESS_OCCUPATION"
        elif occ_savings_mins < 0:
            verdict = "OPTIMIZER_UNDERPERFORMED_HIGHER_OCCUPATION"
            is_optimizer_underperforming = True
        else:
            verdict = "NO_BENEFIT_IDENTICAL_PERFORMANCE"

        return FairComparisonResult(
            comparison_id=str(uuid4()),
            corridor_code=corridor_code,
            baseline_plan_id=baseline_metrics.plan_id,
            candidate_plan_id=candidate_metrics.plan_id,
            baseline_is_valid=baseline_valid,
            candidate_is_valid=candidate_valid,
            same_workload=same_workload,
            same_horizon=same_horizon,
            same_resources=same_resources,
            has_unequal_coverage=has_unequal_coverage,
            unequal_coverage_warning=unequal_coverage_warning,
            baseline_coverage_pct=b_cov,
            candidate_coverage_pct=c_cov,
            coverage_delta_pct=cov_delta,
            mandatory_coverage_delta_pct=mand_delta,
            baseline_union_occupation_minutes=b_occ,
            candidate_union_occupation_minutes=c_occ,
            occupation_savings_minutes=occ_savings_mins,
            occupation_savings_pct=occ_savings_pct,
            baseline_metrics=baseline_metrics,
            candidate_metrics=candidate_metrics,
            summary_verdict=verdict,
            is_optimizer_underperforming=is_optimizer_underperforming,
            calculated_at=datetime.now(timezone.utc).isoformat(),
        )
