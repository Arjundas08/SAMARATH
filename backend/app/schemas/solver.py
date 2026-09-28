"""
SolverRun and SolveJob schemas.
"""
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.enums import (
    ObjectiveProfile,
    SolverStatus,
    JobState,
    StopReason,
)


class SolveJobRequest(APIModel):
    snapshot_id: UUID
    objective_profile: ObjectiveProfile = ObjectiveProfile.PROGRAMME_IMPROVEMENT
    time_limit_seconds: int = Field(default=30, ge=5, le=300)
    allow_partial_solution: bool = True


class SolveJob(APIModel):
    job_id: UUID = Field(default_factory=uuid4)
    snapshot_id: UUID
    objective_profile: ObjectiveProfile
    status: JobState = JobState.QUEUED
    progress_percentage: int = Field(default=0, ge=0, le=100)
    current_phase: str = "QUEUED"
    lease_owner: Optional[str] = None
    lease_expires_at: Optional[datetime] = None
    result_plan_id: Optional[UUID] = None
    error_detail: Optional[str] = None
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)
    completed_at_utc: Optional[datetime] = None


class SolverRun(APIModel):
    run_id: UUID = Field(default_factory=uuid4)
    job_id: UUID
    snapshot_id: UUID
    objective_profile: ObjectiveProfile
    solver_engine: str = "ORTOOLS_CP_SAT"
    solver_version: str = "9.10.4067"
    solver_status: SolverStatus
    stop_reason: StopReason
    objective_value: Optional[float] = None
    solve_wall_time_seconds: float
    num_variables: int
    num_constraints: int
    scheduled_tasks_count: int
    unscheduled_tasks_count: int
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)
