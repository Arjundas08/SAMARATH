"""
Phase 16 – Execution Feedback, Partial Work, and Estimate Review Schemas.

Blueprint Sections: 9, 13, 35-36.
Enforces:
- Authoritative execution-record intake with strict chronology and unit validation
- External authority mirror (read-only observations; never issues grants/extensions/releases)
- Governed residual-work creation for partial completion without duplicate demand
- Distinguishes missing release from zero duration
- Audited corrections with event pipeline plan invalidation
- Deterministic plan-vs-actual variance and estimate review (no ML training on fictional outcomes)
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.schemas.enums import CriticalityTier, ProvenanceMode, DepartmentType


class ExecutionStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    ABANDONED = "ABANDONED"
    CANCELLED_EXTERNALLY = "CANCELLED_EXTERNALLY"


class ChronologyValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    MISSING_RELEASE = "MISSING_RELEASE"
    UNRESOLVED_CONFLICT = "UNRESOLVED_CONFLICT"


class DeviationReason(str, Enum):
    NONE = "NONE"
    MACHINE_BREAKDOWN = "MACHINE_BREAKDOWN"
    WEATHER_ADVERSE = "WEATHER_ADVERSE"
    LATE_POSSESSION_HANDOVER = "LATE_POSSESSION_HANDOVER"
    EARLY_BURST_CANCEL = "EARLY_BURST_CANCEL"
    UNEXPECTED_SITE_CONDITION = "UNEXPECTED_SITE_CONDITION"
    OTHER = "OTHER"


class EstimateReviewRecommendation(str, Enum):
    MAINTAIN_CURRENT = "MAINTAIN_CURRENT"
    INCREASE_BUFFER = "INCREASE_BUFFER"
    DECREASE_BUFFER = "DECREASE_BUFFER"
    SPLIT_WORK_PACKAGE = "SPLIT_WORK_PACKAGE"


# ──────────────────────────────────────────────
#  Execution Record Intake Schemas
# ──────────────────────────────────────────────

class ExecutionRecordCreate(BaseModel):
    """
    Intake schema for execution record observations.
    Can be ingested from external authority feed or created as TEST observations.
    """
    task_id: str = Field(..., description="Original task identifier")
    plan_id: Optional[str] = Field(None, description="Proposed/approved plan ID if linked")
    assignment_id: Optional[str] = Field(None, description="Specific assignment within plan")
    external_authority_ref: Optional[str] = Field(
        None, description="COA or Operating log reference (e.g. COA-BLOCK-20260927-01)"
    )
    actual_start_utc: datetime = Field(..., description="Actual commencement of work on track")
    actual_restoration_utc: datetime = Field(
        ..., description="Timestamp when track/OHE was physically restored to traffic condition"
    )
    actual_release_utc: Optional[datetime] = Field(
        None, description="Official operating hand-back timestamp. If None, indicates missing release signal."
    )
    quantity_completed: float = Field(..., ge=0.0, description="Productive output achieved")
    quantity_units: str = Field(..., description="Standardized measurement unit (e.g. METERS, KM, JOINTS)")
    target_quantity: Optional[float] = Field(None, ge=0.0, description="Nominal target quantity for comparison")
    planned_duration_minutes: Optional[int] = Field(None, ge=0, description="Original planned possession duration")
    resource_use: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of machines/crews used with actual hours (e.g. [{'resource_id': 'BCM-01', 'hours': 3.5}])"
    )
    still_occupied_resources: List[str] = Field(
        default_factory=list,
        description="Resources still tied up at site if work overran"
    )
    deviation_reason: DeviationReason = Field(DeviationReason.NONE, description="Primary cause of any variance")
    deviation_notes: Optional[str] = Field(None, description="Field supervisor notes")
    provenance_mode: ProvenanceMode = Field(
        ProvenanceMode.TEST, description="TEST or AUTHORIZED_IMPORT (never confers unearned authority)"
    )
    idempotency_key: Optional[str] = Field(None, description="Deduplication key")


class ExecutionRecordRevisionRequest(BaseModel):
    """
    Audited correction of a previously recorded outcome.
    Supersedes the prior record and invalidates downstream planning/metrics.
    """
    record_id: UUID = Field(..., description="Existing record to revise")
    correction_reason: str = Field(..., min_length=5, description="Mandatory audit justification for correction")
    actual_start_utc: Optional[datetime] = None
    actual_restoration_utc: Optional[datetime] = None
    actual_release_utc: Optional[datetime] = None
    quantity_completed: Optional[float] = None
    quantity_units: Optional[str] = None
    deviation_reason: Optional[DeviationReason] = None
    deviation_notes: Optional[str] = None


class ExecutionRecord(BaseModel):
    """
    Materialized execution record with chronology validation, variance calculations, and hash integrity.
    """
    record_id: UUID = Field(default_factory=uuid4)
    revision: int = Field(1, description="Sequential revision number (1 for original, 2+ for corrections)")
    superseded_by_record_id: Optional[UUID] = None
    is_latest_revision: bool = True

    task_id: str
    plan_id: Optional[str] = None
    assignment_id: Optional[str] = None
    external_authority_ref: Optional[str] = None

    actual_start_utc: datetime
    actual_restoration_utc: datetime
    actual_release_utc: Optional[datetime] = None

    quantity_completed: float
    quantity_units: str
    target_quantity: Optional[float] = None
    execution_status: ExecutionStatus

    planned_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    overrun_minutes: Optional[int] = None
    quantity_variance: Optional[float] = None

    resource_use: List[Dict[str, Any]] = Field(default_factory=list)
    still_occupied_resources: List[str] = Field(default_factory=list)
    deviation_reason: DeviationReason
    deviation_notes: Optional[str] = None

    chronology_status: ChronologyValidationStatus
    has_missing_release: bool = False
    missing_attribution_explanation: Optional[str] = None

    provenance_mode: ProvenanceMode
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)
    recorded_by_user_id: str = "system"
    content_hash: str = ""


# ──────────────────────────────────────────────
#  Governed Residual Work Schemas
# ──────────────────────────────────────────────

class ResidualWorkConfirmRequest(BaseModel):
    """
    Supervisor / Owner confirmation of residual work following partial execution.
    Prevents duplicate demands and double-counted quantities.
    """
    source_record_id: UUID
    confirmed_residual_quantity: float = Field(..., gt=0.0)
    quantity_units: str
    site_state: str = Field(..., description="Condition track was left in (e.g. BALLAST_DISTRIBUTED_UNPACKED)")
    dependencies: List[str] = Field(default_factory=list, description="New or surviving prerequisite tasks")
    applicable_deadline_utc: Optional[datetime] = None
    priority: CriticalityTier = CriticalityTier.TIER_1_MANDATORY


class ResidualWorkTask(BaseModel):
    """
    Materialized residual task eligible for feeding into next planning horizon.
    """
    residual_task_id: str
    original_task_id: str
    source_record_id: UUID
    completed_quantity: float
    residual_quantity: float
    total_target_quantity: float
    quantity_units: str
    site_state: str
    dependencies: List[str] = Field(default_factory=list)
    applicable_deadline_utc: Optional[datetime] = None
    priority: CriticalityTier
    is_confirmed: bool = True
    confirmed_by_user_id: str = "system"
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)


# ──────────────────────────────────────────────
#  Plan-vs-Actual Variance & Reconciliation
# ──────────────────────────────────────────────

class PlanVsActualVariance(BaseModel):
    """
    Defensible comparison between proposed schedule and actual recorded outcome.
    Explains missing attribution instead of fabricating delay.
    """
    task_id: str
    plan_id: Optional[str] = None
    planned_start_utc: Optional[datetime] = None
    actual_start_utc: Optional[datetime] = None
    start_delay_minutes: Optional[int] = None

    planned_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    duration_overrun_minutes: Optional[int] = None

    planned_quantity: Optional[float] = None
    actual_quantity: float
    quantity_units: str
    quantity_completion_pct: Optional[float] = None

    status: ExecutionStatus
    attribution_notes: str = ""


class ReconciliationQueueItem(BaseModel):
    """
    Conflict queue item for contradictory chronology, duplicate feeds, or unit mismatches.
    """
    conflict_id: str
    task_id: str
    conflict_type: str = Field(..., description="CHRONOLOGY_INVERSION, DUPLICATE_SOURCE, UNIT_MISMATCH, etc.")
    source_a: str
    source_b: Optional[str] = None
    description: str
    severity: str = "WARNING"  # BLOCKING or WARNING
    is_resolved: bool = False
    resolution_notes: Optional[str] = None
    created_at_utc: datetime = Field(default_factory=datetime.utcnow)


# ──────────────────────────────────────────────
#  Estimate Review & Learning Schemas
# ──────────────────────────────────────────────

class EstimateReviewSummary(BaseModel):
    """
    Deterministic variance aggregation suggesting updated duration buffer models.
    Strictly rule-based/statistical; does NOT train ML or silently mutate sealed snapshots.
    """
    task_category: str
    department: str
    sample_size: int
    mean_planned_minutes: float
    mean_actual_minutes: float
    mean_overrun_pct: float
    recommended_action: EstimateReviewRecommendation
    suggested_buffer_minutes: int
    review_notes: str
    requires_policy_revision: bool = True


class EstimateReviewResponse(BaseModel):
    summaries: List[EstimateReviewSummary]
    total_records_analyzed: int
    generated_at_utc: datetime = Field(default_factory=datetime.utcnow)
