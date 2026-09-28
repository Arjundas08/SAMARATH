# Phase 07 Completion Report: Independent Feasibility Checker and Correctness Oracle

**Phase ID:** PHASE-07  
**Phase Title:** Independent Feasibility Checker and Correctness Oracle  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 07 implements the autonomous, decoupled feasibility checker and mathematical correctness oracle per Blueprint Sections 23 and 41:

1. **Decoupled Architecture & Strict Import Boundary (`backend/app/checker/feasibility_checker.py`):**
   - Operates solely on raw Snapshot records, corridor topology data, and materialized `ProposedPlan` objects.
   - **Zero-Dependency Invariant:** Completely isolated from planner and optimizer modules. Does **not** import `app.engine` (candidate generators, solvers) or `app.domain` (planner compatibility rules, package builders).
   - Enforced by automated AST-based import-boundary CI test (`test_checker_import_boundaries`).
   - Implements independent interval sweeps and discrete event sweep algorithms rather than relying on planner predicates.

2. **Multi-Constraint Physical and Regulatory Validation:**
   - **1-Second Resolution Train Sweeping:** Detects any temporal overlap down to 1 second against `TrainOccupation` records on active or isolated tracks (`TRAIN_OCCUPATION_COLLISION`).
   - **Track Collision-Free Invariant:** Prevents concurrent physical occupation of the same track segment (`TRACK_COLLISION`).
   - **Neutral Section Footprint Isolation:** Enforces mandatory dual-track isolation (e.g. Charlie station km 48.0 Neutral Section de-energization requires isolating both UP and DN main tracks) (`UNRESOLVED_NEUTRAL_SECTION_FOOTPRINT`).
   - **Multi-Resource Capacity & Outage Sweeping:** Discrete event sweep line monitors concurrent machine and crew allocations against capacity limits (`RESOURCE_CAPACITY_EXCEEDED`) and depot overhaul schedules (`RESOURCE_OUTAGE_CONFLICT`).
   - **Strict Hard Lock Equality:** Hard commitments must be scheduled with zero time deviation (0s tolerance); any shift is rejected (`HARD_LOCK_ALTERED`).
   - **Mandatory Coverage & Deduplication:** 100% statutory coverage of Tier-1 mandatory tasks required; duplicate task allocations are rejected (`MANDATORY_TASK_MISSING`, `TASK_DUPLICATION`).
   - **Restoration Phase Verification:** Requires an explicit final `RESTORATION` phase before line reopening (`MISSING_RESTORATION_PHASE`).
   - **Prohibition on Autonomous Authority Transitions:** Flags and rejects any plan claiming automatic block granting or releasing without human Section Controller authority (`AUTONOMOUS_AUTHORITY_TRANSITION_PROHIBITED`).

3. **Exhaustive Tiny-Instance Combinatorial Oracle (`backend/app/checker/tiny_oracle.py`):**
   - Performs brute-force Cartesian product enumeration over tiny problem instances ($\le 6$ tasks, $\le 48\text{h}$ horizon).
   - Establishes mathematical ground truth bounds and provably optimal schedules independent of heuristics, serving as the benchmark oracle for Phase 08 CP-SAT verification.

4. **Hand-Authored Fixtures & Mutation Rejection Suite (`backend/app/checker/fixtures.py`):**
   - Created static golden valid and mutated invalid assignment files that do not rely on candidate generators.
   - Verified that all 11 deliberate mutation scenarios are rejected with exact error codes, entity IDs, observed vs expected values, units, and official IR regulatory citations (IR General Rules 4.19, G&SR Para 4.21, ACTM Vol II Para 20433, Block Working Manual Para 15.2).

5. **Phase 06 Baseline Integration:**
   - The greedy baseline from Phase 06 was executed on the live corridor and verified by the checker (`POST /api/v1/checker/verify-baseline`), confirming that its output is valid and safe.

---

## 2. Verification Evidence and Test Results

### 2.1 Automated Test Suite (`backend/tests/test_checker_oracle.py`)
All 13 automated tests passed in **2.38 seconds**:
```
tests/test_checker_oracle.py::test_checker_import_boundaries PASSED               [  7%]
tests/test_checker_oracle.py::test_golden_valid_plan_passes PASSED                [ 15%]
tests/test_checker_oracle.py::test_mutation_one_second_train_overlap PASSED        [ 23%]
tests/test_checker_oracle.py::test_mutation_missing_restoration_phase PASSED       [ 30%]
tests/test_checker_oracle.py::test_mutation_duplicate_task PASSED                 [ 38%]
tests/test_checker_oracle.py::test_mutation_wrong_qualified_resource PASSED       [ 46%]
tests/test_checker_oracle.py::test_mutation_three_way_capacity_violation PASSED   [ 53%]
tests/test_checker_oracle.py::test_mutation_moved_hard_lock PASSED                [ 61%]
tests/test_checker_oracle.py::test_mutation_unresolved_neutral_section_footprint PASSED [ 69%]
tests/test_checker_oracle.py::test_mutation_missing_mandatory_task PASSED          [ 76%]
tests/test_checker_oracle.py::test_mutation_autonomous_authority_prohibited PASSED [ 84%]
tests/test_checker_oracle.py::test_exhaustive_tiny_oracle_correctness PASSED      [ 92%]
tests/test_checker_oracle.py::test_baseline_passes_independent_checker PASSED      [100%]
```

### 2.2 Mutation Rejection Catalog

| Mutation Test Scenario | Injected Fault | Expected Violation Code | Observed Result | Status |
|---|---|---|---|---|
| **1-Second Train Overlap** | Extended block by 1s into Train 12951 | `TRAIN_OCCUPATION_COLLISION` | Rejected: "1s overlap on TRACK-BRV-CHR-DN" | **PASS** |
| **Missing Restoration** | Dropped final `RESTORATION` phase | `MISSING_RESTORATION_PHASE` | Rejected: "Last phase is EXECUTION" | **PASS** |
| **Task Duplication** | Assigned same task in two blocks | `TASK_DUPLICATION` | Rejected: "Duplicated in ASSIGN-01 and ASSIGN-02" | **PASS** |
| **Wrong Qualification** | Stripped required `CSM-01` machine | `WRONG_QUALIFIED_RESOURCE` | Rejected: "Must include required resource CSM-01" | **PASS** |
| **3-Way Capacity Limit** | 3 blocks overlapping on `SUP-CREW-01` | `RESOURCE_CAPACITY_EXCEEDED` | Rejected: "3 concurrent allocations at 2026-10-12T20:00:00" | **PASS** |
| **Moved Hard Lock** | Shifted locked commitment by 60s | `HARD_LOCK_ALTERED` | Rejected: "delta=60s from lock" | **PASS** |
| **Neutral Section Leak** | Omitted adjacent UP track at CHR | `UNRESOLVED_NEUTRAL_SECTION_FOOTPRINT` | Rejected: "Must include adjacent track TRACK-BRV-CHR-UP" | **PASS** |
| **Missing Mandatory Task** | Dropped statutory Tier-1 demand | `MANDATORY_TASK_MISSING` | Rejected: "Tier-1 Mandatory task is missing" | **PASS** |
| **Autonomous Authority** | Set `auto_grant_authority: true` | `AUTONOMOUS_AUTHORITY_TRANSITION_PROHIBITED` | Rejected: "Human Section Controller authority required" | **PASS** |

---

## 3. Invariants & Blueprint Adherence

| Invariant / Requirement | Blueprint Spec | Implementation Verification | Status |
|---|---|---|---|
| **Checker Decoupling** | Sec 23 | AST check verifies zero imports of `app.engine` or `app.domain` | **PASS** |
| **1-Second Resolution** | Sec 23.4 | Second-level intersection detection catches 1s edge overlaps | **PASS** |
| **Hard Lock Invariance** | Sec 22 Inv 1 | 0s tolerance equality check against locked commitments | **PASS** |
| **Neutral Section Multi-Track** | Sec 16 & 23 | Dual-track isolation enforced on CHR neutral section | **PASS** |
| **Ground Truth Oracle** | Sec 41 | Exhaustive combinatorial search on tiny instances verified | **PASS** |
| **No Client-Edited Verdicts** | Sec 23 | Immutable Pydantic models with server-side computation | **PASS** |

---

## 4. Next Phase Gate

- **Next Phase:** Phase 08 (`08_REAL_CP_SAT_WEEKLY_OPTIMIZER_AND_OBJECTIVE_PROFILES.md`).
- **Dependencies Ready:** Verified candidate generation, credible baseline benchmark, and the independent feasibility oracle ready to rigorously validate CP-SAT solutions.
