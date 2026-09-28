"""
REST API endpoints for Declarative Compatibility Rules and Verification.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.schemas.enums import DepartmentType, CompatibilityEffect
from app.schemas.rules import (
    DeclarativeCompatibilityRule,
    RuleVerificationRequest,
    CompatibilityEvaluationResult,
)
from app.domain.rules import (
    get_all_rules,
    get_rule_by_id,
    verify_rule,
    evaluate_compatibility,
)
from app.core.auth import get_current_user
from app.schemas.auth import UserSession

router = APIRouter(prefix="/rules", tags=["Compatibility Rules"])


class RuleEvaluationQuery(BaseModel):
    department_a: DepartmentType
    work_type_a: str
    department_b: DepartmentType
    work_type_b: str


@router.get("", response_model=List[DeclarativeCompatibilityRule])
async def list_rules(active_only: bool = Query(True, description="Filter for active non-superseded rules")):
    """List all declarative compatibility rules."""
    return get_all_rules(active_only=active_only)


@router.get("/{rule_id}", response_model=DeclarativeCompatibilityRule)
async def get_rule(rule_id: str):
    """Get single rule by rule ID."""
    rule = get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    return rule


@router.post("/verify", response_model=DeclarativeCompatibilityRule)
async def verify_compatibility_rule(
    request: RuleVerificationRequest,
    current_user: UserSession = Depends(get_current_user),
):
    """
    Human 'verify' action.
    Attaches documentary evidence and updates rule state by creating a NEW approved revision.
    Never bypasses rules via an unverified flag.
    """
    try:
        updated = verify_rule(request, user_id=current_user.username)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/evaluate", response_model=CompatibilityEvaluationResult)
async def evaluate_pair(query: RuleEvaluationQuery):
    """Evaluate compatibility between two department work types."""
    return evaluate_compatibility(
        dept_a=query.department_a,
        work_a=query.work_type_a,
        dept_b=query.department_b,
        work_b=query.work_type_b,
    )
