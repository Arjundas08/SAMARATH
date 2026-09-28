"""
Schemas for Independent Feasibility Checker and Correctness Oracle.
Implements Blueprint Sections 23 & 41:
- Typed input structures for proposed schedules independent of solver candidates.
- Typed violation records with exact error codes, observed/expected values, units, and source references.
- Immutable checker verdict and report.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.common import APIModel, utc_now


class CheckerVerdict(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


class ViolationSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"


class CheckerViolation(APIModel):
    violation_code: str
    severity: ViolationSeverity
    entity_ids: List[str] = Field(default_factory=list)
    observed_value: str
    expected_value: str
    unit: str
    source_reference: str
    message: str


class CheckerPhase(APIModel):
    phase_name: str  # "SETUP", "EXECUTION", "TESTING", "RESTORATION"
    start_utc: datetime
    end_utc: datetime
    required_resources: List[str] = Field(default_factory=list)


class CheckerAssignment(APIModel):
    assignment_id: str
    task_ids: List[UUID]
    business_keys: List[str] = Field(default_factory=list)
    track_segment_id: str
    start_utc: datetime
    end_utc: datetime
    assigned_resources: List[str] = Field(default_factory=list)
    phases: List[CheckerPhase] = Field(default_factory=list)
    requires_power_block: bool = False
    power_block_elementary_section: Optional[str] = None
    isolated_tracks: List[str] = Field(default_factory=list)
    is_locked: bool = False


class ProposedPlan(APIModel):
    plan_id: str
    corridor_code: str = "VKC"
    snapshot_id: UUID
    snapshot_hash: str
    assignments: List[CheckerAssignment] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheckerReport(APIModel):
    checker_version: str = "2026.1-ORACLE-INDEPENDENT"
    verdict: CheckerVerdict
    checked_at_utc: datetime = Field(default_factory=utc_now)
    snapshot_id: UUID
    snapshot_hash: str
    violations: List[CheckerViolation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    coverage_metrics: Dict[str, Any] = Field(default_factory=dict)
    execution_duration_ms: float
    model_evidence_set: str = "IR-GENERAL-RULES-2026-VKC-TOPOLOGY-V1"
