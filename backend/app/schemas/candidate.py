"""
Candidate placement manifest schemas for Phase 06:
Sparse Opportunity Generation and Credible Baseline.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.work_package import PackagePhase


class PlacementCandidate(APIModel):
    candidate_id: str
    package_id: str
    task_ids: List[UUID]
    business_keys: List[str]
    track_segment_id: str
    start_utc: datetime
    end_utc: datetime
    start_minute: int
    end_minute: int
    duration_minutes: int
    start_second: int = 0
    end_second: int = 0
    duration_seconds: int = 0
    assigned_resources: List[str] = Field(default_factory=list)
    phases: List[PackagePhase] = Field(default_factory=list)
    is_locked: bool = False
    lock_reason: Optional[str] = None
    requires_power_block: bool = False
    power_block_elementary_section: Optional[str] = None
    isolated_tracks: List[str] = Field(default_factory=list)
    shadow_with_task_id: Optional[UUID] = None
    is_valid_prefilter: bool = True
    train_conflict_penalty: float = 0.0


class CandidateManifest(APIModel):
    manifest_id: UUID = Field(default_factory=uuid4)
    snapshot_id: UUID
    total_candidates: int
    candidates: List[PlacementCandidate] = Field(default_factory=list)
    is_truncated: bool = False
    truncation_reason: Optional[str] = None
    generation_duration_ms: float = 0.0
    metrics: Dict[str, Any] = Field(default_factory=dict)
