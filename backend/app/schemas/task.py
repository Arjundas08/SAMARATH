"""
Typed schemas for Task / Maintenance Demand ingestion, validation, and presentation.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field, model_validator

from app.schemas.common import APIModel, utc_now
from app.schemas.enums import (
    DepartmentType,
    CriticalityTier,
    DemandStatus,
    ProvenanceMode,
    ResourceType,
)


class PreferredWindow(APIModel):
    window_start_utc: datetime
    window_end_utc: datetime

    @model_validator(mode="after")
    def validate_window_chronology(self):
        if self.window_end_utc <= self.window_start_utc:
            raise ValueError("window_end_utc must be strictly after window_start_utc")
        return self


class ResourceRequirement(APIModel):
    resource_type: ResourceType
    resource_id: str = Field(..., description="Unique machine ID or gang identifier")
    quantity: int = Field(default=1, ge=1)


class TaskBase(APIModel):
    business_key: str = Field(..., description="Human-readable business key, e.g., TASK-TMS-0012")
    department: DepartmentType
    sub_department: str
    work_type: str
    description: str
    station_from: str = Field(..., max_length=10)
    station_to: str = Field(..., max_length=10)
    track_segment_id: str
    chainage_start_km: float = Field(..., ge=0.0)
    chainage_end_km: float = Field(..., ge=0.0)
    duration_minutes: int = Field(..., ge=15, description="Net physical productive work time in minutes")
    setup_buffer_minutes: int = Field(default=30, ge=0, description="Pre-work possession and machine positioning buffer")
    restoration_buffer_minutes: int = Field(default=30, ge=0, description="Post-work track testing and clearance buffer")
    criticality: CriticalityTier = CriticalityTier.TIER_3_CYCLIC
    deadline_utc: datetime
    earliest_start_date: Optional[datetime] = None
    dependencies: List[str] = Field(default_factory=list, description="Predecessor task IDs or business keys")
    preferred_windows: List[PreferredWindow] = Field(default_factory=list)
    required_resources: List[ResourceRequirement] = Field(default_factory=list)
    requires_power_block: bool = False
    power_block_elementary_section: Optional[str] = None
    requires_speed_restriction_after: bool = False
    imposed_speed_kmh: Optional[int] = None
    provenance_mode: ProvenanceMode = ProvenanceMode.TEST

    @model_validator(mode="after")
    def validate_chainage_and_power(self):
        if self.chainage_end_km < self.chainage_start_km:
            raise ValueError("chainage_end_km must be greater than or equal to chainage_start_km")
        if self.requires_power_block and not self.power_block_elementary_section:
            raise ValueError("power_block_elementary_section is mandatory when requires_power_block is True")
        return self


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    task_id: UUID = Field(default_factory=uuid4)
    total_block_minutes: int = Field(..., description="Sum of duration + setup + restoration")
    demand_status: DemandStatus = DemandStatus.VALIDATED
    created_at_utc: datetime = Field(default_factory=utc_now)
    created_by: str = "system"

    @classmethod
    def from_create(cls, create_dto: TaskCreate, creator: str = "planner") -> "Task":
        total_block = create_dto.duration_minutes + create_dto.setup_buffer_minutes + create_dto.restoration_buffer_minutes
        return cls(
            **create_dto.model_dump(),
            task_id=uuid4(),
            total_block_minutes=total_block,
            demand_status=DemandStatus.VALIDATED,
            created_at_utc=utc_now(),
            created_by=creator,
        )
