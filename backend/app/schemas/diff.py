"""
PlanDiff and Version Delta schemas.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel


class RescheduledTaskDetail(APIModel):
    task_id: UUID
    business_key: str
    previous_start_utc: datetime
    new_start_utc: datetime
    shift_minutes: int
    reason: str


class PlanDiffSummary(APIModel):
    tasks_unchanged: int
    tasks_rescheduled: int
    tasks_cancelled: int
    tasks_added: int
    net_corridor_availability_delta_hours: float
    churn_score: float


class PlanDiff(APIModel):
    diff_id: UUID = Field(default_factory=uuid4)
    baseline_plan_id: UUID
    target_plan_id: UUID
    summary: PlanDiffSummary
    rescheduled_tasks: List[RescheduledTaskDetail] = Field(default_factory=list)
    cancelled_tasks: List[str] = Field(default_factory=list)
    added_tasks: List[str] = Field(default_factory=list)
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)
