"""
REST API Router: Evidence-Backed Why, Why-Not Diagnostics and Bounded Repair.
Implements Blueprint Sections 24, 25, 31, and 32.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.schemas.reason import (
    WhyNotDiagnostic,
    WhySelectedDiagnostic,
    TrialRepairRequest,
    TrialRepairResult,
    ApplyRepairRequest,
    ApplyRepairResponse,
)
from app.engine.diagnostics_engine import DiagnosticsEngine

router = APIRouter(prefix="/planning/diagnostics", tags=["Planning Diagnostics"])


def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    try:
        return get_current_user(request)
    except Exception:
        return None


@router.get(
    "/why-not/{plan_id}/{task_id}",
    response_model=WhyNotDiagnostic,
    summary="Why-Not Diagnostic for Unplaced Task",
    description="Returns structured evidence explaining why a task was not scheduled in the plan version.",
)
async def get_why_not_diagnostic(
    plan_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    try:
        return await DiagnosticsEngine.explain_unplaced_task(db=db, plan_id=plan_id, task_id=task_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnostics evaluation failed: {str(e)}",
        )


@router.get(
    "/why/{plan_id}/{assignment_id}",
    response_model=WhySelectedDiagnostic,
    summary="Why Diagnostic for Scheduled Assignment",
    description="Returns admissibility proofs, priority contribution, and counterfactual comparisons.",
)
async def get_why_selected_diagnostic(
    plan_id: str,
    assignment_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    try:
        return await DiagnosticsEngine.explain_selected_assignment(
            db=db, plan_id=plan_id, assignment_id=assignment_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Selection explanation failed: {str(e)}",
        )


@router.post(
    "/repairs/trial",
    response_model=TrialRepairResult,
    summary="Simulate Non-Publishable Trial Repair",
    description="Runs a bounded trial simulation and evaluates against the independent feasibility checker.",
)
async def simulate_trial_repair(
    request: TrialRepairRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    try:
        return await DiagnosticsEngine.simulate_trial_repair(db=db, request=request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trial repair simulation failed: {str(e)}",
        )


@router.post(
    "/repairs/apply",
    response_model=ApplyRepairResponse,
    summary="Apply Permitted Repair with ETag Precondition",
    description="Applies authorized input revisions and schedules a fresh normal solve job.",
)
async def apply_repair(
    request: ApplyRepairRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
):
    try:
        return await DiagnosticsEngine.apply_repair(db=db, request=request, user=user)
    except ValueError as e:
        if "Precondition Failed" in str(e):
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Repair application failed: {str(e)}",
        )
