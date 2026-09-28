"""
Phase 14: Calculated Metrics, Fair Comparison & Stress Scenarios Tests.
Blueprint Sections: 26, 37-40.

Acceptance Test Matrix:
1. Hand-calculated union test with overlapping tasks (120m + 120m -> 180m union).
2. Multi-track electrical footprint union without double counting.
3. Zero-denominator test (None / N/A, no ZeroDivisionError or NaN).
4. Unequal-coverage comparison warning (coverage before occupation gain).
5. Invalid greedy baseline handling (no fabricated improvement).
6. Provenance pinning (snapshot, plan, calculator version, hardware tag).
7. Fixed-plan stress scenarios (all 4 declared perturbation types).
8. Scenario pass display strictly as a count ('X of Y passed'), not probability.
9. Adaptive recovery experiment separation.
10. REST API endpoints verification.
"""
import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.engine.metrics_calculator import (
    PlanMetricsCalculator,
    compute_interval_union_minutes,
    compute_interval_sum_minutes,
    CALCULATOR_VERSION,
)
from app.engine.fair_comparison import FairComparisonEngine
from app.engine.stress_testing import (
    StressTestingEngine,
    StressScenarioType,
    StressPerturbation,
    DEFAULT_STRESS_SCENARIOS,
)


# ============================================================
# Acceptance Test 1: Hand-Calculated Union Test
# ============================================================
class TestHandCalculatedUnion:
    """
    Blueprint Section 37: Count the union per resource/track segment,
    not the sum of task durations.
    """

    def test_single_track_overlapping_tasks_union(self):
        """
        Task 1: 01:00 to 03:00 (120 min)
        Task 2: 02:00 to 04:00 (120 min) - overlaps Task 1 by 60 min
        Sum = 240 min.
        Union = 01:00 to 04:00 = 180 min!
        Savings = 60 min.
        """
        t1_start = datetime(2026, 10, 2, 1, 0, tzinfo=timezone.utc)
        t1_end = datetime(2026, 10, 2, 3, 0, tzinfo=timezone.utc)
        t2_start = datetime(2026, 10, 2, 2, 0, tzinfo=timezone.utc)
        t2_end = datetime(2026, 10, 2, 4, 0, tzinfo=timezone.utc)

        intervals = [(t1_start, t1_end), (t2_start, t2_end)]

        union_mins = compute_interval_union_minutes(intervals)
        sum_mins = compute_interval_sum_minutes(intervals)

        assert sum_mins == 240, f"Expected raw sum 240m, got {sum_mins}m"
        assert union_mins == 180, f"Expected interval union 180m, got {union_mins}m"
        assert (sum_mins - union_mins) == 60, "Expected 60m co-utilization savings"

    def test_disjoint_tasks_union_equals_sum(self):
        """
        Task 1: 01:00 to 02:30 (90 min)
        Task 2: 03:30 to 05:00 (90 min) - completely disjoint
        Sum = 180 min.
        Union = 180 min.
        Savings = 0 min.
        """
        t1_start = datetime(2026, 10, 2, 1, 0, tzinfo=timezone.utc)
        t1_end = datetime(2026, 10, 2, 2, 30, tzinfo=timezone.utc)
        t2_start = datetime(2026, 10, 2, 3, 30, tzinfo=timezone.utc)
        t2_end = datetime(2026, 10, 2, 5, 0, tzinfo=timezone.utc)

        intervals = [(t1_start, t1_end), (t2_start, t2_end)]

        union_mins = compute_interval_union_minutes(intervals)
        sum_mins = compute_interval_sum_minutes(intervals)

        assert sum_mins == 180
        assert union_mins == 180
        assert (sum_mins - union_mins) == 0

    def test_completely_subsumed_task_union(self):
        """
        Task 1 (Track Possession): 00:00 to 06:00 (360 min)
        Task 2 (Civil Inspection): 02:00 to 03:30 (90 min) - completely inside Task 1
        Union = 360 min.
        Sum = 450 min.
        Savings = 90 min.
        """
        t1_start = datetime(2026, 10, 2, 0, 0, tzinfo=timezone.utc)
        t1_end = datetime(2026, 10, 2, 6, 0, tzinfo=timezone.utc)
        t2_start = datetime(2026, 10, 2, 2, 0, tzinfo=timezone.utc)
        t2_end = datetime(2026, 10, 2, 3, 30, tzinfo=timezone.utc)

        intervals = [(t1_start, t1_end), (t2_start, t2_end)]

        union_mins = compute_interval_union_minutes(intervals)
        sum_mins = compute_interval_sum_minutes(intervals)

        assert sum_mins == 450
        assert union_mins == 360
        assert (sum_mins - union_mins) == 90


# ============================================================
# Acceptance Test 2: Multi-Track Electrical Footprint
# ============================================================
class TestMultiTrackElectricalFootprint:
    """
    Blueprint Section 37: Multi-track electrical footprint.
    OHE isolation blocks both tracks; civil work blocks one track during the same interval.
    The union is computed per track segment, ensuring no double counting.
    """

    def test_multi_track_catenary_and_civil_overlap(self):
        """
        OHE Task: 01:00 - 03:00 (120m) on BOTH Track A and Track B (multi-track isolation).
        Civil Task: 02:00 - 04:00 (120m) on Track A only.

        Track A intervals: [01:00-03:00], [02:00-04:00] -> Union = 180m.
        Track B intervals: [01:00-03:00] -> Union = 120m.
        Total Network Union = 180m + 120m = 300m.
        Total Network Sum = (120 + 120) + 120 = 360m.
        Co-utilization savings = 60m.
        """
        snapshot = {
            "corridor_code": "VKC",
            "horizon_hours": 24,
            "tasks": [
                {"task_id": "TASK-OHE-01", "criticality": "HIGH", "is_mandatory": True},
                {"task_id": "TASK-CIVIL-01", "criticality": "MEDIUM", "is_mandatory": False},
            ],
            "track_segments": [
                {"segment_id": "TRACK-A", "code": "UP-LINE", "horizon_minutes": 1440},
                {"segment_id": "TRACK-B", "code": "DN-LINE", "horizon_minutes": 1440},
            ],
        }

        plan = {
            "plan_id": "plan-ohe-multi-track",
            "corridor_code": "VKC",
            "assignments": [
                {
                    "assignment_id": "asgn-ohe",
                    "task_id": "TASK-OHE-01",
                    "start_time": "2026-10-02T01:00:00Z",
                    "end_time": "2026-10-02T03:00:00Z",
                    "track_segment_ids": ["TRACK-A", "TRACK-B"],  # multi-track electrical footprint
                },
                {
                    "assignment_id": "asgn-civil",
                    "task_id": "TASK-CIVIL-01",
                    "start_time": "2026-10-02T02:00:00Z",
                    "end_time": "2026-10-02T04:00:00Z",
                    "track_segment_ids": ["TRACK-A"],
                },
            ],
        }

        metrics = PlanMetricsCalculator.calculate_plan_metrics(plan, snapshot)

        seg_map = {s.segment_id: s for s in metrics.occupation.segments}
        assert "TRACK-A" in seg_map
        assert "TRACK-B" in seg_map

        assert seg_map["TRACK-A"].maintenance_union_minutes == 180
        assert seg_map["TRACK-A"].overlap_savings_minutes == 60
        assert seg_map["TRACK-B"].maintenance_union_minutes == 120
        assert seg_map["TRACK-B"].overlap_savings_minutes == 0

        assert metrics.occupation.total_maintenance_union_minutes == 300
        assert metrics.occupation.total_co_utilization_savings_minutes == 60


# ============================================================
# Acceptance Test 3: Zero-Denominator Resilience
# ============================================================
class TestZeroDenominatorResilience:
    """
    Blueprint Section 37: Show units and N/A (None) on zero denominators.
    Never emit ZeroDivisionError, NaN, or Inf.
    """

    def test_zero_horizon_capacity(self):
        """Zero horizon minutes emits None for utilization percentage."""
        snapshot = {
            "corridor_code": "VKC",
            "horizon_hours": 0,
            "tasks": [],
            "track_segments": [
                {"segment_id": "TRACK-ZERO", "code": "ZERO", "horizon_minutes": 0},
            ],
        }
        plan = {"plan_id": "plan-zero", "assignments": []}

        metrics = PlanMetricsCalculator.calculate_plan_metrics(plan, snapshot)

        assert metrics.occupation.total_corridor_horizon_minutes == 0
        assert metrics.occupation.network_utilization_pct is None
        assert metrics.occupation.segments[0].utilization_pct is None

    def test_zero_tasks_in_scope(self):
        """Zero candidate tasks in scope emits None for coverage percentages."""
        snapshot = {
            "corridor_code": "VKC",
            "horizon_hours": 24,
            "tasks": [],
            "track_segments": [],
        }
        plan = {"plan_id": "plan-empty", "assignments": []}

        metrics = PlanMetricsCalculator.calculate_plan_metrics(plan, snapshot)

        assert metrics.coverage.total_tasks_in_scope == 0
        assert metrics.coverage.overall_coverage_pct is None
        assert metrics.coverage.mandatory_on_time_coverage_pct is None
        assert metrics.coverage.critical_on_time_coverage_pct is None

    def test_zero_hard_locks(self):
        """Zero hard locks in scope emits None for lock preservation percentage."""
        snapshot = {
            "corridor_code": "VKC",
            "tasks": [{"task_id": "T1", "is_hard_locked": False}],
            "track_segments": [],
        }
        plan = {
            "plan_id": "plan-nolock",
            "assignments": [
                {"task_id": "T1", "start_time": "2026-10-02T01:00:00Z", "end_time": "2026-10-02T03:00:00Z"}
            ],
        }

        metrics = PlanMetricsCalculator.calculate_plan_metrics(plan, snapshot)
        assert metrics.quality_and_timing.hard_locks_total == 0
        assert metrics.quality_and_timing.lock_preservation_pct is None


# ============================================================
# Acceptance Test 4: Unequal-Coverage Comparison Warning
# ============================================================
class TestFairComparisonUnequalCoverage:
    """
    Blueprint Section 37:
    - Display coverage before occupation gain.
    - A lower-coverage proposal must not appear superior merely because it occupies less track.
    - Issue prominent UnequalCoverageWarning.
    """

    def test_unequal_coverage_triggers_warning_and_ordering(self):
        """
        Baseline schedules 5 tasks. Candidate schedules 3 tasks.
        Candidate uses less track, but has LOWER coverage!
        Engine must NOT declare candidate superior merely for lower occupation!
        """
        snapshot = {
            "corridor_code": "VKC",
            "tasks": [{"task_id": f"T{i}", "is_mandatory": (i <= 2)} for i in range(1, 6)],
            "track_segments": [{"segment_id": "SEG-01", "horizon_minutes": 1440}],
        }

        baseline_plan = {
            "plan_id": "plan-baseline-high-cov",
            "assignments": [
                {"task_id": f"T{i}", "start_time": f"2026-10-02T0{i}:00:00Z", "end_time": f"2026-10-02T0{i+1}:00:00Z"}
                for i in range(1, 6)
            ],
        }

        # Candidate only schedules 3 tasks -> leaves 2 unscheduled -> occupies less track
        candidate_plan = {
            "plan_id": "plan-candidate-low-cov",
            "assignments": [
                {"task_id": f"T{i}", "start_time": f"2026-10-02T0{i}:00:00Z", "end_time": f"2026-10-02T0{i+1}:00:00Z"}
                for i in range(1, 4)
            ],
        }

        comp = FairComparisonEngine.compare_plans(baseline_plan, candidate_plan, snapshot)

        assert comp.has_unequal_coverage is True
        assert comp.unequal_coverage_warning is not None
        assert "UNEQUAL COVERAGE WARNING" in comp.unequal_coverage_warning
        assert comp.is_optimizer_underperforming is True
        assert comp.summary_verdict == "OPTIMIZER_UNDERPERFORMED_COVERAGE_DROP"


# ============================================================
# Acceptance Test 5: Invalid Baseline Handling (No Fabricated Gains)
# ============================================================
class TestInvalidBaselineHandling:
    """
    Blueprint Section 37: If the greedy baseline finds no valid plan, show that outcome;
    do not fabricate a percentage improvement against an invalid or zero baseline.
    """

    def test_invalid_baseline_does_not_fabricate_percentage(self):
        snapshot = {
            "corridor_code": "VKC",
            "tasks": [{"task_id": "T1", "is_mandatory": True}],
            "track_segments": [{"segment_id": "SEG-01", "horizon_minutes": 1440}],
        }

        # Baseline found no valid schedule
        baseline_plan = {
            "plan_id": "plan-greedy-failed",
            "is_valid": False,
            "assignments": [],
        }

        candidate_plan = {
            "plan_id": "plan-optimizer-valid",
            "is_valid": True,
            "assignments": [
                {"task_id": "T1", "start_time": "2026-10-02T02:00:00Z", "end_time": "2026-10-02T04:00:00Z"}
            ],
        }

        comp = FairComparisonEngine.compare_plans(baseline_plan, candidate_plan, snapshot)

        assert comp.baseline_is_valid is False
        assert comp.candidate_is_valid is True
        # Do not fabricate a percentage improvement against an invalid baseline!
        assert comp.occupation_savings_pct is None
        assert comp.summary_verdict == "OPTIMIZER_SUPERIOR_BASELINE_INVALID"


# ============================================================
# Acceptance Test 6: Provenance Pinning
# ============================================================
class TestProvenancePinning:
    """
    Blueprint Section 37: Every result pins snapshot, plan/run, calculator,
    rule/policy and domain versions. Hardware tag is explicitly marked.
    """

    def test_metrics_pin_all_required_provenance_keys(self):
        snapshot = {
            "snapshot_id": "snap-vkc-sealed-001",
            "corridor_code": "VKC",
            "tasks": [{"task_id": "T1"}],
            "track_segments": [{"segment_id": "SEG-01", "horizon_minutes": 1440}],
        }
        plan = {
            "plan_id": "plan-pinned-01",
            "plan_version_number": 2,
            "corridor_code": "VKC",
            "snapshot_id": "snap-vkc-sealed-001",
            "assignments": [
                {"task_id": "T1", "start_time": "2026-10-02T01:00:00Z", "end_time": "2026-10-02T03:00:00Z"}
            ],
        }

        metrics = PlanMetricsCalculator.calculate_plan_metrics(
            plan, snapshot, rule_policy_version="v2.1-REGULATORY", domain_version="VKC-72H-TEST"
        )

        assert metrics.snapshot_id == "snap-vkc-sealed-001"
        assert metrics.plan_id == "plan-pinned-01"
        assert metrics.plan_version == 2
        assert metrics.calculator_version == CALCULATOR_VERSION
        assert metrics.rule_policy_version == "v2.1-REGULATORY"
        assert metrics.domain_version == "VKC-72H-TEST"
        assert metrics.hardware_tag is not None and len(metrics.hardware_tag) > 0
        assert metrics.scope_disclosure is not None


# ============================================================
# Acceptance Test 7: Fixed-Plan Stress Scenarios
# ============================================================
class TestFixedPlanStressScenarios:
    """
    Blueprint Section 38: Fixed-plan stress testing with versioned declared TEST perturbations:
    1. WORK_DURATION_INCREASE
    2. LATE_RESOURCE_ARRIVAL
    3. SHIFTED_GOODS_FORECAST
    4. URGENT_UNPLANNED_WORK

    Pass share is strictly displayed as count ('8 of 10 passed'), not probability!
    """

    def test_run_stress_scenarios_all_four_types(self):
        plan = {
            "plan_id": "plan-stress-test",
            "corridor_code": "VKC",
            "assignments": [
                {
                    "assignment_id": "a1",
                    "task_id": "TASK-CIVIL-01",
                    "start_time": "2026-10-02T01:00:00Z",
                    "end_time": "2026-10-02T03:00:00Z",
                }
            ],
        }

        report = StressTestingEngine.run_fixed_plan_stress_test(plan)

        assert report.total_scenarios_tested == 10
        assert len(report.scenarios) == 10

        # Verify all 4 types exist in tested scenarios
        types_tested = {s.scenario_type for s in report.scenarios}
        assert StressScenarioType.WORK_DURATION_INCREASE in types_tested
        assert StressScenarioType.LATE_RESOURCE_ARRIVAL in types_tested
        assert StressScenarioType.SHIFTED_GOODS_FORECAST in types_tested
        assert StressScenarioType.URGENT_UNPLANNED_WORK in types_tested

        # Check count-only display format
        assert report.pass_display.endswith("passed")
        assert "of 10 passed" in report.pass_display
        assert "%" not in report.pass_display, "Pass share must be a count only, not a probability percentage"

        # Check failures record reasons and worst excess minutes
        failed_scenarios = [s for s in report.scenarios if not s.passed]
        assert len(failed_scenarios) > 0
        for f in failed_scenarios:
            assert f.first_violation_reason is not None
            assert len(f.all_violation_reasons) > 0
            assert f.worst_excess_minutes > 0


# ============================================================
# Acceptance Test 8: Adaptive Recovery Experiment Separation
# ============================================================
class TestAdaptiveRecoverySeparation:
    """
    Blueprint Section 38: Adaptive re-solving under a perturbed snapshot is a separate
    experiment with runtime, new version and PlanDiff.
    Do not blend fixed-plan resilience and recovery success into one misleading score.
    """

    def test_adaptive_recovery_experiment(self):
        plan = {
            "plan_id": "plan-to-recover",
            "corridor_code": "VKC",
            "assignments": [{"assignment_id": "a1", "task_id": "T1"}],
        }

        recovery = StressTestingEngine.run_adaptive_recovery_experiment(plan)

        assert recovery.replan_attempted is True
        assert recovery.replan_succeeded is True
        assert recovery.replan_runtime_ms > 0
        assert recovery.replan_churn_score is not None
        assert recovery.recovered_mandatory_coverage_pct == 100.0


# ============================================================
# Acceptance Test 9: REST API Endpoints Verification
# ============================================================
class TestEvaluationApiEndpoints:
    """
    Verifies FastAPI endpoints under /api/v1/evaluation.
    """

    def test_get_scenarios_endpoint(self, client):
        resp = client.get("/api/v1/evaluation/scenarios")
        assert resp.status_code == 200
        scenarios = resp.json()
        assert len(scenarios) == 10
        assert any(s["scenario_type"] == "WORK_DURATION_INCREASE" for s in scenarios)

    def test_calculate_metrics_endpoint(self, client):
        payload = {
            "plan_data": {
                "plan_id": "plan-api-test",
                "corridor_code": "VKC",
                "assignments": [
                    {
                        "assignment_id": "a1",
                        "task_id": "T1",
                        "start_time": "2026-10-02T01:00:00Z",
                        "end_time": "2026-10-02T03:00:00Z",
                        "track_segment_ids": ["VKC-SEG-01"],
                    }
                ],
            },
            "snapshot_data": {
                "corridor_code": "VKC",
                "horizon_hours": 72,
                "tasks": [
                    {"task_id": "T1", "criticality": "MANDATORY", "is_mandatory": True},
                    {"task_id": "T2", "criticality": "ROUTINE", "is_mandatory": False},
                ],
                "track_segments": [
                    {"segment_id": "VKC-SEG-01", "code": "SEG-01", "horizon_minutes": 4320}
                ],
            },
        }
        resp = client.post("/api/v1/evaluation/metrics/calculate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["calculator_version"] == CALCULATOR_VERSION
        assert data["coverage"]["total_tasks_in_scope"] == 2
        assert data["coverage"]["total_tasks_scheduled"] == 1
        assert data["coverage"]["mandatory_on_time_coverage_pct"] == 100.0
        assert data["occupation"]["total_maintenance_union_minutes"] == 120

    def test_compare_endpoint(self, client):
        payload = {
            "baseline_plan": {
                "plan_id": "plan-b",
                "assignments": [
                    {"task_id": "T1", "start_time": "2026-10-02T01:00:00Z", "end_time": "2026-10-02T03:00:00Z"}
                ],
            },
            "candidate_plan": {
                "plan_id": "plan-c",
                "assignments": [
                    {"task_id": "T1", "start_time": "2026-10-02T01:00:00Z", "end_time": "2026-10-02T03:00:00Z"},
                    {"task_id": "T2", "start_time": "2026-10-02T03:00:00Z", "end_time": "2026-10-02T05:00:00Z"},
                ],
            },
            "snapshot": {
                "corridor_code": "VKC",
                "tasks": [{"task_id": "T1"}, {"task_id": "T2"}],
                "track_segments": [{"segment_id": "SEG-01", "horizon_minutes": 1440}],
            },
        }
        resp = client.post("/api/v1/evaluation/compare", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["same_workload"] is True
        assert data["has_unequal_coverage"] is True
        assert data["summary_verdict"] == "OPTIMIZER_SUPERIOR_HIGHER_COVERAGE"

    def test_stress_test_endpoint(self, client):
        payload = {
            "plan_data": {
                "plan_id": "plan-stress-api",
                "corridor_code": "VKC",
                "assignments": [
                    {"task_id": "T1", "start_time": "2026-10-02T01:00:00Z", "end_time": "2026-10-02T03:00:00Z"}
                ],
            }
        }
        resp = client.post("/api/v1/evaluation/stress-test", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_scenarios_tested"] == 10
        assert "passed" in data["pass_display"]
