"""
Pydantic schemas for Multi-Dimensional Readiness Assessment.
Evaluates 9 dimensions per blueprint Section 16.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel, utc_now
from app.schemas.enums import ReadinessDimension, ReadinessState


class DimensionAssessment(APIModel):
    dimension: ReadinessDimension
    state: ReadinessState
    reason: str
    evidence_ref: Optional[str] = None
    checked_at_utc: datetime = Field(default_factory=utc_now)
    expires_at_utc: Optional[datetime] = None


class TaskReadinessAssessment(APIModel):
    task_id: UUID
    business_key: str
    overall_state: ReadinessState
    is_executable: bool = Field(..., description="True only if overall_state is READY")
    dimensions: List[DimensionAssessment] = Field(default_factory=list)
    worst_dimension: ReadinessDimension
    worst_dimension_reason: str
    evaluated_at_utc: datetime = Field(default_factory=utc_now)
    evaluated_interval_start_utc: Optional[datetime] = None
    evaluated_interval_end_utc: Optional[datetime] = None
    details: Dict[str, Any] = Field(default_factory=dict)
