"""
Phase 14: Calculated Metrics, Fair Comparison & Stress Testing Endpoints.
Blueprint Sections: 26, 37-40.

REST API Router for:
- Versioned plan metrics calculation (interval union occupation, zero-denominator safety).
- Fair comparison (coverage displayed before occupation, unequal coverage warnings).
- Fixed-plan stress testing across 4 declared perturbations (pass count only, not probability).
- Adaptive recovery re-solve experiments.
- Listing versioned declared stress scenarios.
"""
from typing import Optional, List, Dict, Any, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import PlanVersionModel, MaterializedAssignmentModel, SnapshotModel
from app.schemas.metrics_evaluation import (
    CalculatedPlanMetrics,
    FairComparisonResult,
    FairComparisonRequest,
    FixedPlanStressReport,
    AdaptiveStressRecoveryResult,
    StressPerturbation,
)
from app.engine.metrics_calculator import PlanMetricsCalculator
from app.engine.fair_comparison import FairComparisonEngine
from app.engine.stress_testing import StressTestingEngine, DEFAULT_STRESS_SCENARIOS

router = APIRouter(prefix="/evaluation", tags=["Phase 14: Metrics, Fair Comparison & Stress Scenarios"])


async def _load_plan_and_snapshot(db: AsyncSession, plan_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Helper to fetch a plan and its snapshot from database into dict format."""
    # Query plan
    plan_res = await db.execute(select(PlanVersionModel).where(PlanVersionModel.plan_id == plan_id))
    plan_obj = plan_res.scalar_one_or_none()
    if not plan_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan '{plan_id}' not found in database."
        )

    # Query assignments
    asgns_res = await db.execute(
        select(MaterializedAssignmentModel).where(MaterializedAssignmentModel.plan_id == plan_id)
    )
    asgn_objs = asgns_res.scalars().all()

    assignments = [
        {
            "assignment_id": a.assignment_id,
            "task_id": a.task_id,
            "start_time": a.start_time.isoformat() if a.start_time else None,
            "end_time": a.end_time.isoformat() if a.end_time else None,
            "track_segment_ids": a.track_segment_ids or [],
            "resource_ids": a.resource_ids or [],
        }
        for a in asgn_objs
    ]

    plan_dict = {
        "plan_id": plan_obj.plan_id,
        "plan_version_number": plan_obj.plan_version_number,
        "corridor_code": plan_obj.corridor_code,
        "snapshot_id": plan_obj.snapshot_id,
        "assignments": assignments,
        "is_valid": True,
    }

    # Query snapshot
    snap_dict: Dict[str, Any] = {"corridor_code": plan_obj.corridor_code, "tasks": [], "track_segments": []}
    if plan_obj.snapshot_id:
        snap_res = await db.execute(select(SnapshotModel).where(SnapshotModel.snapshot_id == plan_obj.snapshot_id))
        snap_obj = snap_res.scalar_one_or_none()
        if snap_obj and snap_obj.payload:
            snap_dict = snap_obj.payload
            snap_dict["snapshot_id"] = snap_obj.snapshot_id

    return plan_dict, snap_dict


@router.get("/scenarios", response_model=List[StressPerturbation])
async def list_declared_stress_scenarios():
    """
    Returns the declared versioned stress test perturbations across all 4 types:
    - WORK_DURATION_INCREASE
    - LATE_RESOURCE_ARRIVAL
    - SHIFTED_GOODS_FORECAST
    - URGENT_UNPLANNED_WORK
    """
    return DEFAULT_STRESS_SCENARIOS


@router.post("/metrics/calculate", response_model=CalculatedPlanMetrics)
async def calculate_plan_metrics(
    plan_id: Optional[str] = Query(None, description="Plan ID to load from database"),
    plan_data: Optional[Dict[str, Any]] = None,
    snapshot_data: Optional[Dict[str, Any]] = None,
    rule_policy_version: str = "v1.2.0-STANDARD",
    domain_version: str = "VKC-72H-DEFAULT",
    db: AsyncSession = Depends(get_db),
):
    """
    Calculates pinned, mathematically defensible metrics for a plan.
    Calculates mandatory/critical coverage, unscheduled reasons, and interval union
    infrastructure occupation.
    Zero denominators emit 'None' / N/A, never NaN/ZeroDivisionError.
    """
    if plan_id:
        p_dict, s_dict = await _load_plan_and_snapshot(db, plan_id)
        if snapshot_data:
            s_dict.update(snapshot_data)
    elif plan_data:
        p_dict = plan_data
        s_dict = snapshot_data or {}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either 'plan_id' query param or 'plan_data' body."
        )

    return PlanMetricsCalculator.calculate_plan_metrics(
        plan_dict=p_dict,
        snapshot_dict=s_dict,
        rule_policy_version=rule_policy_version,
        domain_version=domain_version,
    )


@router.post("/compare", response_model=FairComparisonResult)
async def compare_plans(
    baseline_plan_id: Optional[str] = Query(None),
    candidate_plan_id: Optional[str] = Query(None),
    payload: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Conducts a defensible fair comparison between baseline and candidate plans.
    Enforces aligned workload, horizon, and resource scope.
    Displays coverage before occupation gain.
    Does not fabricate percentage improvement if baseline is invalid or empty.
    """
    b_id = baseline_plan_id or (payload.get("baseline_plan_id") if payload else None)
    c_id = candidate_plan_id or (payload.get("candidate_plan_id") if payload else None)

    if payload and "baseline_plan" in payload and "candidate_plan" in payload:
        b_dict = payload["baseline_plan"]
        c_dict = payload["candidate_plan"]
        s_dict = payload.get("snapshot", {})
    elif b_id and c_id:
        b_dict, b_snap = await _load_plan_and_snapshot(db, b_id)
        c_dict, _ = await _load_plan_and_snapshot(db, c_id)
        s_dict = b_snap
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either baseline_plan_id and candidate_plan_id, or full payload with baseline_plan and candidate_plan."
        )

    domain_ver = (payload.get("declared_domain_version") if payload else None) or "VKC-72H-DEFAULT"
    return FairComparisonEngine.compare_plans(
        baseline_plan=b_dict,
        candidate_plan=c_dict,
        snapshot_dict=s_dict,
        declared_domain_version=domain_ver,
    )


@router.post("/stress-test", response_model=FixedPlanStressReport)
async def run_fixed_plan_stress_test(
    plan_id: Optional[str] = Query(None),
    plan_data: Optional[Dict[str, Any]] = None,
    snapshot_data: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Runs fixed-plan stress tests against declared versioned perturbations.
    Recomputes phase consequences and independently validates unchanged assignments.
    Output pass share is displayed strictly as a count ('8 of 10 passed'),
    NOT as an uncalibrated reliability probability.
    """
    if plan_id:
        p_dict, s_dict = await _load_plan_and_snapshot(db, plan_id)
        if snapshot_data:
            s_dict.update(snapshot_data)
    elif plan_data:
        p_dict = plan_data
        s_dict = snapshot_data or {}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either 'plan_id' query param or 'plan_data' body."
        )

    return StressTestingEngine.run_fixed_plan_stress_test(
        plan_dict=p_dict,
        snapshot_dict=s_dict,
    )


@router.post("/adaptive-stress-test", response_model=AdaptiveStressRecoveryResult)
async def run_adaptive_stress_recovery(
    plan_id: Optional[str] = Query(None),
    plan_data: Optional[Dict[str, Any]] = None,
    snapshot_data: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes an adaptive recovery experiment under a perturbed snapshot.
    Kept strictly separate from fixed-plan robustness.
    """
    if plan_id:
        p_dict, s_dict = await _load_plan_and_snapshot(db, plan_id)
        if snapshot_data:
            s_dict.update(snapshot_data)
    elif plan_data:
        p_dict = plan_data
        s_dict = snapshot_data or {}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either 'plan_id' query param or 'plan_data' body."
        )

    return StressTestingEngine.run_adaptive_recovery_experiment(
        plan_dict=p_dict,
        snapshot_dict=s_dict,
    )
