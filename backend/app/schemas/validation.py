"""
Independent Feasibility Checker validation results and rule evaluation schemas.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.enums import ValidationVerdict, RuleVerdict


class RuleEvaluation(APIModel):
    rule_id: str
    rule_name: str
    verdict: RuleVerdict
    violation_count: int
    details: str
    affected_task_keys: List[str] = Field(default_factory=list)


class ViolationDetail(APIModel):
    violation_id: str
    rule_id: str
    severity: str  # "CRITICAL_SAFETY", "RESOURCE_COLLISION", "POLICY_WARNING"
    description: str
    conflicting_task_ids: List[UUID] = Field(default_factory=list)
    conflicting_train_numbers: List[str] = Field(default_factory=list)
    location_track_id: Optional[str] = None
    time_window_utc: Optional[str] = None


class ValidationResult(APIModel):
    validation_id: UUID = Field(default_factory=uuid4)
    snapshot_id: UUID
    plan_id: UUID
    overall_verdict: ValidationVerdict
    checked_at_utc: datetime = Field(default_factory=datetime.utcnow)
    checks_passed: int
    checks_failed: int
    checks_unknown: int
    rule_evaluations: List[RuleEvaluation] = Field(default_factory=list)
    violations: List[ViolationDetail] = Field(default_factory=list)
