"""
Phase 16 – Execution Feedback, Partial Work, and Estimate Review REST API.

Blueprint Sections: 9, 13, 35-36.
Endpoints:
  POST /execution/record                 – Ingest execution record (authoritative / TEST)
  PUT  /execution/revise                 – Audited correction superseding old record
  POST /execution/residual/confirm       – Confirm governed residual work without double counting
  GET  /execution/variance/{task_id}     – Plan-vs-actual variance with missing attribution notes
  GET  /execution/records                – List latest execution records
  GET  /execution/residual/tasks         – List residual tasks for next planning cycle
  GET  /execution/reconciliation/queue   – Unresolved chronology/unit conflict queue
  POST /execution/reconciliation/resolve – Resolve conflict with audit notes
  GET  /execution/estimate-review        – Deterministic variance & estimate review recommendations
  GET  /execution/occupied-resources     – Still-occupied resources tracking
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends

from app.core.auth import require_authenticated, BOOTSTRAP_USERS
from app.schemas.execution import (
    ExecutionRecordCreate,
    ExecutionRecordRevisionRequest,
    ResidualWorkConfirmRequest,
)
from app.engine.execution_engine import execution_engine

router = APIRouter(prefix="/execution", tags=["execution"])


def _normalize_actor(user: dict) -> dict:
    """Normalize actor dict to guarantee user_id and display_name are populated."""
    if not isinstance(user, dict):
        return {"user_id": "system", "display_name": "System"}
    user_id = user.get("user_id") or user.get("sub", "system")
    display_name = user.get("display_name")
    if not display_name:
        for b in BOOTSTRAP_USERS.values():
            if b.get("user_id") == user_id:
                display_name = b.get("display_name")
                break
    if not display_name:
        display_name = user_id
    normalized = dict(user)
    normalized["user_id"] = user_id
    normalized["display_name"] = display_name
    return normalized


# ──────────────────────────────────────────────
#  1. Record Intake
# ──────────────────────────────────────────────

@router.post("/record", summary="Ingest execution record observation")
async def record_execution(request: ExecutionRecordCreate,
                           user=Depends(require_authenticated)):
    """
    Ingest authoritative or TEST execution observation.
    Validates chronology, source version, and units.
    """
    try:
        actor = _normalize_actor(user)
        record = execution_engine.record_execution(request, actor)
        return record.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ──────────────────────────────────────────────
#  2. Audited Correction Revision
# ──────────────────────────────────────────────

@router.put("/revise", summary="Audited correction of previous outcome")
async def revise_execution(request: ExecutionRecordRevisionRequest,
                           user=Depends(require_authenticated)):
    """
    Audited correction superseding old record and invalidating affected planning.
    """
    try:
        actor = _normalize_actor(user)
        record = execution_engine.revise_execution_record(request, actor)
        return record.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ──────────────────────────────────────────────
#  3. Governed Residual Work
# ──────────────────────────────────────────────

@router.post("/residual/confirm", summary="Confirm governed residual work")
async def confirm_residual_work(request: ResidualWorkConfirmRequest,
                                user=Depends(require_authenticated)):
    """
    Confirm residual work from partial execution.
    Enforces completed_quantity + residual_quantity == target_quantity (no double counting).
    """
    try:
        actor = _normalize_actor(user)
        residual = execution_engine.confirm_residual_work(request, actor)
        return residual.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/residual/tasks", summary="List all confirmed residual tasks")
async def get_residual_tasks(user=Depends(require_authenticated)):
    """List all confirmed residual tasks eligible for next planning inputs."""
    residuals = execution_engine.get_residual_tasks()
    return {"residual_tasks": [r.model_dump() for r in residuals]}


# ──────────────────────────────────────────────
#  4. Plan-vs-Actual Variance
# ──────────────────────────────────────────────

@router.get("/variance/{task_id}", summary="Get plan-vs-actual variance for task")
async def get_variance(task_id: str,
                       user=Depends(require_authenticated)):
    """Calculate plan-vs-actual variance. Explains missing attribution instead of inventing delay."""
    variance = execution_engine.get_plan_vs_actual_variance(task_id)
    if not variance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No execution records found for task {task_id}"
        )
    return variance.model_dump()


@router.get("/records", summary="List latest execution records")
async def list_records(task_id: Optional[str] = None,
                       user=Depends(require_authenticated)):
    """List latest execution records with optional task_id filter."""
    if task_id:
        recs = execution_engine.get_records_for_task(task_id)
    else:
        recs = execution_engine.get_all_records()
    return {"records": [r.model_dump() for r in recs]}


# ──────────────────────────────────────────────
#  5. Reconciliation Queue
# ──────────────────────────────────────────────

@router.get("/reconciliation/queue", summary="List unresolved reconciliation conflicts")
async def get_reconciliation_queue(user=Depends(require_authenticated)):
    """List unresolved chronology, duplicate, or unit conflicts."""
    items = execution_engine.get_reconciliation_queue()
    return {"queue": [i.model_dump() for i in items]}


@router.post("/reconciliation/resolve", summary="Resolve a reconciliation conflict")
async def resolve_reconciliation_conflict(payload: dict,
                                          user=Depends(require_authenticated)):
    """Resolve a conflict with audit justification."""
    conflict_id = payload.get("conflict_id")
    notes = payload.get("resolution_notes", "Resolved by supervisor")
    if not conflict_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="conflict_id is required")
    try:
        actor = _normalize_actor(user)
        resolved = execution_engine.resolve_reconciliation_conflict(conflict_id, notes, actor)
        return resolved.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ──────────────────────────────────────────────
#  6. Deterministic Estimate Review
# ──────────────────────────────────────────────

@router.get("/estimate-review", summary="Deterministic estimate review recommendations")
async def get_estimate_review(user=Depends(require_authenticated)):
    """
    Deterministic variance review proposing buffer adjustments.
    Does NOT train ML on fictional outcomes; preserves sealed snapshots.
    """
    response = execution_engine.generate_estimate_review()
    return response.model_dump()


# ──────────────────────────────────────────────
#  7. Still-Occupied Resources
# ──────────────────────────────────────────────

@router.get("/occupied-resources", summary="Get resources still occupied past window")
async def get_occupied_resources(user=Depends(require_authenticated)):
    """Get resources that remain physically tied up due to overruns."""
    resources = execution_engine.get_still_occupied_resources()
    return {"still_occupied_resources": resources}
