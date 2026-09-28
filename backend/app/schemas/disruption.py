"""
Phase 13: Disruption Event and Stable Replanning Schemas.
Blueprint Sections: 27-28, 34 plus addendum.

Versioned, idempotent events for: task/criticality/deadline, train/forecast
occupation, resources, windows, rule/topology, locks/rejections, execution observations.
"""
from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
from enum import Enum
from pydantic import Field, validator

from app.schemas.common import APIModel


# --- Event Type Taxonomy ---

class DisruptionEventType(str, Enum):
    TASK_CRITICALITY_CHANGE = "TASK_CRITICALITY_CHANGE"
    TASK_DEADLINE_CHANGE = "TASK_DEADLINE_CHANGE"
    TASK_DURATION_CHANGE = "TASK_DURATION_CHANGE"
    TRAIN_OCCUPATION_CHANGE = "TRAIN_OCCUPATION_CHANGE"
    TRAIN_FORECAST_UPDATE = "TRAIN_FORECAST_UPDATE"
    RESOURCE_AVAILABILITY_CHANGE = "RESOURCE_AVAILABILITY_CHANGE"
    RESOURCE_OUTAGE = "RESOURCE_OUTAGE"
    WINDOW_CHANGE = "WINDOW_CHANGE"
    WINDOW_REVOCATION = "WINDOW_REVOCATION"
    RULE_CHANGE = "RULE_CHANGE"
    TOPOLOGY_CHANGE = "TOPOLOGY_CHANGE"
    LOCK_IMPOSED = "LOCK_IMPOSED"
    LOCK_RELEASED = "LOCK_RELEASED"
    REJECTION_ISSUED = "REJECTION_ISSUED"
    EXECUTION_OBSERVATION = "EXECUTION_OBSERVATION"
    TASK_ADDED = "TASK_ADDED"
    TASK_WITHDRAWN = "TASK_WITHDRAWN"


class EventSeverity(str, Enum):
    CRITICAL = "CRITICAL"      # Immediate safety/operational impact
    HIGH = "HIGH"              # Affects scheduled plan feasibility
    MEDIUM = "MEDIUM"          # May require adjustment
    LOW = "LOW"                # Informational / minor adjustment


class EventProcessingStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    IMPACT_ASSESSED = "IMPACT_ASSESSED"
    REPLAN_QUEUED = "REPLAN_QUEUED"
    REPLAN_COMPLETED = "REPLAN_COMPLETED"
    COALESCED = "COALESCED"    # Merged into a batch
    REJECTED = "REJECTED"


class PlanApplicability(str, Enum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    BLOCKED = "BLOCKED"


# --- Disruption Event Schemas ---

class DisruptionEventPayload(APIModel):
    """Flexible key-value payload carrying event-specific data."""
    entity_type: str                          # e.g., "TASK", "TRAIN", "RESOURCE", "WINDOW", "RULE"
    entity_id: str                            # ID of the affected entity
    field_changed: Optional[str] = None       # Specific field that changed
    previous_value: Optional[Any] = None
    new_value: Optional[Any] = None
    affected_track_segments: List[str] = Field(default_factory=list)
    affected_time_range_start_utc: Optional[str] = None
    affected_time_range_end_utc: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DisruptionEventCreate(APIModel):
    """Wire format for submitting a disruption event."""
    event_type: DisruptionEventType
    severity: EventSeverity = EventSeverity.MEDIUM
    corridor_code: str = "VKC"
    source_system: str = "MANUAL"
    source_order: int = Field(ge=0, description="Monotonic sequence number from the source system")
    idempotency_key: str = Field(default_factory=lambda: str(uuid4()))
    payload: DisruptionEventPayload
    description: str = ""
    submitted_by: str = "planner"


class DisruptionEventResponse(APIModel):
    event_id: str
    event_type: DisruptionEventType
    severity: EventSeverity
    corridor_code: str
    source_system: str
    source_order: int
    idempotency_key: str
    processing_status: EventProcessingStatus
    payload: DisruptionEventPayload
    description: str
    affected_plan_ids: List[str] = Field(default_factory=list)
    invalidated_plan_applicability: Optional[PlanApplicability] = None
    submitted_by: str
    created_at_utc: str
    processed_at_utc: Optional[str] = None


class DisruptionEventListResponse(APIModel):
    events: List[DisruptionEventResponse]
    total: int


# --- Impact Closure ---

class ImpactClosureItem(APIModel):
    """One element in the impact closure: a task or assignment affected by the event."""
    entity_type: str          # "TASK", "ASSIGNMENT", "PACKAGE", "RESOURCE"
    entity_id: str
    business_key: Optional[str] = None
    impact_reason: str        # e.g., "shared_resource", "dependency", "overlapping_footprint"
    affected_track_segment: Optional[str] = None
    time_range_start_minute: Optional[int] = None
    time_range_end_minute: Optional[int] = None
    is_completed: bool = False
    is_locked: bool = False


class ImpactClosureResponse(APIModel):
    event_ids: List[str]
    total_affected_items: int
    items: List[ImpactClosureItem]
    scope_disclosure: str = "LIMITED_NEIGHBORHOOD"  # Never claim globally minimum-change
    neighborhood_expansion_count: int = 0
    preserved_completed_count: int = 0
    preserved_locked_count: int = 0


# --- Stable Replan Request/Response ---

class StableReplanRequest(APIModel):
    """Request to trigger minimal-churn disruption recovery replanning."""
    corridor_code: str = "VKC"
    event_ids: List[str] = Field(default_factory=list, description="Specific events to replan for. Empty = all pending.")
    baseline_plan_id: str
    time_limit_seconds: float = Field(default=15.0, ge=1.0, le=120.0)
    max_neighborhood_expansions: int = Field(default=2, ge=0, le=5)
    preserve_locks: bool = True
    coalesce_pending: bool = True


class StableReplanResponse(APIModel):
    replan_job_id: str
    baseline_plan_id: str
    event_ids_processed: List[str]
    events_coalesced_count: int
    impact_closure: ImpactClosureResponse
    status: str = "REPLAN_QUEUED"
    message: str = ""


# --- Enhanced PlanDiff Schemas ---

class DiffCategory(str, Enum):
    UNCHANGED = "UNCHANGED"
    SHIFTED = "SHIFTED"              # Same resource, different time
    RESOURCE_CHANGED = "RESOURCE_CHANGED"  # Different resource, same/different time
    REPACKAGED = "REPACKAGED"        # Different package/bundle composition
    ADDED = "ADDED"                  # New assignment not in baseline
    CANCELLED = "CANCELLED"          # Explicitly cancelled
    NOW_UNSCHEDULED = "NOW_UNSCHEDULED"  # Was scheduled, now omitted (not cancelled)
    COMPLETED = "COMPLETED"          # Executed; preserved across replan


class AssignmentDiffEntry(APIModel):
    """Detailed diff entry for a single task/assignment between two plan versions."""
    task_id: str
    business_key: str
    diff_category: DiffCategory
    # Baseline (from) values
    from_plan_id: Optional[str] = None
    from_assignment_id: Optional[str] = None
    from_start_utc: Optional[str] = None
    from_end_utc: Optional[str] = None
    from_start_minute: Optional[int] = None
    from_end_minute: Optional[int] = None
    from_track_segment_id: Optional[str] = None
    from_resources: List[str] = Field(default_factory=list)
    from_package_ids: List[str] = Field(default_factory=list)
    # Target (to) values
    to_plan_id: Optional[str] = None
    to_assignment_id: Optional[str] = None
    to_start_utc: Optional[str] = None
    to_end_utc: Optional[str] = None
    to_start_minute: Optional[int] = None
    to_end_minute: Optional[int] = None
    to_track_segment_id: Optional[str] = None
    to_resources: List[str] = Field(default_factory=list)
    to_package_ids: List[str] = Field(default_factory=list)
    # Change details
    shift_minutes: Optional[int] = None
    reason_event_ids: List[str] = Field(default_factory=list)
    change_description: str = ""
    is_locked: bool = False
    is_completed: bool = False


class PlanDiffSummaryV2(APIModel):
    """Enhanced PlanDiff summary with all Phase 13 categories."""
    unchanged_count: int = 0
    shifted_count: int = 0
    resource_changed_count: int = 0
    repackaged_count: int = 0
    added_count: int = 0
    cancelled_count: int = 0
    now_unscheduled_count: int = 0
    completed_count: int = 0
    total_changes: int = 0
    churn_score: float = 0.0
    stability_ratio: float = 0.0     # unchanged / total
    scope_disclosure: str = "LIMITED_NEIGHBORHOOD"


class PlanDiffV2(APIModel):
    """Full PlanDiff between two plan versions with event linkage."""
    diff_id: str = Field(default_factory=lambda: str(uuid4()))
    from_plan_id: str
    from_plan_version: int
    to_plan_id: str
    to_plan_version: int
    summary: PlanDiffSummaryV2
    entries: List[AssignmentDiffEntry] = Field(default_factory=list)
    triggering_event_ids: List[str] = Field(default_factory=list)
    created_at_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PlanDiffRequest(APIModel):
    from_plan_id: str
    to_plan_id: str
