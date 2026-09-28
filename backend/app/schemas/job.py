"""
Phase 10: Typed Schemas for Durable Solve Jobs, Worker Queue, and Planning APIs.
Blueprint Sections: 28, 31, 33-34, 42-43.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import Field, BaseModel

from app.schemas.common import APIModel
from app.schemas.enums import (
    ObjectiveProfile,
    JobState,
    SolverStatus,
    ApprovalEligibility,
)


class JobPhase(str):
    QUEUED = "QUEUED"
    CLAIMED = "CLAIMED"
    PREPARING_SNAPSHOT = "PREPARING_SNAPSHOT"
    BUILDING_CANDIDATES = "BUILDING_CANDIDATES"
    SOLVING = "SOLVING"
    VERIFYING_FEASIBILITY = "VERIFYING_FEASIBILITY"
    RECONCILING = "RECONCILING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SolveJobCreateRequest(APIModel):
    corridor_code: str = "VKC"
    snapshot_id: Optional[str] = None
    profile: ObjectiveProfile = ObjectiveProfile.PROGRAMME_IMPROVEMENT
    time_limit_seconds: float = Field(default=15.0, ge=1.0, le=120.0)
    num_workers: int = Field(default=1, ge=1, le=16)
    random_seed: int = 42
    lattice_step_minutes: int = Field(default=60, ge=15, le=120)
    max_candidates: int = Field(default=10000, ge=100, le=50000)
    parent_monthly_plan_id: Optional[str] = None
    target_week_index: Optional[int] = Field(default=None, ge=1, le=4)


class SolveJobCancelRequest(APIModel):
    reason: Optional[str] = "Cancelled by user"


class SolveJobResponse(APIModel):
    job_id: str
    corridor_code: str
    snapshot_id: str
    objective_profile: ObjectiveProfile
    status: JobState
    current_phase: str
    progress_percentage: int
    attempt_count: int
    version: int
    fencing_token: int
    lease_owner: Optional[str] = None
    lease_expires_at: Optional[datetime] = None
    created_at_utc: datetime
    completed_at_utc: Optional[datetime] = None
    status_url: str
    etag: str
    result_plan_id: Optional[str] = None
    error_detail: Optional[str] = None
    is_snapshot_obsolete: bool = False
    result_summary: Optional[Dict[str, Any]] = None


class SolveJobListResponse(APIModel):
    jobs: List[SolveJobResponse]
    total: int


class PlanVersionResponse(APIModel):
    plan_id: str
    plan_version_number: int
    corridor_code: str
    snapshot_id: str
    parent_plan_id: Optional[str] = None
    horizon_type: str = "WEEKLY"
    plan_status: str
    solver_status: Optional[str] = None
    checker_verdict: Optional[str] = None
    approval_eligibility: str
    total_tasks_count: int = 0
    scheduled_tasks_count: int = 0
    mandatory_scheduled_count: int = 0
    bundled_packages_count: int = 0
    total_block_minutes: int = 0
    solve_duration_ms: float = 0.0
    created_at_utc: datetime
    assignments: List[Dict[str, Any]] = Field(default_factory=list)
    reconciliation_cases: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
