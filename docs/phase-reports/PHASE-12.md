# Phase 12 Completion Report: Evidence-Backed Why, Why-Not Diagnostics and Bounded Repair Engine

**Phase ID:** PHASE-12  
**Phase Title:** Evidence-Backed Why, Why-Not Diagnostics and Bounded Repair Engine  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 12 delivers the deterministic explainability and bounded counterfactual repair engine for SAMARATH per Blueprint Sections 24, 25, 31, and 32. Indian Railways operational officers (CPTM, CFTM, Sr.DEN, Chief Controllers) require absolute mathematical rigor, transparency, and regulatory truthfulness before ratifying or amending track possession plans. Phase 12 replaces opaque "black-box" optimization with formal evidence-backed proofs, truthful solver timeout disclosures, and bounded repair workflows that never compromise track safety or electrical isolation.

### Key Invariants Delivered & Verified:
1. **Zero Manufactured LLM Text:**
   - All explanations, reason codes, and causal narratives derive strictly from active database state, timetable headway analysis, resource calendars, and deterministic readiness evaluations.
   - No hallucinated justifications or arbitrary LLM text generation.
2. **Typed Reason Code Catalogue (Section 24):**
   - Distinct, mutually exclusive diagnosis categories:
     - `INPUT_BLOCKED`: Prerequisite field readiness, certificates, or mandatory approvals incomplete.
     - `CANDIDATE_REJECTED`: Window candidates physically rejected due to track geometry or temporal bounds.
     - `NO_CANDIDATE_IN_DOMAIN`: No valid operational window exists within corridor timetable or rules.
     - `MODEL_INFEASIBLE`: CP-SAT mathematical model proved no non-conflicting placement is possible.
     - `FEASIBLE_BUT_UNSELECTED`: Placement physically possible, but lower objective score than competing work.
     - `SEARCH_INCOMPLETE`: Solver time budget or memory limit elapsed before optimality was proven.
3. **Truthfulness Invariant (Section 25):**
   - Solver timeouts are truthfully disclosed as `SEARCH_INCOMPLETE` with `ProofStatus.INCONCLUSIVE`.
   - The platform **never** manufactures a physical or operational impossibility proof when an algorithm merely runs out of computational time.
4. **Allowlisted Bounded Repair Engine (Section 31):**
   - Strictly restricted to 4 permit types:
     1. `MOVE_OPTIONAL_UNLOCKED_WORK`: Shift non-locked, lower-criticality maintenance to adjacent low-density periods.
     2. `SUBSTITUTE_RESOURCE`: Swap uncertified or bottleneck gangs/machines with certified alternates.
     3. `ALTERNATE_PACKAGE_WINDOW`: Select an alternative package window or extend time budget.
     4. `REQUEST_PARENT_WEEK_AMENDMENT`: Request monthly tactical authority amendment from CPTM.
   - **Never** relaxes safety rules, required OHE electrical isolations, prohibited compatibility constraints, or mandatory operational locks.
5. **Non-Publishable Trial Simulations (Section 31):**
   - Interactive trial repairs are strictly flagged as `is_publishable = False`.
   - Trial scenarios run against the independent Phase 07 Feasibility Checker and cannot be published or ratified directly.
6. **Optimistic Concurrency & ETag Preconditions (Section 32):**
   - Permanent repairs check plan version (`expected_plan_version`) to prevent lost updates or concurrent race conditions. Mismatches return HTTP 412 (Precondition Failed).
   - Accepted repairs schedule a fresh, clean solve job through `JobService` rather than directly mutating finalized plan versions.

---

## 2. Architecture & Implementation Details

### 2.1 Domain Schemas (`backend/app/schemas/enums.py`, `backend/app/schemas/reason.py`, `frontend/src/types/api.ts`)
- **Enums:**
  - `DiagnosticReasonCode`: `INPUT_BLOCKED`, `CANDIDATE_REJECTED`, `NO_CANDIDATE_IN_DOMAIN`, `MODEL_INFEASIBLE`, `FEASIBLE_BUT_UNSELECTED`, `SEARCH_INCOMPLETE`.
  - `ProofStatus`: `PROVEN_CONSTRAINED`, `PROVEN_SUBOPTIMAL`, `EMPIRICALLY_CONFLICTING`, `INCONCLUSIVE`.
  - `RepairActionType`: `MOVE_OPTIONAL_UNLOCKED_WORK`, `SUBSTITUTE_RESOURCE`, `ALTERNATE_PACKAGE_WINDOW`, `REQUEST_PARENT_WEEK_AMENDMENT`.
  - `RepairFeasibilityStatus`: `VERIFIED_FEASIBLE`, `AWAITING_AUTHORITY`, `INVALID`.
- **Pydantic Models:**
  - `DiagnosticEvidenceFact`: Key-value evidence item with source record IDs, rule versions, and satisfaction flags.
  - `ConflictCore`: Train numbers, conflicting assignment IDs, exhausted resources, and temporal intervals.
  - `CounterfactualComparison`: Alternative candidate window rejection proofs and objective value deltas.
  - `RepairOption`: Allowlisted action description, required role, feasibility status, and estimated gain.
  - `WhyNotDiagnostic`: Complete diagnosis for unplaced maintenance demands.
  - `WhySelectedDiagnostic`: Selection proofs, priority score contributions, and counterfactuals for scheduled assignments.
  - `TrialRepairRequest`, `TrialRepairResult`: Non-publishable simulation payload and outcome.
  - `ApplyRepairRequest`, `ApplyRepairResponse`: Concurrency-guarded repair application payload and response.

### 2.2 Diagnostics Engine (`backend/app/engine/diagnostics_engine.py`)
- `explain_unplaced_task(db, plan_id, task_id)`:
  - Validates plan and task existence.
  - Checks if already scheduled (`FEASIBLE_BUT_UNSELECTED`).
  - Checks solver execution status: handles `TIMED_OUT` as `SEARCH_INCOMPLETE` with `INCONCLUSIVE`.
  - Evaluates 9-dimension operational readiness: detects missing fleet certifications as `INPUT_BLOCKED`.
  - Performs timetable headway and spatial overlap inspection against train paths in `train_timetable.json`.
  - Identifies bottleneck machinery and overlapping locked possessions.
  - Computes allowlisted repairs with required officer roles.
- `explain_selected_assignment(db, plan_id, assignment_id)`:
  - Synthesizes admissibility invariants (zero headway violations, speed restriction buffer compliance, machine continuity).
  - Calculates objective function score contributions (criticality weight, possession duration).
  - Evaluates counterfactual alternative windows and explains why the chosen window maximizes network utility.
- `simulate_trial_repair(db, request)`:
  - Generates hypothetical assignment for unplaced work with preparation/execution/restoration phases.
  - Evaluates the proposed plan against `IndependentFeasibilityChecker` (Phase 07 Oracle).
  - Returns `is_publishable=False`, checker verdict, objective delta, and remaining conflicts.
- `apply_repair(db, request, user)`:
  - Enforces ETag / plan version precondition.
  - Modifies task preferred windows and registers audit log.
  - Enqueues fresh background solve job through `JobService`.

### 2.3 REST Endpoints (`backend/app/api/v1/diagnostics.py`)
- `GET /api/v1/planning/diagnostics/why-not/{plan_id}/{task_id}`: Why-Not evidence for unplaced tasks.
- `GET /api/v1/planning/diagnostics/why/{plan_id}/{assignment_id}`: Why-Selected proofs for scheduled assignments.
- `POST /api/v1/planning/diagnostics/repairs/trial`: Bounded trial simulation endpoint (`is_publishable=False`).
- `POST /api/v1/planning/diagnostics/repairs/apply`: Authorized repair application with HTTP 412 precondition enforcement.

### 2.4 Frontend Evidence Drawer Integration (`frontend/src/components/common/EvidenceDrawer.tsx`, `PlanningView.tsx`)
- Contextual tabs:
  - **Why / Diagnostics:** Live Why-Not diagnostic for unplaced work with reason badge, proof status, evidence facts, and allowlisted repairs; Why-Selected proofs for scheduled assignments with priority contribution and counterfactual comparisons.
  - **Readiness & Fleet:** 9-dimension readiness audit cards with certification references.
  - **Safety & PTW:** Execution phase topology, traction power elementary section requirements, and Phase 07 Feasibility Oracle badge.
- Interactive Repair Operations:
  - "Simulate Trial": Dispatches bounded simulation, renders oracle verdict and objective gain with amber "Strictly Non-Publishable" banner.
  - "Apply Repair": Submits authorized revision, triggers fresh background solve, and automatically reloads the workbench canvas.

---

## 3. Verification & Test Results

### 3.1 Phase 12 Integration Test Suite (`backend/tests/test_phase12_diagnostics.py`)
| Test Case | Invariant / Blueprint Section | Result |
| :--- | :--- | :--- |
| `test_why_not_diagnostic_unplaced_task_facts` | Blueprint Sec 24: Typed reason code, facts, allowlisted repairs | **PASSED** |
| `test_why_selected_diagnostic_scheduled_assignment` | Blueprint Sec 24: Admissibility invariants, objective delta, counterfactuals | **PASSED** |
| `test_trial_repair_simulation_non_publishable` | Blueprint Sec 31: `is_publishable=False`, independent checker execution | **PASSED** |
| `test_apply_repair_with_precondition_concurrency` | Blueprint Sec 32: Concurrency check, HTTP 412 on stale version | **PASSED** |
| `test_search_incomplete_truthfulness_timeout` | Blueprint Sec 25: Truthful `SEARCH_INCOMPLETE` report on solver timeout | **PASSED** |
| `test_input_blocked_readiness_distinction` | Blueprint Sec 16 & 24: `INPUT_BLOCKED` on missing fleet certification | **PASSED** |
| `test_repair_safety_invariant` | Blueprint Sec 31: Zero relaxation of safety rules or OHE isolation | **PASSED** |

**Phase 12 Suite Summary:** 7 passed in 10.91s (100% pass rate).

### 3.2 Full Backend Regression Suite
- Ran `python -m pytest tests/ -q`.
- **Result:** **86 passed** in 55.61s.
- **Regressions:** **0**.

### 3.3 Frontend Type Validation
- Ran `npx tsc --noEmit` from `frontend/`.
- **Result:** Exit code **0** (0 TypeScript errors).

---

## 4. Acceptance Criteria Verification

- [x] Unscheduled tasks diagnosed with distinct, mutually exclusive reason codes (INPUT_BLOCKED, CANDIDATE_REJECTED, etc.).
- [x] Every diagnostic backed by concrete facts referencing specific data records and timetable headway intervals.
- [x] Solver timeouts truthfully reported as `SEARCH_INCOMPLETE` with `INCONCLUSIVE` proof status.
- [x] Repair options bounded to allowlisted actions (move optional work, substitute resource, alternate window, parent amendment).
- [x] Safety invariants, electrical isolation, and operational locks strictly protected from relaxation.
- [x] Trial simulations marked non-publishable and evaluated against independent feasibility checker.
- [x] Applying repairs guarded by optimistic concurrency (ETag) and generates a fresh, traceable solve job.
- [x] Workbench UI displays diagnostic details and supports interactive trial repair simulation and authorized execution.

---

## 5. Next Steps

With Phase 12 fully delivered, verified, and integrated, the system proceeds immediately to:
- **Phase 13: Event-Driven Stable Replanning & PlanDiff Engine**
  - Blueprint Section 27, 28, and 33.
  - Minimal churn disruption recovery, invariant re-checking, and structured PlanDiff generation.
