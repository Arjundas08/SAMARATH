# Phase 09 Completion Report: Monthly Allocation and Weekly Reconciliation (Two-Horizon Contract)

**Phase ID:** PHASE-09  
**Phase Title:** Monthly Allocation and Weekly Reconciliation (Two-Horizon Contract)  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 09 establishes the formal two-horizon planning contract linking 30-day tactical monthly allocations to 7-day operational weekly solves with controlled reconciliation and immutable version lineage per Blueprint Sections 20, 21, 23, and 38.

### Key Invariants Enforced:
1. **Provisional Monthly Feasibility:** Tactical monthly plan allocations are stamped `ALLOCATED_PROVISIONAL`. Aggregate weekly quota feasibility does NOT guarantee minute-level physical feasibility, truthfully reflecting real-world railway operations.
2. **Approval Eligibility Gate:** A child weekly plan containing unresolved reconciliation variances is strictly flagged `approval_eligibility = BLOCKED_RECONCILIATION_REQUIRED` and cannot be approved by railway leadership until resolved.
3. **Controlled Amendment & Immutable Lineage:** Authorized resolution of variances creates an amended parent plan version ($V \to V+1$) with status `AMENDED`, while the previous parent version is marked `SUPERSEDED`. Historical plan versions are never mutated in-place.
4. **Intra-Week Movement vs. Cross-Week Shifts:** Rescheduling within the designated week boundaries does not require parent amendment, whereas cross-week shifts, capacity overruns, and emergency work intake trigger formal reconciliation cases.

---

## 2. Architecture & Implementation

### 2.1 Domain Enums and Schemas (`backend/app/schemas/enums.py`, `backend/app/schemas/monthly.py`)
- Added domain enums:
  - `ApprovalEligibility`: `ELIGIBLE`, `BLOCKED_RECONCILIATION_REQUIRED`, `BLOCKED_FEASIBILITY_FAILURE`, `BLOCKED_UNAUTHORIZED`.
  - `MonthlyPlanStatus`: `DRAFT`, `ALLOCATED_PROVISIONAL`, `AMENDED`, `SUPERSEDED`, `ARCHIVED`.
  - `VarianceType`: `CROSS_WEEK_MOVE`, `EMERGENCY_INTAKE`, `CAPACITY_OVERRUN`, `FEASIBILITY_DISCREPANCY`, `DEFERRED_TASK`.
  - `ReconciliationStatus`: `PENDING_REVIEW`, `APPROVED_AMENDMENT`, `REJECTED_REVERT_REQUIRED`, `AUTO_RESOLVED`.
  - `AllocationReasonCode`: `DUE_DATE_STATUTORY`, `RESOURCE_OPTIMIZED`, `CROSS_DEPT_BUNDLE`, `CAPACITY_SMOOTHED`.
- Added Pydantic schemas:
  - `WeeklyQuotaBudget`: Weekly duration caps (minutes), track possession limits, machine quotas (BCM, CSM, Tower Wagon).
  - `MonthlyTaskAllocation`: Detailed allocation record per task with allocated week, rationale, and validation status.
  - `MonthlyAllocationPlan`: Full 4-week tactical plan with version index, line of parentage, department breakdown, and audit metadata.
  - `ReconciliationCase`: Structured record of variance between weekly operational schedule and parent monthly plan.
  - `MonthlyAllocationRequest` & `ResolveReconciliationRequest`: Typed API payloads.

### 2.2 Monthly Allocator Engine (`backend/app/engine/monthly_allocator.py`)
- Uses Google OR-Tools CP-SAT discrete integer programming across 4 calendar weeks.
- Decision variables: $y[t, w] \in \{0, 1\}$ representing assignment of task $t$ to calendar week $w \in \{1, 2, 3, 4\}$.
- Constraints:
  - *Single Assignment:* $\sum_{w=1}^4 y[t, w] \le 1$.
  - *Mandatory Statutory Coverage:* $\sum_{w=1}^{\text{due\_week}(t)} y[t, w] == 1$ for all Tier-1 Mandatory tasks.
  - *Predecessor Dependency Ordering:* $w_{\text{pred}} \le w_{\text{succ}}$ for prerequisite tasks.
  - *Weekly Quotas:* Total track possession minutes and specialized machine quotas (BCM, CSM, Tower Wagon) per week.
- Objectives: Lexicographic multi-stage optimization maximizing priority task completion, minimizing due-week delay penalties, and maximizing cross-departmental corridor bundling.
- Stamped with `status = ALLOCATED_PROVISIONAL`.

### 2.3 Weekly Reconciliation Service (`backend/app/domain/reconciliation.py`)
- Independent reconciliation domain service comparing child weekly solves against parent monthly plans:
  - Identifies all 5 variance types (`CROSS_WEEK_MOVE`, `EMERGENCY_INTAKE`, `CAPACITY_OVERRUN`, `FEASIBILITY_DISCREPANCY`, `DEFERRED_TASK`).
  - Correctly permits intra-week adjustments without creating blocking cases.
  - Stalls child plan approval when any case is pending review.
  - Executes controlled amendments: increments parent version ($V+1$), updates task allocations, marks prior parent version `SUPERSEDED`, and clears reconciliation cases for re-evaluation.

### 2.4 Weekly CP-SAT Solver Integration (`backend/app/engine/cp_sat_solver.py`)
- Extended `CPSatWeeklyOptimizer.solve()` with `parent_monthly_plan_id` and `target_week_index`.
- If parent monthly plan is specified, automatically invokes `WeeklyReconciliationService` upon solve completion.
- Stamps solver output with `parent_monthly_plan_id`, `target_week_index`, `reconciliation_cases`, and calculated `approval_eligibility`.

### 2.5 REST API Endpoints (`backend/app/api/v1/planning.py`)
- `POST /api/v1/planning/monthly/allocate`: Generates 4-week tactical monthly plan via CP-SAT.
- `GET /api/v1/planning/monthly/plans`: Lists all monthly plans for corridor.
- `GET /api/v1/planning/monthly/plans/{plan_id}`: Retrieves specific monthly plan.
- `GET /api/v1/planning/reconciliation/cases`: Lists reconciliation cases with status and weekly plan filters.
- `POST /api/v1/planning/reconciliation/{case_id}/resolve`: Resolves variance case with audit notes, emitting amended parent plan.

---

## 3. Verification Evidence and Test Results

### 3.1 Test Suite (`backend/tests/test_monthly_reconciliation.py`)
All 7 tests passed:
```
backend\tests\test_monthly_reconciliation.py::test_monthly_allocation_aggregate_provisional PASSED [ 14%]
backend\tests\test_monthly_reconciliation.py::test_ample_aggregate_hours_vs_impossible_detailed_window_raises_reconciliation PASSED [ 28%]
backend\tests\test_monthly_reconciliation.py::test_weekly_move_within_permitted_parent_bounds_needs_no_amendment PASSED [ 42%]
backend\tests\test_monthly_reconciliation.py::test_cross_week_move_requires_amendment_blocks_approval PASSED [ 57%]
backend\tests\test_monthly_reconciliation.py::test_emergency_intake_surfaced_as_exception PASSED [ 71%]
backend\tests\test_monthly_reconciliation.py::test_reconciliation_controlled_amendment_creates_immutable_lineage PASSED [ 85%]
backend\tests\test_monthly_reconciliation.py::test_monthly_reconciliation_api_endpoints PASSED [100%]

======================= 7 passed, 73 warnings in 16.80s =======================
```

### 3.2 Acceptance Criteria Verification
| Requirement | Status | Verification Detail |
|---|---|---|
| Monthly output strictly marked ALLOCATED_PROVISIONAL | PASS | Verified in `test_monthly_allocation_aggregate_provisional`. |
| Aggregate vs minute-level discrepancy raises reconciliation | PASS | Verified in `test_ample_aggregate_hours_vs_impossible_detailed_window_raises_reconciliation`. |
| Permitted intra-week shifts require no amendment | PASS | Verified in `test_weekly_move_within_permitted_parent_bounds_needs_no_amendment`. |
| Cross-week move requires amendment & blocks approval | PASS | Verified in `test_cross_week_move_requires_amendment_blocks_approval`. |
| Emergency intake surfaced as exception | PASS | Verified in `test_emergency_intake_surfaced_as_exception`. |
| Controlled amendment creates immutable parent lineage ($V \to V+1$) | PASS | Verified in `test_reconciliation_controlled_amendment_creates_immutable_lineage`. |
| Monthly and Reconciliation REST APIs verified | PASS | Verified in `test_monthly_reconciliation_api_endpoints`. |
