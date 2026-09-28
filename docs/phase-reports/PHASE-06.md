# Phase 06 Completion Report: Sparse Opportunity Generation and a Credible Baseline

**Phase ID:** PHASE-06  
**Phase Title:** Sparse Opportunity Generation and a Credible Baseline  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 06 delivers the high-performance sparse opportunity generation engine and the coordinated greedy baseline benchmark solver per Blueprint Sections 19, 21, and 22:

1. **Declared Discretization Lattice & Candidate Generator (`backend/app/engine/candidate_generator.py`):**
   - Discretizes time into declared lattice steps (e.g. 15m, 30m, 60m) referenced strictly to the immutable snapshot horizon epoch (`horizon_start_utc`).
   - Replaces naive $O(N^2)$ global scanning with spatial and temporal index structures (`train_index` keyed by `track_segment_id`, `outage_index` keyed by `resource_id`).
   - Evaluates multi-track footprints and neutral section de-energization isolation windows (e.g. Charlie station Neutral Section affects both UP and DN main tracks).
   - Prunes candidates overlapping scheduled train paths, machine overhaul outages, and expired deadlines.
   - Respects cross-midnight boundaries without date-wrapping bugs.
   - Guards against memory bloat and DOS via explicit `DOMAIN_TRUNCATED` ceiling guardrails.

2. **Strict Hard Lock Equality Constraints:**
   - Any task marked with a locked commitment is constrained to its exact designated minute:
     $$\text{start\_minute} = \text{lock.start\_minute}$$
   - The candidate generator eliminates all non-matching start ticks, guaranteeing that zero non-compliant candidates enter downstream evaluation.
   - In accordance with Blueprint Section 22 Invariant 1, hard locks are mathematically enforced as hard equality constraints, never soft penalties or relaxable objectives.

3. **Coordinated Priority-First Greedy Baseline Solver (`backend/app/engine/greedy_baseline.py`):**
   - Implements a credible, non-strawman benchmark solver representing skilled manual controller heuristics.
   - **Ordering Hierarchy:** Strictly orders tasks by criticality tier (`TIER_1_MANDATORY` sorted by deadline, followed by `TIER_2_SPEED_RESTRICTION`, then `TIER_3_CYCLIC`).
   - **Invariants Enforced:**
     - Enforces at-most-once task coverage across singletons and bundled packages.
     - Preserves all locked commitments without shifting.
     - Generates zero track collision and zero resource double-booking.
   - **One-Step Bounded Repair Pass:** If a mandatory task cannot be placed due to routine cyclic work, the repair pass evicts blocking non-mandatory assignments to schedule the mandatory demand.
   - **Truthful Status Reporting:** If mandatory demand remains unplaced due to genuine physical infeasibility, the baseline returns `BASELINE_NO_FEASIBLE_PLAN_FOUND` rather than concealing failures.

4. **REST Planning APIs (`backend/app/api/v1/planning.py`):**
   - `POST /api/v1/planning/candidates/generate`: Generates and returns a typed `CandidateManifest` with detailed pruning metrics and truncation status.
   - `POST /api/v1/planning/baseline/solve`: Executes the greedy baseline solver and returns a typed `BaselineSolveResult` with assignments, unscheduled demands, and runtime metrics.

---

## 2. Verification Evidence and Benchmark Performance

### 2.1 Automated Test Suite (`backend/tests/test_candidate_baseline.py`)
All 8 automated tests passed in **1.12 seconds**:
```
tests/test_candidate_baseline.py::test_sparse_candidate_generation_and_pruning PASSED [ 12%]
tests/test_candidate_baseline.py::test_hard_lock_strict_equality_enforcement PASSED   [ 25%]
tests/test_candidate_baseline.py::test_cross_midnight_candidate_containment PASSED   [ 37%]
tests/test_candidate_baseline.py::test_domain_truncation_ceiling PASSED            [ 50%]
tests/test_candidate_baseline.py::test_greedy_baseline_solver_execution PASSED       [ 62%]
tests/test_candidate_baseline.py::test_greedy_baseline_repair_pass PASSED            [ 75%]
tests/test_candidate_baseline.py::test_benchmark_performance_timing PASSED          [ 87%]
tests/test_candidate_baseline.py::test_planning_api_endpoints PASSED               [100%]
```

### 2.2 Performance Benchmark Measurements
- **Candidate Generation Wall Time:** $< 45\text{ ms}$ for standard weekly corridor instance.
- **Greedy Baseline Solve Wall Time:** $< 20\text{ ms}$ for standard corridor instance.
- **Combined Pipeline Execution Time:** $< 70\text{ ms}$ (well below the 1.50s requirement).
- **Domain Truncation Protection:** Verified that instances exceeding candidate ceilings flag `DOMAIN_TRUNCATED` cleanly without crashing.

---

## 3. Invariants & Blueprint Adherence

| Invariant / Requirement | Blueprint Spec | Implementation Verification | Status |
|---|---|---|---|
| **Hard Lock Equality** | Sec 22 Inv 1 | Only candidates matching `lock.start_minute` emitted; baseline preserves all locks | **PASS** |
| **No Fabrication** | Sec 19 | Pure deterministic spatial/temporal calculation; honest `BASELINE_NO_FEASIBLE_PLAN_FOUND` | **PASS** |
| **At-Most-Once Coverage** | Sec 21 | Task ID deduplication prevents double-counting across bundles | **PASS** |
| **Cross-Midnight Containment** | Sec 21 | Time computed as offset minutes from horizon epoch; `end_utc > start_utc` verified | **PASS** |
| **No O(N^2) Train Scanning** | Sec 19 | Track segment index `train_index[seg_id]` cuts search complexity | **PASS** |

---

## 4. Next Phase Gate

- **Next Phase:** Phase 07 (`07_INDEPENDENT_FEASIBILITY_CHECKER_AND_CORRECTNESS_ORACLE.md`).
- **Dependencies Ready:** Pure snapshot representations, raw candidate manifests, baseline solve results, and verified domain rules.
