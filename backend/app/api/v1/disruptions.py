"""
Phase 13: Disruption Events, Stable Replanning & PlanDiff API Endpoints.
Blueprint Sections: 27-28, 34 plus addendum.

REST endpoints for:
- Disruption event submission (POST /disruptions/events)
- Event listing and retrieval
- Impact closure computation
- Stable replan triggering
- PlanDiff computation and retrieval
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.disruption import (
    DisruptionEventCreate,
    DisruptionEventResponse,
    DisruptionEventListResponse,
    ImpactClosureResponse,
    StableReplanRequest,
    StableReplanResponse,
    PlanDiffRequest,
    PlanDiffV2,
)
from app.engine.disruption_events import (
    DisruptionEventEngine,
    DuplicateEventError,
    OutOfOrderEventError,
)
from app.engine.stable_replanner import StableReplanner
from app.engine.plandiff_engine import PlanDiffEngine

router = APIRouter(prefix="/disruptions", tags=["Phase 13: Disruptions & Replanning"])


# --- Event Endpoints ---

@router.post("/events", response_model=DisruptionEventResponse, status_code=201)
async def submit_disruption_event(
    event: DisruptionEventCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a versioned, idempotent disruption event.
    
    Validates source order and scope. In one transaction persists the
    revision/audit/outbox event and invalidates affected plan applicability.
    An old approved artifact remains historically approved while its current
    usability becomes STALE or BLOCKED.
    """
    engine = DisruptionEventEngine()
    try:
        return await engine.receive_event(db, event)
    except DuplicateEventError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except OutOfOrderEventError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/events", response_model=DisruptionEventListResponse)
async def list_disruption_events(
    corridor_code: str = Query(default="VKC"),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Returns all disruption events for a corridor."""
    engine = DisruptionEventEngine()
    events = await engine.get_all_events(db, corridor_code, limit)
    return DisruptionEventListResponse(events=events, total=len(events))


@router.get("/events/pending", response_model=DisruptionEventListResponse)
async def list_pending_events(
    corridor_code: str = Query(default="VKC"),
    db: AsyncSession = Depends(get_db),
):
    """Returns all pending (non-completed) disruption events."""
    engine = DisruptionEventEngine()
    events = await engine.get_pending_events(db, corridor_code)
    return DisruptionEventListResponse(events=events, total=len(events))


# --- Impact Closure ---

@router.post("/impact-closure", response_model=ImpactClosureResponse)
async def compute_impact_closure(
    event_ids: List[str],
    baseline_plan_id: str = Query(...),
    max_expansions: int = Query(default=2, ge=0, le=5),
    db: AsyncSession = Depends(get_db),
):
    """
    Computes impact closure across package membership, dependencies,
    shared resources, overlapping affected footprints and parent/boundary commitments.
    
    Discloses restricted search scope; does not call it globally minimum-change.
    """
    engine = DisruptionEventEngine()
    try:
        return await engine.compute_impact_closure(
            db, event_ids=event_ids, baseline_plan_id=baseline_plan_id,
            max_expansions=max_expansions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Stable Replanning ---

@router.post("/replan", response_model=StableReplanResponse)
async def trigger_stable_replan(
    request: StableReplanRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers minimal-churn disruption recovery replanning.
    
    Uses DISRUPTION_RECOVERY objectives. Minimizes changed comparable
    assignments before marginal efficiency gains. Preserves completed work
    and hard locks. A conflicting hard lock creates escalation, never
    automatic unlock.
    """
    replanner = StableReplanner()
    try:
        return await replanner.trigger_replan(db, request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replan/check-escalation")
async def check_lock_escalation(
    plan_id: str = Query(...),
    event_ids: List[str] = Query(default=[]),
    db: AsyncSession = Depends(get_db),
):
    """
    Checks if disruption events conflict with hard-locked assignments.
    Returns escalation details for each conflict.
    """
    replanner = StableReplanner()
    try:
        escalations = await replanner.check_lock_escalation(db, plan_id, event_ids)
        return {"escalations": escalations, "has_conflicts": len(escalations) > 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- PlanDiff ---

@router.post("/plandiff", response_model=PlanDiffV2)
async def compute_plan_diff(
    request: PlanDiffRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Computes PlanDiff between two plan versions.
    
    Categories: unchanged, shifted, resource_changed, repackaged,
    added, cancelled, now_unscheduled, completed.
    
    Distinguishes actual cancellation from an omitted assignment
    and from residual work.
    """
    engine = PlanDiffEngine()
    try:
        return await engine.compute_diff(
            db, from_plan_id=request.from_plan_id, to_plan_id=request.to_plan_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plandiff/{diff_id}", response_model=PlanDiffV2)
async def get_plan_diff(
    diff_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves a persisted PlanDiff by ID."""
    engine = PlanDiffEngine()
    diff = await engine.get_diff(db, diff_id)
    if not diff:
        raise HTTPException(status_code=404, detail=f"Diff '{diff_id}' not found")
    return diff


@router.get("/plandiff/for-plan/{plan_id}")
async def get_diffs_for_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Returns all diffs where this plan is either source or target."""
    engine = PlanDiffEngine()
    diffs = await engine.get_diffs_for_plan(db, plan_id)
    return {"diffs": [d.model_dump(mode="json") for d in diffs], "total": len(diffs)}
