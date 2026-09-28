"""
Phase 15 – Human Review, Programme Approval, and Audit Integrity REST API.

Endpoints:
  POST /approval/register         – Register a plan for approval workflow
  POST /approval/submit-review    – Submit plan for joint review
  POST /approval/review           – Submit a review decision
  GET  /approval/eligibility/{id} – Pre-flight approval eligibility check
  POST /approval/approve          – Atomic approval transaction
  POST /approval/lock             – Create a field-level lock
  PUT  /approval/lock/revise      – Revise an existing lock
  GET  /approval/locks/{id}       – Get all active locks for a plan
  GET  /approval/audit            – Query audit trail
  GET  /approval/export/{id}      – Export evidence with provenance manifest
  GET  /approval/summary/{id}     – Plan approval status summary

Security invariants:
  - Infrastructure admin CANNOT approve (enforced server-side)
  - Self-approval is prohibited (enforced server-side)
  - Audit trail is append-only (no UPDATE/DELETE endpoint exists)
  - Metrics are read-only (no mutation endpoint for computed values)
  - No grant, extension, signal-control, or release endpoint exists
"""
from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, status, Depends

from app.core.auth import require_permission, require_authenticated, get_current_user, BOOTSTRAP_USERS
from app.schemas.auth import Permission
from app.schemas.approval import (
    ReviewRequest, ApprovalRequest,
    LockCreateRequest, LockRevisionRequest,
    SubmitForReviewRequest,
)
from app.engine.approval_engine import approval_engine

router = APIRouter(prefix="/approval", tags=["approval"])


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
#  Plan Registration
# ──────────────────────────────────────────────

@router.post("/register", summary="Register a plan for approval workflow")
async def register_plan(payload: dict,
                        user=Depends(require_authenticated)):
    """Register a plan for the approval workflow."""
    plan_id = payload.get("plan_id", str(uuid4()))
    plan_data = payload.get("plan_data", payload)
    provenance = payload.get("provenance_mode", "TEST")

    result = approval_engine.register_plan(plan_id, plan_data, provenance)
    return {"status": "registered", **result}


# ──────────────────────────────────────────────
#  Submit for Review
# ──────────────────────────────────────────────

@router.post("/submit-review", summary="Submit plan for joint review")
async def submit_for_review(request: SubmitForReviewRequest,
                            user=Depends(require_permission(Permission.PROGRAMME_REVIEW))):
    """Submit a plan for joint review. Requires PROGRAMME_REVIEW permission."""
    actor = _normalize_actor(user)
    result = approval_engine.submit_for_review(request, actor)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=result["error"])
    return result


# ──────────────────────────────────────────────
#  Review Decision
# ──────────────────────────────────────────────

@router.post("/review", summary="Submit a review decision")
async def submit_review(request: ReviewRequest,
                        user=Depends(require_permission(Permission.PROGRAMME_REVIEW))):
    """
    Submit a review decision (RECOMMEND, REQUEST_REVISION, REJECT).
    Binds to exact immutable plan content hash, checker result, and parent lineage.
    Requires PROGRAMME_REVIEW permission.
    """
    try:
        actor = _normalize_actor(user)
        decision = approval_engine.submit_review(request, actor)
        return decision.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc))


# ──────────────────────────────────────────────
#  Approval Eligibility Check
# ──────────────────────────────────────────────

@router.get("/eligibility/{plan_id}", summary="Pre-flight approval eligibility check")
async def check_eligibility(plan_id: str,
                            user=Depends(require_authenticated)):
    """Check whether a plan is eligible for approval."""
    result = approval_engine.check_eligibility(plan_id)
    return result.model_dump()


# ──────────────────────────────────────────────
#  Atomic Approval Transaction
# ──────────────────────────────────────────────

@router.post("/approve", summary="Atomic approval transaction")
async def process_approval(request: ApprovalRequest,
                           user=Depends(require_authenticated)):
    """
    Atomic approval transaction with freshness checks.
    Server-side enforced:
      - Version epoch must match (no concurrent mutation)
      - Content hash must match (plan not modified)
      - ETag must match (optimistic concurrency)
      - Checker result must be VALID
      - Review recommendation must exist
      - Actor must have PROGRAMME_APPROVE permission
      - Infrastructure admin cannot approve
      - Self-approval is prohibited
    """
    actor = _normalize_actor(user)
    result = approval_engine.process_approval(request, actor)
    status_code = status.HTTP_200_OK if result.success else status.HTTP_409_CONFLICT
    if result.was_idempotent_duplicate:
        status_code = status.HTTP_200_OK
    return result.model_dump()


# ──────────────────────────────────────────────
#  Lock Management
# ──────────────────────────────────────────────

@router.post("/lock", summary="Create a field-level lock")
async def create_lock(request: LockCreateRequest,
                      user=Depends(require_authenticated)):
    """
    Create a field-level lock on a specific assignment within a plan.
    Locks identify task/assignment fields and authority category, not a whole-plan boolean.
    """
    try:
        actor = _normalize_actor(user)
        lock = approval_engine.create_lock(request, actor)
        return lock.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc))


@router.put("/lock/revise", summary="Revise an existing lock")
async def revise_lock(request: LockRevisionRequest,
                      user=Depends(require_authenticated)):
    """
    Revise an existing lock through an audited new revision.
    Operational reservations and completed history are not unlockable by this workflow.
    """
    try:
        actor = _normalize_actor(user)
        lock = approval_engine.revise_lock(request, actor)
        return lock.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc))


@router.get("/locks/{plan_id}", summary="Get all active locks for a plan")
async def get_locks(plan_id: str,
                    user=Depends(require_authenticated)):
    """Get all active locks for a plan."""
    locks = approval_engine.get_locks(plan_id)
    return {"plan_id": plan_id, "locks": [lk.model_dump() for lk in locks]}


# ──────────────────────────────────────────────
#  Audit Trail (Read-Only)
# ──────────────────────────────────────────────

@router.get("/audit", summary="Query append-only audit trail")
async def query_audit_trail(scope: Optional[str] = None,
                            limit: int = 100,
                            user=Depends(require_permission(Permission.AUDIT_READ))):
    """
    Query the append-only audit trail.
    Application-role permissions prohibit update/delete of history.
    Hash-chain provides tamper-evidence within stated assumptions
    (not DBA-proof immutability).
    """
    result = approval_engine.get_audit_trail(scope_filter=scope, limit=limit)
    return result.model_dump()


# ──────────────────────────────────────────────
#  Evidence Export
# ──────────────────────────────────────────────

@router.get("/export/{plan_id}", summary="Export evidence with provenance manifest")
async def export_evidence(plan_id: str,
                          user=Depends(require_permission(Permission.AUDIT_READ))):
    """
    Generate an evidence export with provenance, status, and source/version manifest.
    A proposal export is NEVER an official Railway grant.
    The disclaimer is included in every export.
    """
    try:
        actor = _normalize_actor(user)
        export = approval_engine.export_evidence(plan_id, actor)
        return export.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(exc))


# ──────────────────────────────────────────────
#  Plan Summary (Read-Only)
# ──────────────────────────────────────────────

@router.get("/summary/{plan_id}", summary="Plan approval status summary")
async def get_plan_summary(plan_id: str,
                           user=Depends(require_authenticated)):
    """Read-only plan summary. Server-enforced read-only metrics."""
    summary = approval_engine.get_plan_summary(plan_id)
    if "error" in summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=summary["error"])
    return summary
