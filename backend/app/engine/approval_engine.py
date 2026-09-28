"""
Phase 15 – Human Review and Programme Approval Engine.

Implements:
- Versioned plan content hashing and ETag generation
- Atomic approval transaction with freshness checks (version epoch, hash, ETag, role)
- Separation-of-duty enforcement (admin ≠ approver, self-approval prohibited)
- Append-only audit trail with SHA-256 hash-chain linkage
- Lock management with audited revisions
- Evidence export with provenance manifest
- Idempotent duplicate command detection
- Concurrency race detection via version epoch
"""
import hashlib
import json
import threading
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime
from copy import deepcopy

from app.schemas.approval import (
    ReviewRequest, ReviewDecision, ReviewAction,
    ApprovalRequest, ApprovalResult, ApprovalAction, ApprovalBlockDetail, ApprovalBlockReason,
    ApprovalEligibilityCheck,
    PlanLock, LockCreateRequest, LockRevisionRequest, LockCategory, LockAuthority,
    AuditEvent, AuditEventType, AuditTrailResponse,
    EvidenceExport, EvidenceManifestEntry,
    SubmitForReviewRequest,
)
from app.schemas.auth import UserRole, Permission
from app.schemas.enums import PlanStatus, ProgrammeAuthorityState


def _sha256(data: str) -> str:
    """Compute SHA-256 hex digest of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _compute_plan_hash(plan_data: Dict[str, Any]) -> str:
    """Compute deterministic SHA-256 of plan content."""
    # Sort keys for deterministic serialization
    canonical = json.dumps(plan_data, sort_keys=True, default=str)
    return _sha256(canonical)


def _compute_etag(plan_id: str, version: int, epoch: int, content_hash: str) -> str:
    """Compute ETag from plan identity + version + epoch + content hash."""
    payload = f"{plan_id}:{version}:{epoch}:{content_hash}"
    return _sha256(payload)[:16]  # Short ETag


class ApprovalEngine:
    """
    Manages the complete review → approval lifecycle with atomic freshness checks,
    append-only audit trail, and concurrency protection.

    Concurrency strategy:
      A global threading.Lock protects all state mutations. The version_epoch is
      a monotonically increasing counter per plan. Any mutation (input change, lock,
      review, approval) bumps the epoch. The approval transaction re-checks the
      caller-provided expected_version_epoch against the current epoch inside the lock;
      if they differ, a CONCURRENT_MUTATION_DETECTED block is raised.

    Hash-chain:
      Each AuditEvent records previous_event_hash (the content_hash of the preceding
      event) and a monotonic chain_sequence. This provides tamper-evidence within the
      stated assumption that the application layer is not compromised. It is NOT
      DBA-proof immutability — a database administrator with direct table access
      could rewrite rows. External anchoring (e.g., periodic hash publication to
      an immutable store) would strengthen guarantees but is not implemented here.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Plan state store: plan_id -> plan data
        self._plans: Dict[str, Dict[str, Any]] = {}
        # Version epoch per plan (monotonically increasing)
        self._version_epochs: Dict[str, int] = {}

        # Reviews: plan_id -> list of ReviewDecision
        self._reviews: Dict[str, List[ReviewDecision]] = {}

        # Locks: plan_id -> list of PlanLock
        self._locks: Dict[str, List[PlanLock]] = {}

        # Approval history: plan_id -> list of ApprovalResult
        self._approvals: Dict[str, List[ApprovalResult]] = {}

        # Audit trail: ordered list of AuditEvent (append-only)
        self._audit_events: List[AuditEvent] = []
        self._chain_head_hash: str = "GENESIS"

        # Idempotency keys: set of processed keys
        self._processed_idempotency_keys: Dict[str, ApprovalResult] = {}

        # Checker results cache: plan_id -> is_valid
        self._checker_results: Dict[str, bool] = {}

    # ─── Plan Registration ───────────────────────────

    def register_plan(self, plan_id: str, plan_data: Dict[str, Any],
                      provenance_mode: str = "TEST") -> Dict[str, Any]:
        """Register a plan in the approval engine."""
        with self._lock:
            content_hash = _compute_plan_hash(plan_data)
            epoch = 1
            version = plan_data.get("plan_version_number", 1)
            etag = _compute_etag(plan_id, version, epoch, content_hash)

            self._plans[plan_id] = {
                **plan_data,
                "plan_id": plan_id,
                "content_hash": content_hash,
                "etag": etag,
                "plan_status": PlanStatus.DRAFT_PROPOSAL.value,
                "programme_authority_state": ProgrammeAuthorityState.PROPOSED.value,
                "provenance_mode": provenance_mode,
            }
            self._version_epochs[plan_id] = epoch
            self._reviews[plan_id] = []
            self._locks[plan_id] = []
            self._approvals[plan_id] = []

            return {
                "plan_id": plan_id,
                "content_hash": content_hash,
                "etag": etag,
                "version_epoch": epoch,
            }

    def register_checker_result(self, plan_id: str, is_valid: bool) -> None:
        """Record a checker validation result for a plan."""
        with self._lock:
            self._checker_results[plan_id] = is_valid
            if plan_id in self._version_epochs:
                self._version_epochs[plan_id] += 1

    def bump_epoch(self, plan_id: str) -> int:
        """Simulate an external mutation bumping the version epoch."""
        with self._lock:
            if plan_id not in self._version_epochs:
                raise ValueError(f"Plan {plan_id} not registered")
            self._version_epochs[plan_id] += 1
            # Recompute ETag
            plan = self._plans[plan_id]
            plan["etag"] = _compute_etag(
                plan_id, plan.get("plan_version_number", 1),
                self._version_epochs[plan_id], plan["content_hash"]
            )
            return self._version_epochs[plan_id]

    # ─── Submit for Review ───────────────────────────

    def submit_for_review(self, request: SubmitForReviewRequest,
                          actor: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a plan for joint review."""
        with self._lock:
            plan_id = str(request.plan_id)
            if plan_id not in self._plans:
                return {"error": "Plan not found", "plan_id": plan_id}

            plan = self._plans[plan_id]

            # Verify content hash matches
            if plan["content_hash"] != request.plan_content_hash:
                return {"error": "Content hash mismatch — plan may have been modified",
                        "plan_id": plan_id}

            # Transition to JOINT_REVIEW
            plan["plan_status"] = PlanStatus.JOINT_REVIEW.value
            self._version_epochs[plan_id] += 1
            plan["etag"] = _compute_etag(
                plan_id, request.plan_version,
                self._version_epochs[plan_id], plan["content_hash"]
            )

            # Audit
            self._append_audit(
                event_type=AuditEventType.PLAN_SUBMITTED_FOR_REVIEW,
                actor=actor,
                scope=plan_id,
                reason=request.comment,
                after_ref=json.dumps({"plan_status": plan["plan_status"],
                                       "version_epoch": self._version_epochs[plan_id]}),
            )

            return {
                "plan_id": plan_id,
                "new_status": plan["plan_status"],
                "version_epoch": self._version_epochs[plan_id],
                "etag": plan["etag"],
            }

    # ─── Review ──────────────────────────────────────

    def submit_review(self, request: ReviewRequest,
                      actor: Dict[str, Any]) -> ReviewDecision:
        """Record a review decision with immutable binding to plan content."""
        with self._lock:
            plan_id = str(request.plan_id)
            if plan_id not in self._plans:
                raise ValueError(f"Plan {plan_id} not registered")

            plan = self._plans[plan_id]

            # Verify content hash matches
            if plan["content_hash"] != request.plan_content_hash:
                raise ValueError(
                    f"Content hash mismatch: expected {plan['content_hash']}, "
                    f"got {request.plan_content_hash}. Plan may have been modified."
                )

            actor_uid = actor.get("user_id") or actor.get("sub", "system")
            actor_dname = actor.get("display_name") or actor.get("username", actor_uid)
            decision = ReviewDecision(
                plan_id=request.plan_id,
                plan_version=request.plan_version,
                plan_content_hash=request.plan_content_hash,
                checker_result_id=request.checker_result_id,
                parent_plan_id=plan.get("parent_plan_id"),
                reviewer_user_id=actor_uid,
                reviewer_display_name=actor_dname,
                reviewer_role=actor.get("roles", ["UNKNOWN"])[0] if isinstance(actor.get("roles"), list) else str(actor.get("roles", "UNKNOWN")),
                action=request.action,
                comment=request.comment,
                reviewed_assignments=request.reviewed_assignments,
            )

            self._reviews[plan_id].append(decision)
            self._version_epochs[plan_id] += 1
            plan["etag"] = _compute_etag(
                plan_id, request.plan_version,
                self._version_epochs[plan_id], plan["content_hash"]
            )

            # Update authority state if recommended
            if request.action == ReviewAction.RECOMMEND:
                plan["programme_authority_state"] = ProgrammeAuthorityState.RECOMMENDED.value

            # Audit
            self._append_audit(
                event_type=AuditEventType.REVIEW_DECISION,
                actor=actor,
                scope=plan_id,
                reason=request.comment,
                before_ref=json.dumps({"plan_status": plan["plan_status"]}),
                after_ref=json.dumps({
                    "action": request.action.value,
                    "reviewer": actor_uid,
                    "plan_content_hash": request.plan_content_hash,
                }),
                correlation_id=decision.correlation_id,
            )

            return decision

    # ─── Approval ────────────────────────────────────

    def check_eligibility(self, plan_id: str) -> ApprovalEligibilityCheck:
        """Pre-flight eligibility check for approval."""
        with self._lock:
            return self._check_eligibility_internal(plan_id)

    def _check_eligibility_internal(self, plan_id: str) -> ApprovalEligibilityCheck:
        """Internal eligibility check (must be called inside lock)."""
        if plan_id not in self._plans:
            return ApprovalEligibilityCheck(
                plan_id=UUID(plan_id) if len(plan_id) == 36 else uuid4(),
                is_eligible=False,
                block_reasons=[ApprovalBlockDetail(
                    reason=ApprovalBlockReason.CHECKER_NOT_VALID,
                    description="Plan not found",
                )],
                current_plan_hash="",
                current_version_epoch=0,
                current_etag="",
                has_valid_checker_result=False,
                has_review_recommendation=False,
                pending_reconciliation=False,
            )

        plan = self._plans[plan_id]
        epoch = self._version_epochs[plan_id]
        blocks: List[ApprovalBlockDetail] = []

        # Check checker result
        has_valid_checker = self._checker_results.get(plan_id, False)
        if not has_valid_checker:
            blocks.append(ApprovalBlockDetail(
                reason=ApprovalBlockReason.CHECKER_NOT_VALID,
                description="Plan has no valid feasibility checker result",
                navigation_target=f"/checker/{plan_id}",
            ))

        # Check review recommendation exists
        reviews = self._reviews.get(plan_id, [])
        has_recommendation = any(r.action == ReviewAction.RECOMMEND for r in reviews)
        if not has_recommendation:
            blocks.append(ApprovalBlockDetail(
                reason=ApprovalBlockReason.MISSING_REVIEW_RECOMMENDATION,
                description="No reviewer has recommended this plan for approval",
                navigation_target=f"/review/{plan_id}",
            ))

        return ApprovalEligibilityCheck(
            plan_id=UUID(plan_id),
            is_eligible=len(blocks) == 0,
            block_reasons=blocks,
            current_plan_hash=plan["content_hash"],
            current_version_epoch=epoch,
            current_etag=plan["etag"],
            has_valid_checker_result=has_valid_checker,
            has_review_recommendation=has_recommendation,
            pending_reconciliation=False,
        )

    def process_approval(self, request: ApprovalRequest,
                         actor: Dict[str, Any]) -> ApprovalResult:
        """
        Atomic approval transaction.

        Inside the lock, re-checks:
        1. Version epoch matches (no concurrent mutation)
        2. Content hash matches (plan not modified)
        3. ETag matches (optimistic concurrency)
        4. Checker result is VALID
        5. Review recommendation exists
        6. Actor has PROGRAMME_APPROVE permission
        7. Actor is NOT infrastructure admin
        8. Actor is NOT the sole reviewer (self-approval prohibited)
        """
        with self._lock:
            plan_id = str(request.plan_id)
            idempotency_key = str(request.idempotency_key)

            # Idempotency check
            if idempotency_key in self._processed_idempotency_keys:
                prev = self._processed_idempotency_keys[idempotency_key]
                # Record idempotent duplicate in audit
                self._append_audit(
                    event_type=AuditEventType.IDEMPOTENT_DUPLICATE,
                    actor=actor,
                    scope=plan_id,
                    reason=f"Duplicate idempotency key: {idempotency_key}",
                )
                return ApprovalResult(
                    success=prev.success,
                    plan_id=request.plan_id,
                    plan_version=request.plan_version,
                    action=prev.action,
                    new_plan_status=prev.new_plan_status,
                    new_authority_state=prev.new_authority_state,
                    approved_at_utc=prev.approved_at_utc,
                    approved_by=prev.approved_by,
                    audit_event_id=prev.audit_event_id,
                    was_idempotent_duplicate=True,
                )

            if plan_id not in self._plans:
                return self._fail_approval(request, actor, [
                    ApprovalBlockDetail(
                        reason=ApprovalBlockReason.CHECKER_NOT_VALID,
                        description="Plan not found",
                    )
                ])

            plan = self._plans[plan_id]
            epoch = self._version_epochs[plan_id]
            blocks: List[ApprovalBlockDetail] = []

            # 1. Version epoch check
            if request.expected_version_epoch != epoch:
                blocks.append(ApprovalBlockDetail(
                    reason=ApprovalBlockReason.CONCURRENT_MUTATION_DETECTED,
                    description=(
                        f"Version epoch mismatch: expected {request.expected_version_epoch}, "
                        f"current is {epoch}. A concurrent mutation occurred."
                    ),
                ))

            # 2. Content hash check
            if request.plan_content_hash != plan["content_hash"]:
                blocks.append(ApprovalBlockDetail(
                    reason=ApprovalBlockReason.PLAN_HASH_MISMATCH,
                    description="Plan content hash does not match current version",
                ))

            # 3. ETag check
            if request.expected_etag != plan["etag"]:
                blocks.append(ApprovalBlockDetail(
                    reason=ApprovalBlockReason.ETAG_MISMATCH,
                    description="ETag mismatch — plan may have been modified concurrently",
                ))

            # 4. Checker result
            if not self._checker_results.get(plan_id, False):
                blocks.append(ApprovalBlockDetail(
                    reason=ApprovalBlockReason.CHECKER_NOT_VALID,
                    description="Plan has no valid checker result",
                    navigation_target=f"/checker/{plan_id}",
                ))

            # 5. Review recommendation
            reviews = self._reviews.get(plan_id, [])
            has_recommendation = any(r.action == ReviewAction.RECOMMEND for r in reviews)
            if not has_recommendation:
                blocks.append(ApprovalBlockDetail(
                    reason=ApprovalBlockReason.MISSING_REVIEW_RECOMMENDATION,
                    description="No reviewer has recommended this plan",
                    navigation_target=f"/review/{plan_id}",
                ))

            # 6. Permission check
            actor_perms = actor.get("permissions", [])
            perm_values = [p.value if hasattr(p, 'value') else p for p in actor_perms]
            if Permission.PROGRAMME_APPROVE.value not in perm_values:
                blocks.append(ApprovalBlockDetail(
                    reason=ApprovalBlockReason.ROLE_INSUFFICIENT,
                    description="Actor does not have PROGRAMME_APPROVE permission",
                ))

            # 7. Infrastructure admin cannot approve
            actor_roles = actor.get("roles", [])
            role_values = [r.value if hasattr(r, 'value') else r for r in actor_roles]
            if UserRole.INFRASTRUCTURE_ADMIN.value in role_values:
                blocks.append(ApprovalBlockDetail(
                    reason=ApprovalBlockReason.ADMIN_CANNOT_APPROVE,
                    description=(
                        "Infrastructure administrator cannot approve by virtue of admin status. "
                        "A delegated approver with PROGRAMME_APPROVE authority is required."
                    ),
                ))

            # 8. Self-approval check: approver must not be the sole reviewer
            if has_recommendation:
                recommending_reviewers = [
                    r.reviewer_user_id for r in reviews
                    if r.action == ReviewAction.RECOMMEND
                ]
                actor_id = actor.get("user_id") or actor.get("sub", "")
                if recommending_reviewers and all(rid == actor_id for rid in recommending_reviewers):
                    blocks.append(ApprovalBlockDetail(
                        reason=ApprovalBlockReason.SELF_APPROVAL_PROHIBITED,
                        description="Approver is the sole recommending reviewer — separation of duty required",
                    ))

            # If any blocks, fail
            if blocks:
                return self._fail_approval(request, actor, blocks)

            # ── All checks passed — commit the approval ──
            now = datetime.utcnow()
            actor_uid = actor.get("user_id") or actor.get("sub", "system")
            actor_dname = actor.get("display_name") or actor.get("username", actor_uid)

            if request.action == ApprovalAction.APPROVE:
                plan["plan_status"] = PlanStatus.APPROVED_PROGRAMME.value
                plan["programme_authority_state"] = ProgrammeAuthorityState.OPERATING_RATIFIED.value
                plan["approved_at_utc"] = now.isoformat()
                plan["approved_by_officer"] = actor_dname
                event_type = AuditEventType.APPROVAL_GRANTED
            else:
                plan["plan_status"] = PlanStatus.DRAFT_PROPOSAL.value
                plan["programme_authority_state"] = ProgrammeAuthorityState.PROPOSED.value
                event_type = AuditEventType.APPROVAL_REJECTED

            # Bump epoch
            self._version_epochs[plan_id] += 1
            plan["etag"] = _compute_etag(
                plan_id, request.plan_version,
                self._version_epochs[plan_id], plan["content_hash"]
            )

            # Audit
            audit_event = self._append_audit(
                event_type=event_type,
                actor=actor,
                scope=plan_id,
                reason=request.comment,
                before_ref=json.dumps({"plan_status": PlanStatus.JOINT_REVIEW.value}),
                after_ref=json.dumps({
                    "plan_status": plan["plan_status"],
                    "authority_state": plan["programme_authority_state"],
                    "approver": actor_uid,
                    "plan_content_hash": request.plan_content_hash,
                }),
            )

            result = ApprovalResult(
                success=True,
                plan_id=request.plan_id,
                plan_version=request.plan_version,
                action=request.action,
                new_plan_status=plan["plan_status"],
                new_authority_state=plan["programme_authority_state"],
                approved_at_utc=now if request.action == ApprovalAction.APPROVE else None,
                approved_by=actor.get("display_name"),
                audit_event_id=audit_event.event_id,
            )

            # Store idempotency key
            self._processed_idempotency_keys[idempotency_key] = result

            return result

    def _fail_approval(self, request: ApprovalRequest,
                       actor: Dict[str, Any],
                       blocks: List[ApprovalBlockDetail]) -> ApprovalResult:
        """Record a failed approval attempt."""
        plan_id = str(request.plan_id)
        self._append_audit(
            event_type=AuditEventType.APPROVAL_ATTEMPTED,
            actor=actor,
            scope=plan_id,
            reason=f"Blocked: {', '.join(b.reason.value for b in blocks)}",
            after_ref=json.dumps([b.model_dump() for b in blocks], default=str),
        )

        result = ApprovalResult(
            success=False,
            plan_id=request.plan_id,
            plan_version=request.plan_version,
            block_reasons=blocks,
        )
        # Store idempotency key for failed attempts too
        idempotency_key = str(request.idempotency_key)
        self._processed_idempotency_keys[idempotency_key] = result
        return result

    # ─── Locks ───────────────────────────────────────

    def create_lock(self, request: LockCreateRequest,
                    actor: Dict[str, Any]) -> PlanLock:
        """Create a field-level lock on a plan assignment."""
        with self._lock:
            plan_id = str(request.plan_id)
            if plan_id not in self._plans:
                raise ValueError(f"Plan {plan_id} not registered")

            # Determine authority from actor role
            actor_roles = actor.get("roles", [])
            role_values = [r.value if hasattr(r, 'value') else r for r in actor_roles]
            if UserRole.DELEGATED_APPROVER.value in role_values:
                authority = LockAuthority.APPROVER
            elif UserRole.OPERATING_REVIEWER.value in role_values:
                authority = LockAuthority.OPERATING_REVIEWER
            elif UserRole.CORRIDOR_COORDINATOR.value in role_values:
                authority = LockAuthority.COORDINATOR
            else:
                authority = LockAuthority.PLANNER

            actor_uid = actor.get("user_id") or actor.get("sub", "system")
            actor_dname = actor.get("display_name") or actor.get("username", actor_uid)
            lock = PlanLock(
                plan_id=request.plan_id,
                assignment_id=request.assignment_id,
                lock_category=request.lock_category,
                lock_authority=authority,
                locked_by_user_id=actor_uid,
                locked_by_display_name=actor_dname,
                reason=request.reason,
            )

            self._locks[plan_id].append(lock)
            self._version_epochs[plan_id] += 1

            # Audit
            self._append_audit(
                event_type=AuditEventType.LOCK_CREATED,
                actor=actor,
                scope=f"{plan_id}/{request.assignment_id}",
                reason=request.reason,
                after_ref=json.dumps({
                    "lock_id": str(lock.lock_id),
                    "category": lock.lock_category.value,
                    "assignment_id": lock.assignment_id,
                }),
            )

            return lock

    def revise_lock(self, request: LockRevisionRequest,
                    actor: Dict[str, Any]) -> PlanLock:
        """Revise an existing lock through an audited new revision."""
        with self._lock:
            lock_id = str(request.lock_id)
            target_lock = None
            plan_id = None

            for pid, locks in self._locks.items():
                for lk in locks:
                    if str(lk.lock_id) == lock_id and lk.is_active:
                        target_lock = lk
                        plan_id = pid
                        break
                if target_lock:
                    break

            if not target_lock:
                raise ValueError(f"Active lock {lock_id} not found")

            before_ref = json.dumps({
                "reason": target_lock.reason,
                "category": target_lock.lock_category.value,
                "revision": target_lock.revision,
            })

            # Create new revision
            actor_uid = actor.get("user_id") or actor.get("sub", "system")
            actor_dname = actor.get("display_name") or actor.get("username", actor_uid)
            target_lock.revision += 1
            target_lock.reason = request.new_reason
            if request.new_category:
                target_lock.lock_category = request.new_category
            target_lock.locked_at_utc = datetime.utcnow()
            target_lock.locked_by_user_id = actor_uid
            target_lock.locked_by_display_name = actor_dname

            if plan_id:
                self._version_epochs[plan_id] += 1

            # Audit
            self._append_audit(
                event_type=AuditEventType.LOCK_REVISED,
                actor=actor,
                scope=f"{plan_id}/{target_lock.assignment_id}",
                reason=request.new_reason,
                before_ref=before_ref,
                after_ref=json.dumps({
                    "lock_id": lock_id,
                    "new_revision": target_lock.revision,
                    "new_category": target_lock.lock_category.value,
                }),
            )

            return target_lock

    def get_locks(self, plan_id: str) -> List[PlanLock]:
        """Get all active locks for a plan."""
        return [lk for lk in self._locks.get(plan_id, []) if lk.is_active]

    # ─── Audit Trail ─────────────────────────────────

    def _append_audit(self, event_type: AuditEventType,
                      actor: Dict[str, Any], scope: str,
                      reason: str = "",
                      before_ref: Optional[str] = None,
                      after_ref: Optional[str] = None,
                      correlation_id: Optional[UUID] = None) -> AuditEvent:
        """Append an immutable audit event with hash-chain linkage."""
        sequence = len(self._audit_events)

        actor_uid = actor.get("user_id") or actor.get("sub", "system")
        actor_dname = actor.get("display_name") or actor.get("username", actor_uid)

        # Compute content hash for this event
        content_payload = json.dumps({
            "event_type": event_type.value,
            "actor": actor_uid,
            "scope": scope,
            "reason": reason,
            "before_ref": before_ref,
            "after_ref": after_ref,
            "sequence": sequence,
        }, sort_keys=True, default=str)
        content_hash = _sha256(content_payload)

        actor_roles = actor.get("roles", [])
        role_str = actor_roles[0].value if actor_roles and hasattr(actor_roles[0], 'value') else (
            actor_roles[0] if actor_roles else "UNKNOWN"
        )

        event = AuditEvent(
            event_type=event_type,
            actor_user_id=actor_uid,
            actor_display_name=actor_dname,
            actor_role=role_str,
            scope=scope,
            reason=reason,
            before_ref=before_ref,
            after_ref=after_ref,
            content_hash=content_hash,
            correlation_id=correlation_id or uuid4(),
            previous_event_hash=self._chain_head_hash,
            chain_sequence=sequence,
        )

        self._audit_events.append(event)
        self._chain_head_hash = content_hash

        return event

    def get_audit_trail(self, scope_filter: Optional[str] = None,
                        limit: int = 100) -> AuditTrailResponse:
        """
        Retrieve audit trail with optional scope filter.
        Application-role permissions prohibit update/delete of history.
        """
        events = self._audit_events
        if scope_filter:
            events = [e for e in events if scope_filter in e.scope]

        # Verify chain integrity
        integrity_ok = self._verify_chain_integrity()

        return AuditTrailResponse(
            events=events[-limit:],
            total_count=len(events),
            chain_head_hash=self._chain_head_hash,
            chain_integrity_verified=integrity_ok,
        )

    def _verify_chain_integrity(self) -> bool:
        """Verify the hash-chain integrity of the audit trail."""
        expected_prev = "GENESIS"
        for event in self._audit_events:
            if event.previous_event_hash != expected_prev:
                return False
            expected_prev = event.content_hash
        return True

    # ─── Evidence Export ─────────────────────────────

    def export_evidence(self, plan_id: str,
                        actor: Dict[str, Any]) -> EvidenceExport:
        """
        Generate evidence export with provenance, status, and source/version manifest.
        The export is clearly marked as a PROGRAMME PROPOSAL — never a Railway grant.
        """
        with self._lock:
            if plan_id not in self._plans:
                raise ValueError(f"Plan {plan_id} not registered")

            plan = self._plans[plan_id]

            manifest: List[EvidenceManifestEntry] = []

            # Plan entry
            manifest.append(EvidenceManifestEntry(
                source_type="plan",
                source_id=plan_id,
                source_version=plan.get("plan_version_number", 1),
                content_hash=plan["content_hash"],
                status=plan["plan_status"],
            ))

            # Checker result entry
            checker_valid = self._checker_results.get(plan_id, False)
            manifest.append(EvidenceManifestEntry(
                source_type="checker_result",
                source_id=plan_id,
                content_hash=_sha256(f"checker:{plan_id}:{checker_valid}"),
                status="VALID" if checker_valid else "INVALID",
            ))

            # Review decisions
            for review in self._reviews.get(plan_id, []):
                manifest.append(EvidenceManifestEntry(
                    source_type="review_decision",
                    source_id=str(review.decision_id),
                    content_hash=review.plan_content_hash,
                    status=review.action.value,
                ))

            # Approval decisions
            for approval in self._approvals.get(plan_id, []):
                if approval.audit_event_id:
                    manifest.append(EvidenceManifestEntry(
                        source_type="approval_decision",
                        source_id=str(approval.audit_event_id),
                        content_hash=_sha256(f"approval:{plan_id}:{approval.action}"),
                        status=approval.action.value if approval.action else "UNKNOWN",
                    ))

            # Audit trail for this plan
            audit_events = [e for e in self._audit_events if plan_id in e.scope]

            export_content = json.dumps({
                "plan_id": plan_id,
                "manifest": [m.model_dump() for m in manifest],
                "audit_count": len(audit_events),
            }, sort_keys=True, default=str)

            actor_uid = actor.get("user_id") or actor.get("sub", "system")
            actor_dname = actor.get("display_name") or actor.get("username", actor_uid)
            export = EvidenceExport(
                plan_id=UUID(plan_id),
                plan_version=plan.get("plan_version_number", 1),
                exported_by_user_id=actor_uid,
                exported_by_display_name=actor_dname,
                plan_status=plan["plan_status"],
                programme_authority_state=plan["programme_authority_state"],
                provenance_mode=plan.get("provenance_mode", "TEST"),
                manifest=manifest,
                audit_trail_summary=audit_events[-20:],  # Last 20 events
                content_hash=_sha256(export_content),
            )

            # Audit the export itself
            self._append_audit(
                event_type=AuditEventType.EVIDENCE_EXPORTED,
                actor=actor,
                scope=plan_id,
                reason="Evidence export generated",
                after_ref=json.dumps({"export_id": str(export.export_id),
                                       "content_hash": export.content_hash}),
            )

            return export

    # ─── Read-Only Metrics (server-enforced) ─────────

    def get_plan_state(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Read-only access to plan state. No mutation path from metrics."""
        return deepcopy(self._plans.get(plan_id))

    def get_reviews(self, plan_id: str) -> List[ReviewDecision]:
        """Read-only access to review decisions."""
        return list(self._reviews.get(plan_id, []))

    def get_plan_summary(self, plan_id: str) -> Dict[str, Any]:
        """Return summary of plan status for UI."""
        plan = self._plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}
        epoch = self._version_epochs.get(plan_id, 0)
        reviews = self._reviews.get(plan_id, [])
        locks = self.get_locks(plan_id)
        return {
            "plan_id": plan_id,
            "plan_status": plan["plan_status"],
            "programme_authority_state": plan["programme_authority_state"],
            "content_hash": plan["content_hash"],
            "etag": plan["etag"],
            "version_epoch": epoch,
            "review_count": len(reviews),
            "has_recommendation": any(r.action == ReviewAction.RECOMMEND for r in reviews),
            "active_locks": len(locks),
            "checker_valid": self._checker_results.get(plan_id, False),
            "provenance_mode": plan.get("provenance_mode", "TEST"),
        }

    def seed_demo_plan(self, plan_id: str = "11111111-1111-4111-8111-111111111111") -> None:
        """Seed a demonstration plan for UI inspection and review flows."""
        plan_uuid = UUID(plan_id)
        with self._lock:
            if plan_id in self._plans:
                return

        demo_payload = {
            "plan_id": plan_id,
            "corridor_code": "VKC",
            "horizon_hours": 72,
            "total_tasks": 30,
            "assignments": [
                {"task_id": "TASK-001", "corridor": "VKC", "track_segment": "VKC-UP-01", "start_hour": 2, "end_hour": 5},
                {"task_id": "TASK-002", "corridor": "VKC", "track_segment": "VKC-DN-02", "start_hour": 3, "end_hour": 6},
                {"task_id": "TASK-003", "corridor": "VKC", "track_segment": "VKC-UP-02", "start_hour": 7, "end_hour": 10},
            ]
        }
        self.register_plan(plan_id, demo_payload, provenance_mode="PROD_EQUIVALENT")
        self.register_checker_result(plan_id, is_valid=True)

        reviewer = {
            "user_id": "usr-005-rev",
            "display_name": "S. Chatterjee (Section Controller / Operating)",
            "roles": [UserRole.OPERATING_REVIEWER.value],
            "permissions": [Permission.PROGRAMME_REVIEW.value],
        }
        self.submit_review(
            request=ReviewRequest(
                plan_id=plan_uuid,
                plan_version=1,
                plan_content_hash=self._plans[plan_id]["content_hash"],
                action=ReviewAction.RECOMMEND,
                comment="Coordinated with freight dispatch. Windows recommended with zero train path clashes.",
                reviewed_assignments=["TASK-001", "TASK-002", "TASK-003"],
            ),
            actor=reviewer,
        )

        self.create_lock(
            request=LockCreateRequest(
                plan_id=plan_uuid,
                assignment_id="TASK-001",
                lock_category=LockCategory.SCHEDULE_WINDOW,
                reason="Bridge girder replacement requiring unalterable 02:00-05:00 window",
            ),
            actor=reviewer,
        )

        # Alias for legacy or human-friendly UI identifiers
        alias_id = "plan-vkc-72h-approved"
        with self._lock:
            self._plans[alias_id] = self._plans[plan_id]
            self._version_epochs[alias_id] = self._version_epochs[plan_id]
            self._reviews[alias_id] = self._reviews[plan_id]
            self._locks[alias_id] = self._locks[plan_id]
            self._checker_results[alias_id] = True


# ── Singleton ────────────────────────────────────
approval_engine = ApprovalEngine()
approval_engine.seed_demo_plan()

