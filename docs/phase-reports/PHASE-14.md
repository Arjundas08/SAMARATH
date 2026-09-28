# Phase 14 Completion Report: Calculated Metrics, Fair Comparison and Stress Scenarios

**Phase ID:** PHASE-14  
**Phase Title:** Calculated Metrics, Fair Comparison and Stress Scenarios  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 14 establishes a versioned metric calculator, defensible fair comparison benchmark, and fixed-plan perturbation testbench for SAMARATH in accordance with Blueprint Sections 26, 37-40. Rail optimization platforms frequently suffer from misleading claims where a heuristic is declared "superior" merely because it occupies less track, when in fact it simply scheduled fewer tasks. Phase 14 eliminates this bias by establishing mathematically provable interval union infrastructure occupation, enforcing identical workload/horizon scopes, displaying on-time coverage before occupation, issuing mandatory unequal-coverage warnings, and strictly refusing to fabricate percentage gains against invalid baselines.

### Key Invariants Delivered & Verified:
1. **No Release KPI Stored as an Editable Constant:**
   - Every metric is dynamically calculated from actual plan assignments, timetable lattices, and sealed snapshot records.
2. **Interval Union Infrastructure Occupation:**
   - Measures the mathematical length of overlapping maintenance windows $\bigcup [s_i, e_i]$ per track segment.
   - Raw arithmetic sums are not used for occupation; sum minus union is explicitly reported as *Co-utilization Savings*.
   - Multi-track electrical footprint (OHE catenary isolations affecting multiple lines) correctly accounted without double counting.
3. **Zero-Denominator Safety Guards:**
   - Zero horizon minutes, zero candidate tasks, or zero hard locks emit `None` / `N/A`, never raising `ZeroDivisionError` or producing `NaN` / `Inf`.
4. **Coverage Before Occupation Rule (Section 37):**
   - Fair comparison displays on-time coverage before occupation savings.
   - Prominent `UnequalCoverageWarning` issued if candidate and baseline scheduled different numbers of tasks:
     *"A lower-coverage proposal must not appear superior merely because it occupies less track."*
5. **No Fabricated Improvement on Invalid Baselines:**
   - If the greedy baseline fails or produces an empty schedule, the outcome is recorded as `BASELINE_INVALID`; no artificial "+100%" or arbitrary gains are fabricated.
6. **Fixed-Plan Stress Testing (4 Declared Perturbations):**
   - Versioned testbench testing unchanged assignments against:
     1. `WORK_DURATION_INCREASE`: Task takes longer than nominal estimate.
     2. `LATE_RESOURCE_ARRIVAL`: Machinery/gang arrives late.
     3. `SHIFTED_GOODS_FORECAST`: Freight train schedule encroaches into window.
     4. `URGENT_UNPLANNED_WORK`: Emergency track possession inserted.
   - **Pass share display rule:** Explicitly formatted as count only (`8 of 10 passed`), NOT as an uncalibrated reliability probability.
7. **Adaptive Recovery Experiment Separation:**
   - Dynamic re-solving under perturbed snapshots is kept as a separate experiment; never blended into fixed-plan robustness scores.
8. **Pinned Provenance & Hardware Attribution:**
   - Every metric report pins `snapshot_id`, `plan_id`, `calculator_version` (`1.4.0`), `rule_policy_version`, `domain_version`, and execution `hardware_tag` (e.g. `AMD Ryzen / Intel Core on Windows, Python 3.13 (Measured Benchmark)`).

---

## 2. Architecture & Components

- **Schemas (`backend/app/schemas/metrics_evaluation.py`):**
  - `OnTimeCoverageMetrics`: Mandatory, critical, routine, permitted lateness, and unscheduled reasons breakdown.
  - `SegmentUnionOccupation`: Segment-level interval union, fixed closures, and overlap savings.
  - `InfrastructureOccupationMetrics`: Network-wide union occupation and capacity utilization.
  - `CalculatedPlanMetrics`: Pinned root metric report.
  - `FairComparisonResult`: Aligned comparison, unequal coverage warning, and plain-language verdict.
  - `FixedPlanStressReport`: 10 versioned scenarios with pass count.
  - `AdaptiveStressRecoveryResult`: Re-solve experiment results.
- **Engines:**
  - `backend/app/engine/metrics_calculator.py`: Interval union algorithm $\bigcup [s_i, e_i]$, zero-denominator guards, and provenance pinning.
  - `backend/app/engine/fair_comparison.py`: Aligned workload/horizon checks, coverage prioritization, and invalid baseline protection.
  - `backend/app/engine/stress_testing.py`: Fixed-plan perturbation runner and adaptive recovery re-solver.
- **REST Endpoints (`backend/app/api/v1/evaluation.py`):**
  - `GET /api/v1/evaluation/scenarios`: 10 declared stress test perturbations.
  - `POST /api/v1/evaluation/metrics/calculate`: Pinned metrics calculation.
  - `POST /api/v1/evaluation/compare`: Fair comparison between baseline and candidate.
  - `POST /api/v1/evaluation/stress-test`: Fixed-plan stress testbench.
  - `POST /api/v1/evaluation/adaptive-stress-test`: Adaptive recovery re-solve.
- **Frontend Defensible Evaluation Cockpit:**
  - `frontend/src/types/evaluation.ts`: TypeScript definitions.
  - `frontend/src/api/evaluation.ts`: API client.
  - `frontend/src/views/EvaluationView.tsx`: Quiet, defensible evaluation cockpit with aligned denominators, union breakdown table, fair comparison matrix, fixed-plan stress testbench ('8 of 10 passed'), and raw JSON export.
  - Integrated into `App.tsx` and `AppShell.tsx` navigation.

---

## 3. Automated Test Verification

**Test Suite:** `backend/tests/test_phase14_metrics_and_stress.py`  
**Results:** **16 passed / 16 total (100%) in 0.45s**  
**Combined Regression Suite (Phase 13 + 14):** **53 passed / 53 total (100%) in 36.48s**

| Test Name | Acceptance Criteria Verified | Status |
|:---|:---|:---:|
| `test_single_track_overlapping_tasks_union` | 120m + 120m overlapping tasks -> 180m union (60m savings) | **PASSED** |
| `test_disjoint_tasks_union_equals_sum` | Non-overlapping tasks yield union == sum (0m savings) | **PASSED** |
| `test_completely_subsumed_task_union` | Subsumed task yields union == outer duration (90m savings) | **PASSED** |
| `test_multi_track_catenary_and_civil_overlap` | Multi-track electrical footprint union across Track A & B | **PASSED** |
| `test_zero_horizon_capacity` | Zero horizon minutes emits `None` / N/A, zero division safe | **PASSED** |
| `test_zero_tasks_in_scope` | Zero candidate tasks emits `None` / N/A for coverage | **PASSED** |
| `test_zero_hard_locks` | Zero hard locks emits `None` / N/A for lock preservation | **PASSED** |
| `test_unequal_coverage_triggers_warning_and_ordering` | Unequal coverage warning; coverage ordered before occupation | **PASSED** |
| `test_invalid_baseline_does_not_fabricate_percentage` | Invalid greedy baseline emits `None` savings %, no fake gain | **PASSED** |
| `test_metrics_pin_all_required_provenance_keys` | Pins snapshot, plan, calculator v1.4.0, hardware tag | **PASSED** |
| `test_run_stress_scenarios_all_four_types` | Tests all 4 perturbation types; pass count format 'X of Y' | **PASSED** |
| `test_adaptive_recovery_experiment` | Adaptive recovery runs as distinct experiment with runtime & churn | **PASSED** |
| `test_get_scenarios_endpoint` | REST API lists all 10 declared stress scenarios | **PASSED** |
| `test_calculate_metrics_endpoint` | REST API computes pinned metrics with interval union | **PASSED** |
| `test_compare_endpoint` | REST API conducts fair comparison with unequal coverage flag | **PASSED** |
| `test_stress_test_endpoint` | REST API executes fixed-plan stress test | **PASSED** |
