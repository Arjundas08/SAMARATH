"""
Phase 15 – Human Review, Programme Approval, and Audit Integrity schemas.

Covers:
- Versioned lock management (per-assignment, per-field, audited revisions)
- Atomic approval transactions with freshness epoch / ETag / hash checks
- Append-only audit trail with hash-chain linkage
- Evidence export with provenance manifest
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from pydantic import Field, field_validator

from app.schemas.common import APIModel


# ──────────────────────────────────────────────
#  Enums
# ──────────────────────────────────────────────

class ReviewAction(str, Enum):
    """Review actions available to reviewers."""
    RECOMMEND = "RECOMMEND"               # Reviewer recommends approval
    REQUEST_REVISION = "REQUEST_REVISION" # Reviewer requests changes
    REJECT = "REJECT"                     # Reviewer rejects the plan


class ApprovalAction(str, Enum):
    """Approval actions available to delegated approvers."""
    APPROVE = "APPROVE"                   # Approver ratifies the programme
    REJECT = "REJECT"                     # Approver rejects the programme


class LockCategory(str, Enum):
    """Lock categories for field-level locking of assignments."""
    SCHEDULE_WINDOW = "SCHEDULE_WINDOW"       # Start/end time is locked
    RESOURCE_ASSIGNMENT = "RESOURCE_ASSIGNMENT" # Assigned machine/crew is locked
    TRACK_ALLOCATION = "TRACK_ALLOCATION"     # Track/section allocation locked
    DURATION_ESTIMATE = "DURATION_ESTIMATE"   # Duration hours locked
    PRIORITY_OVERRIDE = "PRIORITY_OVERRIDE"   # Priority/tier override locked


class LockAuthority(str, Enum):
    """Who can create this lock category."""
    PLANNER = "PLANNER"                       # Department planner locked it
    COORDINATOR = "COORDINATOR"               # Corridor coordinator locked it
    OPERATING_REVIEWER = "OPERATING_REVIEWER" # Operating review locked it
    APPROVER = "APPROVER"                     # Approval-time lock


class AuditEventType(str, Enum):
    """Types of audit events in the append-only trail."""
    PLAN_SUBMITTED_FOR_REVIEW = "PLAN_SUBMITTED_FOR_REVIEW"
    REVIEW_DECISION = "REVIEW_DECISION"
    LOCK_CREATED = "LOCK_CREATED"
    LOCK_REVISED = "LOCK_REVISED"
    APPROVAL_ATTEMPTED = "APPROVAL_ATTEMPTED"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_REJECTED = "APPROVAL_REJECTED"
    STALENESS_DETECTED = "STALENESS_DETECTED"
    EVIDENCE_EXPORTED = "EVIDENCE_EXPORTED"
    IDEMPOTENT_DUPLICATE = "IDEMPOTENT_DUPLICATE"


class ApprovalBlockReason(str, Enum):
    """Reasons why a plan cannot be approved."""
    CHECKER_NOT_VALID = "CHECKER_NOT_VALID"
    PLAN_HASH_MISMATCH = "PLAN_HASH_MISMATCH"
    VERSION_EPOCH_STALE = "VERSION_EPOCH_STALE"
    ETAG_MISMATCH = "ETAG_MISMATCH"
    MISSING_REVIEW_RECOMMENDATION = "MISSING_REVIEW_RECOMMENDATION"
    ROLE_INSUFFICIENT = "ROLE_INSUFFICIENT"
    ADMIN_CANNOT_APPROVE = "ADMIN_CANNOT_APPROVE"
    SELF_APPROVAL_PROHIBITED = "SELF_APPROVAL_PROHIBITED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"
    MISSING_MANDATORY_EVIDENCE = "MISSING_MANDATORY_EVIDENCE"
    CONCURRENT_MUTATION_DETECTED = "CONCURRENT_MUTATION_DETECTED"
    LOCKED_CONFLICT = "LOCKED_CONFLICT"


# ──────────────────────────────────────────────
#  Lock Schemas
# ──────────────────────────────────────────────

class PlanLock(APIModel):
    """A field-level lock on a specific assignment within a plan."""
    lock_id: UUID = Field(default_factory=uuid4)
    plan_id: UUID
    assignment_id: str = Field(..., description="task_id or assignment_key being locked")
    lock_category: LockCategory
    lock_authority: LockAuthority
    locked_by_user_id: str
    locked_by_display_name: str
    locked_at_utc: datetime = Field(default_factory=datetime.utcnow)
    revision: int = 1
    reason: str = ""
    is_active: bool = True


class LockCreateRequest(APIModel):
    """Request to create a lock on assignment fields."""
    plan_id: UUID
    assignment_id: str
    lock_category: LockCategory
    reason: str = ""


class LockRevisionRequest(APIModel):
    """Request to revise (update) an existing lock through an audited new revision."""
    lock_id: UUID
    new_reason: str
    new_category: Optional[LockCategory] = None


# ──────────────────────────────────────────────
#  Review Schemas
# ──────────────────────────────────────────────

class ReviewRequest(APIModel):
    """Request body for submitting a review decision."""
    plan_id: UUID
    plan_version: int
    plan_content_hash: str = Field(..., description="SHA-256 hash of plan content at review time")
    checker_result_id: Optional[UUID] = None
    action: ReviewAction
    comment: str = ""
    reviewed_assignments: List[str] = Field(default_factory=list, description="Assignment IDs explicitly reviewed")


class ReviewDecision(APIModel):
    """A recorded review decision with immutable binding."""
    decision_id: UUID = Field(default_factory=uuid4)
    plan_id: UUID
    plan_version: int
    plan_content_hash: str
    checker_result_id: Optional[UUID] = None
    parent_plan_id: Optional[UUID] = None
    reviewer_user_id: str
    reviewer_display_name: str
    reviewer_role: str
    action: ReviewAction
    comment: str = ""
    reviewed_assignments: List[str] = Field(default_factory=list)
    decided_at_utc: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: UUID = Field(default_factory=uuid4)


# ──────────────────────────────────────────────
#  Approval Schemas
# ──────────────────────────────────────────────

class ApprovalRequest(APIModel):
    """Atomic approval request with all freshness checks."""
    plan_id: UUID
    plan_version: int
    plan_content_hash: str = Field(..., description="SHA-256 of the plan being approved")
    expected_etag: str = Field(..., description="ETag for optimistic concurrency")
    expected_version_epoch: int = Field(..., description="Version epoch to prevent stale approval")
    checker_result_valid: bool = Field(True, description="Client assertion that checker passed")
    action: ApprovalAction
    comment: str = ""
    idempotency_key: UUID = Field(default_factory=uuid4, description="Client-generated idempotency key")


class ApprovalBlockDetail(APIModel):
    """Detail about why approval is blocked."""
    reason: ApprovalBlockReason
    description: str
    navigation_target: Optional[str] = None  # Where to go to fix the issue


class ApprovalResult(APIModel):
    """Result of an approval attempt."""
    success: bool
    plan_id: UUID
    plan_version: int
    action: Optional[ApprovalAction] = None
    new_plan_status: Optional[str] = None
    new_authority_state: Optional[str] = None
    approved_at_utc: Optional[datetime] = None
    approved_by: Optional[str] = None
    block_reasons: List[ApprovalBlockDetail] = Field(default_factory=list)
    audit_event_id: Optional[UUID] = None
    was_idempotent_duplicate: bool = False


class ApprovalEligibilityCheck(APIModel):
    """Pre-flight check for whether a plan is eligible for approval."""
    plan_id: UUID
    is_eligible: bool
    block_reasons: List[ApprovalBlockDetail] = Field(default_factory=list)
    current_plan_hash: str
    current_version_epoch: int
    current_etag: str
    has_valid_checker_result: bool
    has_review_recommendation: bool
    pending_reconciliation: bool


# ──────────────────────────────────────────────
#  Audit Trail Schemas
# ──────────────────────────────────────────────

class AuditEvent(APIModel):
    """Append-only audit event with hash-chain linkage."""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: AuditEventType
    actor_user_id: str
    actor_display_name: str
    actor_role: str
    scope: str = Field(..., description="Entity scope, e.g. plan_id or lock_id")
    timestamp_utc: datetime = Field(default_factory=datetime.utcnow)
    reason: str = ""
    before_ref: Optional[str] = None  # Serialized before-state reference
    after_ref: Optional[str] = None   # Serialized after-state reference
    content_hash: str = ""            # SHA-256 of event payload
    correlation_id: UUID = Field(default_factory=uuid4)
    previous_event_hash: str = ""     # Hash-chain: hash of previous event
    chain_sequence: int = 0           # Monotonic sequence in the chain


class AuditTrailResponse(APIModel):
    """Paginated audit trail response."""
    events: List[AuditEvent] = Field(default_factory=list)
    total_count: int = 0
    chain_head_hash: str = ""
    chain_integrity_verified: bool = True


# ──────────────────────────────────────────────
#  Evidence Export Schemas
# ──────────────────────────────────────────────

class EvidenceManifestEntry(APIModel):
    """Single entry in the evidence export manifest."""
    source_type: str         # e.g. "plan", "checker_result", "review_decision"
    source_id: str
    source_version: Optional[int] = None
    content_hash: str
    status: str              # e.g. "APPROVED", "VALID", "RECOMMENDED"


class EvidenceExport(APIModel):
    """Complete evidence export with provenance and source manifest."""
    export_id: UUID = Field(default_factory=uuid4)
    plan_id: UUID
    plan_version: int
    exported_at_utc: datetime = Field(default_factory=datetime.utcnow)
    exported_by_user_id: str
    exported_by_display_name: str
    plan_status: str
    programme_authority_state: str
    provenance_mode: str                  # TEST, SYNTHETIC_SCENARIO, etc.
    disclaimer: str = (
        "This is a PROGRAMME PROPOSAL generated by the SAMARATH decision-support system. "
        "It is NOT an official Railway Block Programme Grant, Traffic Block Permit, "
        "or Signal Control Release. External authority clearance is required before "
        "any field possession or traffic block can commence."
    )
    manifest: List[EvidenceManifestEntry] = Field(default_factory=list)
    audit_trail_summary: List[AuditEvent] = Field(default_factory=list)
    content_hash: str = ""                # SHA-256 of the export payload


# ──────────────────────────────────────────────
#  Submit for Review
# ──────────────────────────────────────────────

class SubmitForReviewRequest(APIModel):
    """Submit a plan for joint review."""
    plan_id: UUID
    plan_version: int
    plan_content_hash: str
    checker_result_id: Optional[UUID] = None
    comment: str = ""
