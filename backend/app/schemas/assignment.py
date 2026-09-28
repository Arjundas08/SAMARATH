"""
MaterializedAssignment and WorkPhaseSchedule schemas.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.task import ResourceRequirement


class WorkPhaseSchedule(APIModel):
    setup_start_utc: datetime
    setup_end_utc: datetime
    work_start_utc: datetime
    work_end_utc: datetime
    restoration_start_utc: datetime
    restoration_end_utc: datetime


class MaterializedAssignment(APIModel):
    assignment_id: UUID = Field(default_factory=uuid4)
    plan_id: UUID
    task_id: UUID
    business_key: str
    track_segment_id: str
    start_utc: datetime
    end_utc: datetime
    start_minute: int
    end_minute: int
    duration_minutes: int
    work_phase_schedule: WorkPhaseSchedule
    assigned_resources: List[ResourceRequirement] = Field(default_factory=list)
    power_block_required: bool = False
    power_block_section: Optional[str] = None
    is_locked: bool = False
    is_shadow_block: bool = False
    bundled_with_task_ids: List[UUID] = Field(default_factory=list)
