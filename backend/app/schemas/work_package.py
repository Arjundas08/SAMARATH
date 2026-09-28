"""
Pydantic schemas for Executable Work Packages, Recipes, and Phase DAGs.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.enums import DepartmentType, CompatibilityEffect, WorkPhaseType


class PackagePhase(APIModel):
    phase_type: WorkPhaseType
    duration_minutes: int = Field(..., ge=0)
    offset_start_minutes: int = Field(..., ge=0)
    offset_end_minutes: int = Field(..., ge=0)
    required_resources: List[str] = Field(default_factory=list)
    description: str


class WorkPackageRecipe(APIModel):
    recipe_id: str
    name: str
    total_duration_minutes: int
    is_sequential: bool = False
    phases: List[PackagePhase] = Field(default_factory=list)
    assumption_badge: str = "[TEST_ASSUMPTION]"


class WorkPackage(APIModel):
    package_id: str
    task_ids: List[UUID]
    business_keys: List[str]
    departments: List[DepartmentType]
    track_segment_id: str
    chainage_start_km: float
    chainage_end_km: float
    requires_power_block: bool = False
    power_block_elementary_section: Optional[str] = None
    compatibility_verdict: CompatibilityEffect
    cumulative_capacity_required: int = 1
    available_capacity: int = 2
    is_eligible: bool = True
    ineligibility_reason: Optional[str] = None
    recipe: WorkPackageRecipe
    metadata: Dict[str, Any] = Field(default_factory=dict)
