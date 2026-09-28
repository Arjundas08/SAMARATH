"""
Pydantic schemas for Declarative Compatibility Rules and Verification Workflows.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel, utc_now
from app.schemas.enums import DepartmentType, CompatibilityEffect


class DeclarativeCompatibilityRule(APIModel):
    rule_id: str = Field(..., description="Unique rule code, e.g. RULE-IR-001")
    revision: int = Field(default=1, ge=1)
    department_a: DepartmentType
    work_type_a: str = Field(..., description="Work type pattern or '*' for all")
    department_b: DepartmentType
    work_type_b: str = Field(..., description="Work type pattern or '*' for all")
    effect: CompatibilityEffect = CompatibilityEffect.ALLOWED
    requires_concurrent_execution: bool = False
    requires_sequential_execution: bool = False
    requires_isolation: bool = False
    description: str = Field(..., description="Technical engineering rationale")
    evidence_reference: str = Field(..., description="IR Manual clause, e.g. IR_PWM_2020_PARA_804")
    author: str = "Chief Safety Officer"
    approver: str = "Principal Chief Engineer"
    effective_from_utc: datetime = Field(default_factory=utc_now)
    effective_to_utc: Optional[datetime] = None
    superseded_by_revision: Optional[int] = None


class RuleVerificationRequest(APIModel):
    rule_id: str = Field(..., description="Rule code to verify/update")
    new_effect: CompatibilityEffect = Field(..., description="New verified effect: ALLOWED, PROHIBITED, or UNKNOWN")
    evidence_document: str = Field(..., min_length=5, description="Documentary citation or joint safety assessment")
    notes: str = Field(..., min_length=5, description="Engineering review comments")
    approving_officer: str = Field(..., min_length=3, description="Officer name/designation authorizing update")


class CompatibilityEvaluationResult(APIModel):
    effect: CompatibilityEffect
    matched_rule_ids: List[str] = Field(default_factory=list)
    is_prohibited: bool = False
    is_allowed: bool = False
    is_unknown: bool = False
    dominant_rule: Optional[str] = None
    explanation: str
    facts: Dict[str, Any] = Field(default_factory=dict)
