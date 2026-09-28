# Phase 08 Completion Report: Real CP-SAT Weekly Optimizer and Lexicographic Profiles

**Phase ID:** PHASE-08  
**Phase Title:** Real CP-SAT Weekly Optimizer and Lexicographic Profiles  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 08 implements the production-grade, bounded weekly optimizer using Google OR-Tools CP-SAT per Blueprint Sections 17, 18, 19, 22, 23, 27, and 42:

1. **Finite-Placement Formulation with Sparse Intervals (`backend/app/engine/cp_sat_solver.py`):**
   - **Decision Variables:** Finite-placement formulation with one Boolean variable $x[c] \in \{0, 1\}$ per candidate placement and task indicator $u[t] \in \{0, 1\}$.
   - **Sparse Model Structures:** Rather than allocating dense candidate-by-minute tensors or generating $O(N^2)$ pairwise boolean collision clauses, the model instantiates sparse `NewOptionalIntervalVar` instances for each candidate.
   - **Track & Electrical Footprint Protection:** Native `model.AddNoOverlap(...)` is enforced on all track segments including adjacent tracks isolated by neutral section de-energization (`affected_adjacent_tracks`).
   - **Multi-Resource Discrete Capacity:** Handled via `AddNoOverlap` for singleton machines and `AddCumulative` for multi-crew/supervisor pools, preventing double-counting across overlapping intervals.
   - **Strict Hard Lock Equality:** Hard commitments are modeled as strict mathematical equality constraints (`sum(x[c] for matching c) == 1`), never treated as soft penalties or relaxed.
   - **Mandatory Statutory Coverage:** Enforces $u[t] == 1$ for all Tier-1 Mandatory tasks; returns `INFEASIBLE` with truthful explanation if any statutory task cannot be scheduled within available gaps.

2. **Lexicographic Objective Profiles:**
   - **`PROGRAMME_IMPROVEMENT` (Routine Weekly Formulation):**
     - *Stage 1 (Primary):* Maximize high-priority tasks ($\text{Weight} = 10$ for Speed Restriction remediation, $\text{Weight} = 1$ for cyclic maintenance).
     - *Stage 2 (Secondary):* Maximize bundled cross-departmental work packages (`bundle_expr = sum(x[c] for c if len(c.task_ids) > 1)`).
     - *Stage 3 (Tertiary):* Minimize total traffic possession block duration to preserve network throughput.
   - **`DISRUPTION_RECOVERY` (Event-Driven Minimal Churn):**
     - Preserves required statutory work and hard locks.
     - *Stage 1 (Primary):* Minimize schedule churn against the original baseline plan (time shift penalties in 15m increments + cancellation fixed penalty).
     - *Stage 2 (Secondary):* Minimize total block minutes.
     - Documented invariant: Avoids rearranging multiple undisturbed tasks for marginal single-minute efficiency gains.

3. **Time-Budgeted Multi-Stage Solving & Incumbent Preservation:**
   - Evaluates lexicographic stages under a strict wall-clock budget.
   - Freezes stage objective values only upon proven `OPTIMAL` status.
   - Preserves earlier qualified incumbents across lower-stage timeouts or interruptions; never outputs unverified solutions.
   - Integrated with Phase 06 `GreedyBaselineSolver` for warmstart hint seeding (`model.AddHint`), enabling instant branch-and-bound pruning even on large corridors (7,400+ candidates).

4. **Independent Oracle & Feasibility Checker Verification:**
   - Every generated plan automatically passes through the independent Phase 07 `feasibility_checker.py` post-solve before result delivery.
   - Mathematical agreement verified against the `ExhaustiveTinyOracle` on objective values.

---

## 2. Verification Evidence and Test Results

### 2.1 Automated Test Suite (`backend/tests/test_cp_sat_optimizer.py`)
All 7 automated tests passed in **14.25 seconds**:
```
tests/test_cp_sat_optimizer.py::test_tiny_exhaustive_oracle_agreement PASSED          [ 14%]
tests/test_cp_sat_optimizer.py::test_mandatory_impossibility_truthfully_reported PASSED [ 28%]
tests/test_cp_sat_optimizer.py::test_strict_hard_lock_preservation PASSED             [ 42%]
tests/test_cp_sat_optimizer.py::test_deterministic_single_worker_regression PASSED   [ 57%]
tests/test_cp_sat_optimizer.py::test_disruption_recovery_minimizes_churn PASSED       [ 71%]
tests/test_cp_sat_optimizer.py::test_comparison_cp_sat_vs_greedy_baseline PASSED      [ 85%]
tests/test_cp_sat_optimizer.py::test_optimizer_planning_api_endpoint PASSED           [100%]

======================= 7 passed, 6 warnings in 14.25s ========================
```

### 2.2 Full Regression Suite Across All Phases (00 to 08)
Executed `pytest tests/ -v`:
```
====================== 63 passed, 245 warnings in 19.41s ======================
```
Zero regressions detected across all 63 repository tests.

---

## 3. Verified Invariants and Implementation Highlights

| Blueprint / Addendum Invariant | Implementation Mechanism | Verification Test |
|---|---|---|
| **Exhaustive Oracle Agreement** | CP-SAT matches mathematical ground truth from brute-force Cartesian solver | `test_tiny_exhaustive_oracle_agreement` |
| **Truthful Mandatory Impossibility** | Returns `INFEASIBLE` with `StopReason.INFEASIBILITY_PROVEN` when all slots are physically blocked | `test_mandatory_impossibility_truthfully_reported` |
| **Strict Hard Lock Equality** | 0s tolerance preserved: hard lock start times never shifted | `test_strict_hard_lock_preservation` |
| **Deterministic Regression** | 1 worker + fixed seed generates identical bitwise schedules across independent runs | `test_deterministic_single_worker_regression` |
| **Minimal Churn in Disruption** | Emergency train injection redirects affected tasks while preserving undisturbed assignments | `test_disruption_recovery_minimizes_churn` |
| **Baseline Superiority** | CP-SAT schedules equal or greater tasks than greedy heuristic | `test_comparison_cp_sat_vs_greedy_baseline` |
| **Full Checker Approval** | REST endpoint `/api/v1/planning/optimizer/solve` outputs `CheckerVerdict.VALID` on live VKC corridor | `test_optimizer_planning_api_endpoint` |

---

## 4. API Specification

- **Endpoint:** `POST /api/v1/planning/optimizer/solve`
- **Request Payload (`OptimizerSolveRequest`):**
  - `corridor_code: str` (default: `"VKC"`)
  - `profile: ObjectiveProfile` (`PROGRAMME_IMPROVEMENT` or `DISRUPTION_RECOVERY`)
  - `time_limit_seconds: float` (default: `15.0`)
  - `num_workers: int` (default: `1`)
  - `random_seed: int` (default: `42`)
  - `lattice_step_minutes: int` (default: `30`)
  - `original_plan: Optional[ProposedPlan]` (required for recovery)
- **Response Payload (`OptimizerSolveResult`):**
  - Full stage metrics, solver status, scheduled counts, assignment phases, and embedded Phase 07 `CheckerReport`.

---

## 5. Next Steps

With Gate G2 Phase 08 fully completed and verified, proceed to **Phase 09: Monthly Allocation and Weekly Reconciliation**, implementing the 30-day macro allocation model and reconciliation against 7-day operational schedules per Blueprint Section 27.
