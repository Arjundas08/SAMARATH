"""
Phase 09 Test Suite:
Monthly Allocation and Weekly Reconciliation (Two-Horizon Contract).
Tests Blueprint Sections 20-21, 23, 38:
1. test_monthly_allocation_aggregate_provisional
2. test_ample_aggregate_hours_vs_impossible_detailed_window_raises_reconciliation
3. test_weekly_move_within_permitted_parent_bounds_needs_no_amendment
4. test_cross_week_move_requires_amendment_blocks_approval
5. test_emergency_intake_surfaced_as_exception
6. test_reconciliation_controlled_amendment_creates_immutable_lineage
7. test_monthly_reconciliation_api_endpoints
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.enums import (
    CriticalityTier,
    DepartmentType,
    MonthlyPlanStatus,
    VarianceType,
    ReconciliationStatus,
    AllocationReasonCode,
    WeekValidationStatus,
    ApprovalEligibility,
    ResourceType,
)
from app.schemas.task import Task, ResourceRequirement
from app.schemas.snapshot import Snapshot, LockedCommitment
from app.schemas.monthly import (
    WeeklyQuotaBudget,
    MonthlyAllocationRequest,
    MonthlyAllocationPlan,
    ResolveReconciliationRequest,
)
from app.engine.monthly_allocator import MonthlyAllocator
from app.domain.reconciliation import (
    ReconciliationStore,
    WeeklyReconciliationService,
)


@pytest.fixture(autouse=True)
def clean_store():
    """Clear in-memory store before each test."""
    ReconciliationStore.clear()
    yield
    ReconciliationStore.clear()


def _build_synthetic_monthly_snapshot() -> Snapshot:
    """Builds a realistic synthetic snapshot with tasks across departments, deadlines, and dependencies."""
    now = datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    tasks = []

    # 1. Mandatory tasks with due weeks
    # Task 1: Due Week 1 (Oct 07)
    tasks.append(
        Task(
            task_id=uuid4(),
            business_key="TASK-MAND-W1",
            department=DepartmentType.ENGINEERING,
            sub_department="P-WAY",
            work_type="POINT_MACHINE",
            description="Critical Point Machine Replacement",
            station_from="ALP",
            station_to="BRV",
            track_segment_id="SEC-01-UP",
            chainage_start_km=5.0,
            chainage_end_km=8.0,
            duration_minutes=180,
            setup_buffer_minutes=15,
            restoration_buffer_minutes=15,
            total_block_minutes=210,
            criticality=CriticalityTier.TIER_1_MANDATORY,
            deadline_utc=now + timedelta(days=5),
            required_resources=[
                ResourceRequirement(resource_type=ResourceType.CREW, resource_id="CREW-ENG-01", quantity=1)
            ],
        )
    )
    # Task 2: Due Week 2 (Oct 14)
    tasks.append(
        Task(
            task_id=uuid4(),
            business_key="TASK-MAND-W2",
            department=DepartmentType.ELECTRICAL,
            sub_department="OHE",
            work_type="WIRING",
            description="OHE Catenary Wire Renewal",
            station_from="BRV",
            station_to="CHR",
            track_segment_id="SEC-02-UP",
            chainage_start_km=25.0,
            chainage_end_km=30.0,
            duration_minutes=240,
            setup_buffer_minutes=15,
            restoration_buffer_minutes=15,
            total_block_minutes=270,
            criticality=CriticalityTier.TIER_1_MANDATORY,
            deadline_utc=now + timedelta(days=12),
            required_resources=[
                ResourceRequirement(resource_type=ResourceType.MACHINE, resource_id="TOWER-WAGON-01", quantity=1),
                ResourceRequirement(resource_type=ResourceType.CREW, resource_id="CREW-TRD-01", quantity=1),
            ],
        )
    )
    # Task 3: Due Week 4 (Oct 28)
    tasks.append(
        Task(
            task_id=uuid4(),
            business_key="TASK-MAND-W4",
            department=DepartmentType.SIGNALLING,
            sub_department="SIGNALLING",
            work_type="AXLE_COUNTER",
            description="Axle Counter Sensor Calibration",
            station_from="CHR",
            station_to="DEL",
            track_segment_id="SEC-03-UP",
            chainage_start_km=50.0,
            chainage_end_km=52.0,
            duration_minutes=120,
            setup_buffer_minutes=15,
            restoration_buffer_minutes=15,
            total_block_minutes=150,
            criticality=CriticalityTier.TIER_1_MANDATORY,
            deadline_utc=now + timedelta(days=26),
            required_resources=[
                ResourceRequirement(resource_type=ResourceType.CREW, resource_id="CREW-SIG-01", quantity=1)
            ],
        )
    )

    # 2. Predecessor dependency pair: Predecessor (P) and Successor (S)
    p_id = uuid4()
    tasks.append(
        Task(
            task_id=p_id,
            business_key="TASK-PRED-01",
            department=DepartmentType.ENGINEERING,
            sub_department="P-WAY",
            work_type="BCM",
            description="Ballast Cleaning Machine Run",
            station_from="DEL",
            station_to="ECH",
            track_segment_id="SEC-04-UP",
            chainage_start_km=75.0,
            chainage_end_km=80.0,
            duration_minutes=300,
            setup_buffer_minutes=30,
            restoration_buffer_minutes=30,
            total_block_minutes=360,
            criticality=CriticalityTier.TIER_2_SPEED_RESTRICTION,
            deadline_utc=now + timedelta(days=20),
            required_resources=[
                ResourceRequirement(resource_type=ResourceType.MACHINE, resource_id="BCM-01", quantity=1)
            ],
        )
    )
    tasks.append(
        Task(
            task_id=uuid4(),
            business_key="TASK-SUCC-01",
            department=DepartmentType.ENGINEERING,
            sub_department="P-WAY",
            work_type="TAMPING",
            description="Post-BCM Continuous Track Tamping",
            station_from="DEL",
            station_to="ECH",
            track_segment_id="SEC-04-UP",
            chainage_start_km=75.0,
            chainage_end_km=80.0,
            duration_minutes=240,
            setup_buffer_minutes=15,
            restoration_buffer_minutes=15,
            total_block_minutes=270,
            criticality=CriticalityTier.TIER_2_SPEED_RESTRICTION,
            deadline_utc=now + timedelta(days=25),
            dependencies=[str(p_id)],
            required_resources=[
                ResourceRequirement(resource_type=ResourceType.MACHINE, resource_id="CSM-01", quantity=1)
            ],
        )
    )

    # 3. Conditional task (requires Girder delivery)
    tasks.append(
        Task(
            task_id=uuid4(),
            business_key="TASK-COND-01",
            department=DepartmentType.ENGINEERING,
            sub_department="WORKS",
            work_type="BRIDGE",
            description="Bridge Steel Girder Rehabilitation",
            station_from="ECH",
            station_to="FOX",
            track_segment_id="SEC-05-UP",
            chainage_start_km=105.0,
            chainage_end_km=108.0,
            duration_minutes=360,
            setup_buffer_minutes=30,
            restoration_buffer_minutes=30,
            total_block_minutes=420,
            criticality=CriticalityTier.TIER_2_SPEED_RESTRICTION,
            earliest_start_date=now + timedelta(days=8),  # Release in Week 2
            deadline_utc=now + timedelta(days=28),
            required_resources=[
                ResourceRequirement(resource_type=ResourceType.CREW, resource_id="CREW-ENG-01", quantity=1)
            ],
        )
    )

    return Snapshot(
        snapshot_id=uuid4(),
        corridor_code="VKC",
        snapshot_hash="hash-synthetic-monthly-001",
        horizon_start_utc=now,
        horizon_end_utc=now + timedelta(days=28),
        created_at_utc=now,
        tasks=tasks,
        locked_commitments=[],
    )


def test_monthly_allocation_aggregate_provisional():
    """
    Blueprint 20: Monthly allocator maps tasks to calendar weeks under due-week,
    precedence, and resource budgets. Output is ALLOCATED_PROVISIONAL.
    """
    snapshot = _build_synthetic_monthly_snapshot()
    allocator = MonthlyAllocator(snapshot=snapshot)
    plan = allocator.allocate()

    # 1. Output status and mandatory provisional disclosure
    assert plan.status == MonthlyPlanStatus.ALLOCATED_PROVISIONAL
    assert "ALLOCATED_PROVISIONAL" in plan.provisional_notice
    assert "minute-level feasibility" in plan.provisional_notice

    # 2. Check 4 weekly quota budgets
    assert len(plan.weekly_budgets) == 4
    for b in plan.weekly_budgets:
        assert b.max_track_possession_hours == 35.0
        assert "BCM-01" in b.max_machine_hours

    # 3. Mandatory due-week coverage
    alloc_map = {a.task_number: a for a in plan.allocations}
    assert alloc_map["TASK-MAND-W1"].allocated_week == 1  # Due week 1
    assert alloc_map["TASK-MAND-W2"].allocated_week in (1, 2)  # Due week 2
    assert alloc_map["TASK-MAND-W4"].allocated_week in (1, 2, 3, 4)  # Due week 4

    # 4. Precedence dependency: Week(PRED) <= Week(SUCC)
    pred_week = alloc_map["TASK-PRED-01"].allocated_week
    succ_week = alloc_map["TASK-SUCC-01"].allocated_week
    assert pred_week is not None and succ_week is not None
    assert pred_week <= succ_week

    # 5. Conditional task properties preserved
    cond_alloc = alloc_map["TASK-COND-01"]
    assert cond_alloc.is_conditional is True
    assert cond_alloc.prerequisite_owner == "TRD-SECR"
    assert cond_alloc.allocated_week >= 2  # Earliest start was Week 2

    # 6. Detailed validation coverage initialized to UNVALIDATED
    for w in range(1, 5):
        assert plan.metrics.detailed_validation_coverage[w] == WeekValidationStatus.UNVALIDATED

    # 7. Mandatory metrics
    assert plan.metrics.mandatory_coverage_pct == 100.0
    assert plan.metrics.conditional_tasks_count >= 1


def test_ample_aggregate_hours_vs_impossible_detailed_window_raises_reconciliation():
    """
    Phase 09 Acceptance: A month with ample aggregate hours but impossible detailed
    windows raises a ReconciliationCase and blocks programme approval.
    """
    snapshot = _build_synthetic_monthly_snapshot()
    allocator = MonthlyAllocator(snapshot=snapshot)
    parent_plan = allocator.allocate()
    ReconciliationStore.save_plan(parent_plan)

    recon_service = WeeklyReconciliationService(parent_plan)

    # Simulate detailed weekly solver failure for Week 1 (e.g. tight train-headway clash)
    cases, eligibility = recon_service.reconcile_weekly_schedule(
        child_weekly_plan_id="PLAN-WEEK-01-FAIL",
        target_week_index=1,
        scheduled_task_ids=[],
        total_duration_minutes=0,
        is_solver_feasible=False,
        solver_error_msg="Time-distance clash: No available 180min window between express train paths",
    )

    assert len(cases) == 1
    assert cases[0].variance_type == VarianceType.FEASIBILITY_DISCREPANCY
    assert cases[0].resolution_status == ReconciliationStatus.PENDING
    assert eligibility == ApprovalEligibility.BLOCKED_RECONCILIATION_REQUIRED


def test_weekly_move_within_permitted_parent_bounds_needs_no_amendment():
    """
    Blueprint 21: Within an allocated week, changes in exact start time or package
    choice require NO amendment. Approval eligibility remains ELIGIBLE.
    """
    snapshot = _build_synthetic_monthly_snapshot()
    allocator = MonthlyAllocator(snapshot=snapshot)
    parent_plan = allocator.allocate()
    ReconciliationStore.save_plan(parent_plan)

    alloc_map = {a.task_id: a for a in parent_plan.allocations}
    w1_tasks = [a.task_id for a in parent_plan.allocations if a.allocated_week == 1]

    recon_service = WeeklyReconciliationService(parent_plan)

    # Weekly schedule places exactly the tasks allocated to Week 1
    total_mins = sum(alloc_map[tid].duration_minutes for tid in w1_tasks)
    cases, eligibility = recon_service.reconcile_weekly_schedule(
        child_weekly_plan_id="PLAN-WEEK-01-OK",
        target_week_index=1,
        scheduled_task_ids=w1_tasks,
        total_duration_minutes=total_mins,
        is_solver_feasible=True,
    )

    assert len(cases) == 0
    assert eligibility == ApprovalEligibility.ELIGIBLE


def test_cross_week_move_requires_amendment_blocks_approval():
    """
    Blueprint 21 & Phase 09 Acceptance: Moving a task across calendar weeks
    requires an amendment and blocks weekly programme approval.
    """
    snapshot = _build_synthetic_monthly_snapshot()
    allocator = MonthlyAllocator(snapshot=snapshot)
    parent_plan = allocator.allocate()
    ReconciliationStore.save_plan(parent_plan)

    alloc_map = {a.task_id: a for a in parent_plan.allocations}
    # Pick a task allocated to Week 2 and schedule it in Week 1
    w2_tasks = [a.task_id for a in parent_plan.allocations if a.allocated_week == 2]
    assert len(w2_tasks) > 0
    moved_task_id = w2_tasks[0]

    w1_tasks = [a.task_id for a in parent_plan.allocations if a.allocated_week == 1]
    # Add moved task to Week 1 schedule
    w1_scheduled = w1_tasks + [moved_task_id]

    recon_service = WeeklyReconciliationService(parent_plan)
    cases, eligibility = recon_service.reconcile_weekly_schedule(
        child_weekly_plan_id="PLAN-WEEK-01-CROSS-MOVE",
        target_week_index=1,
        scheduled_task_ids=w1_scheduled,
        total_duration_minutes=500,
        is_solver_feasible=True,
    )

    cross_cases = [c for c in cases if c.variance_type == VarianceType.CROSS_WEEK_MOVE]
    assert len(cross_cases) == 1
    assert cross_cases[0].implicated_task_ids == [moved_task_id]
    assert cross_cases[0].parent_allocated_week == 2
    assert cross_cases[0].weekly_attempted_week == 1
    assert eligibility == ApprovalEligibility.BLOCKED_RECONCILIATION_REQUIRED


def test_emergency_intake_surfaced_as_exception():
    """
    Blueprint 21: Emergency intake absent from parent is explicitly labelled
    an exception (EMERGENCY_INTAKE) and not silently backfilled.
    """
    snapshot = _build_synthetic_monthly_snapshot()
    allocator = MonthlyAllocator(snapshot=snapshot)
    parent_plan = allocator.allocate()
    ReconciliationStore.save_plan(parent_plan)

    recon_service = WeeklyReconciliationService(parent_plan)
    emergency_tid = "TASK-EMERGENCY-FRACTURE-01"

    cases, eligibility = recon_service.reconcile_weekly_schedule(
        child_weekly_plan_id="PLAN-WEEK-01-EMERGENCY",
        target_week_index=1,
        scheduled_task_ids=[emergency_tid],
        total_duration_minutes=120,
        is_solver_feasible=True,
    )

    emergency_cases = [c for c in cases if c.variance_type == VarianceType.EMERGENCY_INTAKE]
    assert len(emergency_cases) == 1
    assert emergency_cases[0].implicated_task_ids == [emergency_tid]
    assert emergency_cases[0].parent_allocated_week is None
    assert eligibility == ApprovalEligibility.BLOCKED_RECONCILIATION_REQUIRED


def test_reconciliation_controlled_amendment_creates_immutable_lineage():
    """
    Controlled amendment workflow:
    - Reviewer approves amendment.
    - Parent v1 is marked SUPERSEDED; new parent v2 is created with AMENDED status.
    - Task allocation is amended in v2.
    - Child weekly plan is re-checked against v2 and achieves ELIGIBLE.
    """
    snapshot = _build_synthetic_monthly_snapshot()
    allocator = MonthlyAllocator(snapshot=snapshot, version_index=1)
    parent_v1 = allocator.allocate()
    ReconciliationStore.save_plan(parent_v1)

    # Find all tasks allocated to Week 1 and one task allocated to Week 2
    w1_all_tasks = [a.task_id for a in parent_v1.allocations if a.allocated_week == 1]
    w2_task = next(a.task_id for a in parent_v1.allocations if a.allocated_week == 2)
    scheduled_tasks = w1_all_tasks + [w2_task]
    total_mins = sum(a.duration_minutes for a in parent_v1.allocations if a.task_id in scheduled_tasks)

    recon_service = WeeklyReconciliationService(parent_v1)
    cases, eligibility = recon_service.reconcile_weekly_schedule(
        child_weekly_plan_id="PLAN-WEEK-01-AMEND-DEMO",
        target_week_index=1,
        scheduled_task_ids=scheduled_tasks,
        total_duration_minutes=total_mins,
        is_solver_feasible=True,
    )
    assert eligibility == ApprovalEligibility.BLOCKED_RECONCILIATION_REQUIRED
    case_to_resolve = [c for c in cases if c.variance_type == VarianceType.CROSS_WEEK_MOVE][0]

    # Resolve case: Authorized reviewer approves amendment
    resolve_req = ResolveReconciliationRequest(
        resolution=ReconciliationStatus.APPROVED_AMENDMENT,
        reviewer_role="OPERATING_REVIEWER",
        resolution_notes="Authorized early execution of catenary wire renewal during joint bridge block.",
    )
    updated_case, parent_v2 = WeeklyReconciliationService.resolve_case(
        case_id=case_to_resolve.case_id,
        request=resolve_req,
        resolved_by="sr-dom-central",
    )

    # Verify immutable parent lineage
    assert updated_case.resolution_status == ReconciliationStatus.APPROVED_AMENDMENT
    assert parent_v2 is not None
    assert parent_v2.version_index == 2
    assert parent_v2.status == MonthlyPlanStatus.AMENDED
    assert parent_v1.status == MonthlyPlanStatus.SUPERSEDED

    # Verify task in v2 is now allocated to Week 1
    v2_alloc_map = {a.task_id: a for a in parent_v2.allocations}
    assert v2_alloc_map[w2_task].allocated_week == 1

    # Re-evaluate weekly schedule against new parent v2
    recon_service_v2 = WeeklyReconciliationService(parent_v2)
    new_cases, new_eligibility = recon_service_v2.reconcile_weekly_schedule(
        child_weekly_plan_id="PLAN-WEEK-01-AMEND-DEMO",
        target_week_index=1,
        scheduled_task_ids=scheduled_tasks,
        total_duration_minutes=total_mins,
        is_solver_feasible=True,
    )
    assert len(new_cases) == 0
    assert new_eligibility == ApprovalEligibility.ELIGIBLE


def test_monthly_reconciliation_api_endpoints(client: TestClient):
    """
    Validates REST API endpoints for Monthly Allocation and Weekly Reconciliation.
    """
    # 1. Allocate Monthly Plan
    resp_alloc = client.post("/api/v1/planning/monthly/allocate", json={
        "corridor_code": "VKC",
        "planning_month": "2026-10",
        "time_limit_seconds": 10.0,
    })
    assert resp_alloc.status_code == 200
    plan_data = resp_alloc.json()
    assert plan_data["status"] == "ALLOCATED_PROVISIONAL"
    assert len(plan_data["allocations"]) > 0
    assert plan_data["metrics"]["mandatory_coverage_pct"] == 100.0
    monthly_plan_id = plan_data["monthly_plan_id"]

    # 2. Get Monthly Plan by ID
    resp_get = client.get(f"/api/v1/planning/monthly/plans/{monthly_plan_id}")
    assert resp_get.status_code == 200
    assert resp_get.json()["monthly_plan_id"] == monthly_plan_id

    # 3. List Monthly Plans
    resp_list = client.get("/api/v1/planning/monthly/plans?corridor_code=VKC")
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 1

    # 4. Run Weekly CP-SAT Solver with Parent Monthly Plan Link
    resp_solve = client.post("/api/v1/planning/optimizer/solve", json={
        "corridor_code": "VKC",
        "profile": "PROGRAMME_IMPROVEMENT",
        "time_limit_seconds": 15.0,
        "lattice_step_minutes": 60,
        "max_candidates": 10000,
        "parent_monthly_plan_id": monthly_plan_id,
        "target_week_index": 1,
    })
    assert resp_solve.status_code == 200
    solve_data = resp_solve.json()
    assert solve_data["solver_status"] in ("OPTIMAL", "FEASIBLE", "TIME_LIMIT")
    assert solve_data["parent_monthly_plan_id"] == monthly_plan_id
    assert "approval_eligibility" in solve_data

    # 5. List Reconciliation Cases
    resp_cases = client.get("/api/v1/planning/reconciliation/cases")
    assert resp_cases.status_code == 200
    cases_list = resp_cases.json()

    # If any cases exist, test resolving the first case
    if cases_list:
        first_case_id = cases_list[0]["case_id"]
        resp_resolve = client.post(
            f"/api/v1/planning/reconciliation/{first_case_id}/resolve",
            json={
                "resolution": "APPROVED_AMENDMENT",
                "reviewer_role": "OPERATING_REVIEWER",
                "resolution_notes": "Approved amendment via API integration test.",
            }
        )
        assert resp_resolve.status_code == 200
        resolved_data = resp_resolve.json()
        assert resolved_data["case"]["resolution_status"] == "APPROVED_AMENDMENT"
        assert resolved_data["amended_parent_plan"] is not None
        assert resolved_data["amended_parent_plan"]["status"] == "AMENDED"
