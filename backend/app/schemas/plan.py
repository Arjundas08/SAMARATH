"""
PlanVersion, PlanMetrics, and Programme Review schemas.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.enums import (
    PlanStatus,
    ProgrammeAuthorityState,
    FieldAuthorityState,
    ApprovalEligibility,
)
from app.schemas.assignment import MaterializedAssignment


class PlanMetric(APIModel):
    total_tasks_demanded: int
    total_tasks_scheduled: int
    statutory_safety_compliance_pct: float
    corridor_availability_hours: float
    total_possession_hours: float
    multi_dept_shadow_blocks_count: int
    estimated_train_impact_index: float
    unscheduled_mandatory_count: int


class PlanVersion(APIModel):
    plan_id: UUID = Field(default_factory=uuid4)
    plan_version_number: int = 1
    snapshot_id: UUID
    parent_plan_id: Optional[UUID] = None
    validation_id: Optional[UUID] = None
    horizon_type: str = "WEEKLY"  # "MONTHLY", "WEEKLY"
    plan_status: PlanStatus = PlanStatus.DRAFT_PROPOSAL
    programme_authority_state: ProgrammeAuthorityState = ProgrammeAuthorityState.PROPOSED
    field_authority_state: FieldAuthorityState = FieldAuthorityState.NOT_REQUESTED
    approval_eligibility: ApprovalEligibility = ApprovalEligibility.ELIGIBLE
    metrics: PlanMetric
    assignments: List[MaterializedAssignment] = Field(default_factory=list)
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)
    approved_at_utc: Optional[datetime] = None
    approved_by_officer: Optional[str] = None
