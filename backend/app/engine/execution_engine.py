"""
Phase 16 – Execution Feedback, Partial Work, and Estimate Review Engine.

Blueprint Sections: 9, 13, 35-36.
Core Invariants:
1. Strict chronology validation: actual_start < actual_restoration <= actual_release.
2. Missing release signal is distinguished from zero duration / zero output.
3. Unit consistency enforcement; mismatched units routed to reconciliation.
4. Governed residual work creation: completed + residual == target (no double-counting).
5. Corrected outcomes append new revisions and invalidate affected active plans.
6. Still-occupied resources preserved if execution overruns.
7. Deterministic estimate review; NO ML training on fictional outcomes; snapshot immutability preserved.
"""
import hashlib
import json
import threading
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.schemas.execution import (
    ExecutionRecordCreate,
    ExecutionRecordRevisionRequest,
    ExecutionRecord,
    ExecutionStatus,
    ChronologyValidationStatus,
    DeviationReason,
    ResidualWorkConfirmRequest,
    ResidualWorkTask,
    PlanVsActualVariance,
    ReconciliationQueueItem,
    EstimateReviewRecommendation,
    EstimateReviewSummary,
    EstimateReviewResponse,
)
from app.schemas.enums import CriticalityTier, ProvenanceMode, PlanStatus
from app.engine.approval_engine import approval_engine


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class ExecutionFeedbackEngine:
    """
    Manages execution records intake, partial work residual generation,
    plan-vs-actual variance analysis, and deterministic estimate reviews.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Records: record_id (str) -> ExecutionRecord
        self._records: Dict[str, ExecutionRecord] = {}

        # Records by task_id: task_id -> list of record_id
        self._task_records: Dict[str, List[str]] = {}

        # Idempotency deduplication: key -> record_id
        self._idempotency_keys: Dict[str, str] = {}

        # Governed residual tasks: residual_task_id -> ResidualWorkTask
        self._residuals: Dict[str, ResidualWorkTask] = {}

        # Conflict reconciliation queue: conflict_id -> ReconciliationQueueItem
        self._reconciliation_queue: Dict[str, ReconciliationQueueItem] = {}

        # Known task catalog metadata (for unit verification & planned targets): task_id -> metadata
        self._task_metadata: Dict[str, Dict[str, Any]] = {}

        # Still occupied resources tracker: resource_id -> details
        self._still_occupied: Dict[str, Dict[str, Any]] = {}

    def register_task_contract(self, task_id: str, expected_units: str,
                               target_quantity: float, planned_duration_minutes: int,
                               department: str = "ENGINEERING",
                               task_category: str = "TRACK_TAMPING") -> None:
        """Register task contract expectations for unit and variance validation."""
        with self._lock:
            self._task_metadata[task_id] = {
                "expected_units": expected_units.upper(),
                "target_quantity": target_quantity,
                "planned_duration_minutes": planned_duration_minutes,
                "department": department,
                "task_category": task_category,
            }

    # ─── 1. Execution Record Intake ───────────────────

    def record_execution(self, request: ExecutionRecordCreate,
                         actor: Dict[str, Any]) -> ExecutionRecord:
        """
        Ingest an authoritative or TEST execution observation.
        Validates chronology, source consistency, units, and idempotency.
        """
        with self._lock:
            # 1. Idempotency Check
            if request.idempotency_key and request.idempotency_key in self._idempotency_keys:
                existing_id = self._idempotency_keys[request.idempotency_key]
                return self._records[existing_id]

            actor_uid = actor.get("user_id") or actor.get("sub", "system")

            # 2. Chronology Validation
            start = request.actual_start_utc
            resto = request.actual_restoration_utc
            release = request.actual_release_utc

            if start >= resto:
                # Chronology inversion error
                conflict_id = f"conf-{uuid4().hex[:8]}"
                self._reconciliation_queue[conflict_id] = ReconciliationQueueItem(
                    conflict_id=conflict_id,
                    task_id=request.task_id,
                    conflict_type="CHRONOLOGY_INVERSION",
                    source_a=f"start: {start.isoformat()}",
                    source_b=f"restoration: {resto.isoformat()}",
                    description=(
                        f"Actual start time ({start.isoformat()}) is at or after restoration "
                        f"time ({resto.isoformat()}). Chronology violated."
                    ),
                    severity="BLOCKING",
                )
                raise ValueError(
                    f"Invalid chronology: actual start ({start.isoformat()}) must strictly precede "
                    f"actual restoration ({resto.isoformat()})"
                )

            has_missing_release = False
            chronology_status = ChronologyValidationStatus.VALID

            if release is not None:
                if release < resto:
                    conflict_id = f"conf-{uuid4().hex[:8]}"
                    self._reconciliation_queue[conflict_id] = ReconciliationQueueItem(
                        conflict_id=conflict_id,
                        task_id=request.task_id,
                        conflict_type="CHRONOLOGY_INVERSION",
                        source_a=f"restoration: {resto.isoformat()}",
                        source_b=f"release: {release.isoformat()}",
                        description="Actual release precedes physical restoration to traffic condition.",
                        severity="BLOCKING",
                    )
                    raise ValueError(
                        f"Invalid chronology: actual release ({release.isoformat()}) cannot precede "
                        f"physical restoration ({resto.isoformat()})"
                    )
            else:
                # Explicit requirement: distinguish missing release from zero duration
                has_missing_release = True
                chronology_status = ChronologyValidationStatus.MISSING_RELEASE

            # 3. Unit Consistency Validation
            units = request.quantity_units.strip().upper()
            target_qty = request.target_quantity
            planned_dur = request.planned_duration_minutes

            if request.task_id in self._task_metadata:
                meta = self._task_metadata[request.task_id]
                expected_u = meta["expected_units"]
                if units != expected_u:
                    conflict_id = f"conf-{uuid4().hex[:8]}"
                    self._reconciliation_queue[conflict_id] = ReconciliationQueueItem(
                        conflict_id=conflict_id,
                        task_id=request.task_id,
                        conflict_type="UNIT_MISMATCH",
                        source_a=f"Reported: {units}",
                        source_b=f"Expected: {expected_u}",
                        description=f"Unit mismatch for task {request.task_id}: reported {units}, expected {expected_u}",
                        severity="BLOCKING",
                    )
                    raise ValueError(f"Mismatched unit: task expects '{expected_u}', reported '{units}'")
                if target_qty is None:
                    target_qty = meta["target_quantity"]
                if planned_dur is None:
                    planned_dur = meta["planned_duration_minutes"]

            # 4. Determine Execution Status
            # Invariant: A recorded block release does not prove all maintenance tasks finished.
            if target_qty is not None and target_qty > 0:
                if request.quantity_completed >= target_qty:
                    exec_status = ExecutionStatus.COMPLETED
                elif request.quantity_completed > 0:
                    exec_status = ExecutionStatus.PARTIAL
                else:
                    exec_status = ExecutionStatus.ABANDONED
            else:
                exec_status = ExecutionStatus.COMPLETED if request.quantity_completed > 0 else ExecutionStatus.ABANDONED

            # 5. Calculate Variances
            # Duration is calculated from start to restoration (not zero even if release is missing)
            actual_dur_min = int((resto - start).total_seconds() / 60)
            overrun_min = None
            if planned_dur is not None:
                overrun_min = max(0, actual_dur_min - planned_dur)

            qty_variance = None
            if target_qty is not None:
                qty_variance = request.quantity_completed - target_qty

            missing_explanation = None
            if planned_dur is None or target_qty is None:
                missing_explanation = "Missing baseline target attribution; plan-vs-actual variance bounded to observed actuals."

            # 6. Still Occupied Resources Tracking
            if request.still_occupied_resources:
                for r_id in request.still_occupied_resources:
                    self._still_occupied[r_id] = {
                        "task_id": request.task_id,
                        "occupied_since": start.isoformat(),
                        "reason": request.deviation_notes or request.deviation_reason.value,
                    }

            # 7. Materialize Execution Record
            rec_id = uuid4()
            content_payload = json.dumps({
                "record_id": str(rec_id),
                "task_id": request.task_id,
                "plan_id": request.plan_id,
                "start": start.isoformat(),
                "restoration": resto.isoformat(),
                "release": release.isoformat() if release else None,
                "completed": request.quantity_completed,
                "units": units,
                "status": exec_status.value,
            }, sort_keys=True)

            record = ExecutionRecord(
                record_id=rec_id,
                revision=1,
                is_latest_revision=True,
                task_id=request.task_id,
                plan_id=request.plan_id,
                assignment_id=request.assignment_id,
                external_authority_ref=request.external_authority_ref,
                actual_start_utc=start,
                actual_restoration_utc=resto,
                actual_release_utc=release,
                quantity_completed=request.quantity_completed,
                quantity_units=units,
                target_quantity=target_qty,
                execution_status=exec_status,
                planned_duration_minutes=planned_dur,
                actual_duration_minutes=actual_dur_min,
                overrun_minutes=overrun_min,
                quantity_variance=qty_variance,
                resource_use=request.resource_use,
                still_occupied_resources=request.still_occupied_resources,
                deviation_reason=request.deviation_reason,
                deviation_notes=request.deviation_notes,
                chronology_status=chronology_status,
                has_missing_release=has_missing_release,
                missing_attribution_explanation=missing_explanation,
                provenance_mode=request.provenance_mode,
                recorded_by_user_id=actor_uid,
                content_hash=_sha256(content_payload),
            )

            str_rec_id = str(rec_id)
            self._records[str_rec_id] = record
            if request.task_id not in self._task_records:
                self._task_records[request.task_id] = []
            self._task_records[request.task_id].append(str_rec_id)

            if request.idempotency_key:
                self._idempotency_keys[request.idempotency_key] = str_rec_id

            return record

    # ─── 2. Audited Outcome Correction ───────────────

    def revise_execution_record(self, request: ExecutionRecordRevisionRequest,
                                actor: Dict[str, Any]) -> ExecutionRecord:
        """
        Audited correction of a previously recorded outcome.
        Appends a new revision, supersedes the old record, and invalidates affected active plans.
        """
        with self._lock:
            str_old_id = str(request.record_id)
            if str_old_id not in self._records:
                raise ValueError(f"Execution record {str_old_id} not found")

            old_record = self._records[str_old_id]
            if not old_record.is_latest_revision:
                raise ValueError(f"Execution record {str_old_id} has already been superseded by a newer revision")

            actor_uid = actor.get("user_id") or actor.get("sub", "system")

            # Determine updated timestamps
            start = request.actual_start_utc or old_record.actual_start_utc
            resto = request.actual_restoration_utc or old_record.actual_restoration_utc
            release = request.actual_release_utc if request.actual_release_utc is not None else old_record.actual_release_utc

            if start >= resto:
                raise ValueError(f"Invalid chronology in correction: start must precede restoration")
            if release and release < resto:
                raise ValueError(f"Invalid chronology in correction: release cannot precede restoration")

            qty_comp = request.quantity_completed if request.quantity_completed is not None else old_record.quantity_completed
            units = (request.quantity_units or old_record.quantity_units).strip().upper()
            target_qty = old_record.target_quantity
            planned_dur = old_record.planned_duration_minutes

            # Recalculate status
            if target_qty is not None and target_qty > 0:
                if qty_comp >= target_qty:
                    exec_status = ExecutionStatus.COMPLETED
                elif qty_comp > 0:
                    exec_status = ExecutionStatus.PARTIAL
                else:
                    exec_status = ExecutionStatus.ABANDONED
            else:
                exec_status = ExecutionStatus.COMPLETED if qty_comp > 0 else ExecutionStatus.ABANDONED

            actual_dur_min = int((resto - start).total_seconds() / 60)
            overrun_min = max(0, actual_dur_min - planned_dur) if planned_dur else None
            qty_variance = (qty_comp - target_qty) if target_qty is not None else None

            new_rec_id = uuid4()
            content_payload = json.dumps({
                "record_id": str(new_rec_id),
                "task_id": old_record.task_id,
                "revision": old_record.revision + 1,
                "correction_reason": request.correction_reason,
                "completed": qty_comp,
                "units": units,
                "status": exec_status.value,
            }, sort_keys=True)

            new_record = ExecutionRecord(
                record_id=new_rec_id,
                revision=old_record.revision + 1,
                is_latest_revision=True,
                task_id=old_record.task_id,
                plan_id=old_record.plan_id,
                assignment_id=old_record.assignment_id,
                external_authority_ref=old_record.external_authority_ref,
                actual_start_utc=start,
                actual_restoration_utc=resto,
                actual_release_utc=release,
                quantity_completed=qty_comp,
                quantity_units=units,
                target_quantity=target_qty,
                execution_status=exec_status,
                planned_duration_minutes=planned_dur,
                actual_duration_minutes=actual_dur_min,
                overrun_minutes=overrun_min,
                quantity_variance=qty_variance,
                resource_use=old_record.resource_use,
                still_occupied_resources=old_record.still_occupied_resources,
                deviation_reason=request.deviation_reason or old_record.deviation_reason,
                deviation_notes=f"[Rev {old_record.revision + 1} Correction: {request.correction_reason}] " + (request.deviation_notes or old_record.deviation_notes or ""),
                chronology_status=ChronologyValidationStatus.VALID if release else ChronologyValidationStatus.MISSING_RELEASE,
                has_missing_release=release is None,
                provenance_mode=old_record.provenance_mode,
                recorded_by_user_id=actor_uid,
                content_hash=_sha256(content_payload),
            )

            # Supersede old
            old_record.is_latest_revision = False
            old_record.superseded_by_record_id = new_rec_id

            str_new_id = str(new_rec_id)
            self._records[str_new_id] = new_record
            self._task_records[old_record.task_id].append(str_new_id)

            # Invalidate affected current plans in approval engine per spec
            if old_record.plan_id and old_record.plan_id in approval_engine._plans:
                affected_plan = approval_engine._plans[old_record.plan_id]
                affected_plan["plan_status"] = PlanStatus.STALE.value
                approval_engine.bump_epoch(old_record.plan_id)

            return new_record

    # ─── 3. Governed Residual Work Creation ───────────

    def confirm_residual_work(self, request: ResidualWorkConfirmRequest,
                              actor: Dict[str, Any]) -> ResidualWorkTask:
        """
        Confirm governed residual work for partial execution.
        Strict invariant: completed_quantity + residual_quantity == target_quantity.
        Prevents duplicate demand and double-counting of productive quantity.
        """
        with self._lock:
            str_rec_id = str(request.source_record_id)
            if str_rec_id not in self._records:
                raise ValueError(f"Execution record {str_rec_id} not found")

            record = self._records[str_rec_id]
            if record.execution_status not in (ExecutionStatus.PARTIAL, ExecutionStatus.ABANDONED):
                raise ValueError(
                    f"Residual work can only be generated for PARTIAL or ABANDONED execution, "
                    f"current status is {record.execution_status.value}"
                )

            target = record.target_quantity
            if target is None:
                # If target wasn't in record, look up in metadata
                meta = self._task_metadata.get(record.task_id)
                target = meta["target_quantity"] if meta else (record.quantity_completed + request.confirmed_residual_quantity)

            # Invariant: Avoid duplicate demand and double-counted productive quantity
            expected_residual = max(0.0, target - record.quantity_completed)
            if abs(request.confirmed_residual_quantity - expected_residual) > 1e-4:
                raise ValueError(
                    f"Residual double-counting prevention: confirmed residual ({request.confirmed_residual_quantity}) "
                    f"plus completed ({record.quantity_completed}) must equal target ({target}). "
                    f"Expected residual is exactly {expected_residual} {record.quantity_units}."
                )

            actor_uid = actor.get("user_id") or actor.get("sub", "system")
            count = len([r for r in self._residuals.values() if r.original_task_id == record.task_id]) + 1
            resid_id = f"RESID-{record.task_id}-{count:02d}"

            residual_task = ResidualWorkTask(
                residual_task_id=resid_id,
                original_task_id=record.task_id,
                source_record_id=record.record_id,
                completed_quantity=record.quantity_completed,
                residual_quantity=request.confirmed_residual_quantity,
                total_target_quantity=target,
                quantity_units=record.quantity_units,
                site_state=request.site_state,
                dependencies=request.dependencies,
                applicable_deadline_utc=request.applicable_deadline_utc,
                priority=request.priority,
                is_confirmed=True,
                confirmed_by_user_id=actor_uid,
            )

            self._residuals[resid_id] = residual_task
            return residual_task

    # ─── 4. Plan-vs-Actual Variance Analysis ──────────

    def get_plan_vs_actual_variance(self, task_id: str) -> Optional[PlanVsActualVariance]:
        """
        Calculate plan-vs-actual variance. Explains missing attribution instead of inventing delay.
        """
        with self._lock:
            record_ids = self._task_records.get(task_id, [])
            if not record_ids:
                return None

            latest_rec = None
            for rid in reversed(record_ids):
                rec = self._records[rid]
                if rec.is_latest_revision:
                    latest_rec = rec
                    break

            if not latest_rec:
                return None

            # Calculate completion percentage
            pct = None
            if latest_rec.target_quantity and latest_rec.target_quantity > 0:
                pct = round((latest_rec.quantity_completed / latest_rec.target_quantity) * 100.0, 2)

            notes = latest_rec.missing_attribution_explanation or ""
            if latest_rec.deviation_notes:
                notes = f"{notes} {latest_rec.deviation_notes}".strip()

            return PlanVsActualVariance(
                task_id=task_id,
                plan_id=latest_rec.plan_id,
                planned_start_utc=None,  # Populated when linked to plan timetable
                actual_start_utc=latest_rec.actual_start_utc,
                start_delay_minutes=None,
                planned_duration_minutes=latest_rec.planned_duration_minutes,
                actual_duration_minutes=latest_rec.actual_duration_minutes,
                duration_overrun_minutes=latest_rec.overrun_minutes,
                planned_quantity=latest_rec.target_quantity,
                actual_quantity=latest_rec.quantity_completed,
                quantity_units=latest_rec.quantity_units,
                quantity_completion_pct=pct,
                status=latest_rec.execution_status,
                attribution_notes=notes or "Nominal execution reported.",
            )

    # ─── 5. Reconciliation Queue ──────────────────────

    def get_reconciliation_queue(self) -> List[ReconciliationQueueItem]:
        """Get all unresolved conflicts in the reconciliation queue."""
        with self._lock:
            return [c for c in self._reconciliation_queue.values() if not c.is_resolved]

    def resolve_reconciliation_conflict(self, conflict_id: str,
                                        resolution_notes: str,
                                        actor: Dict[str, Any]) -> ReconciliationQueueItem:
        """Resolve a reconciliation conflict with audit notes."""
        with self._lock:
            if conflict_id not in self._reconciliation_queue:
                raise ValueError(f"Conflict {conflict_id} not found in reconciliation queue")

            actor_uid = actor.get("user_id") or actor.get("sub", "system")
            item = self._reconciliation_queue[conflict_id]
            item.is_resolved = True
            item.resolution_notes = f"[Resolved by {actor_uid}]: {resolution_notes}"
            return item

    # ─── 6. Deterministic Estimate Review Workflow ────

    def generate_estimate_review(self) -> EstimateReviewResponse:
        """
        Deterministic aggregation of variance across completed records.
        Suggests updated buffer models; strictly avoids ML training on fictional outcomes.
        Preserves sealed snapshot immutability (reviewed estimates apply only to subsequent snapshots).
        """
        with self._lock:
            # Group records by category
            groups: Dict[str, List[ExecutionRecord]] = {}

            for rec in self._records.values():
                if not rec.is_latest_revision:
                    continue
                meta = self._task_metadata.get(rec.task_id, {})
                cat = meta.get("task_category", "GENERAL_MAINTENANCE")
                dept = meta.get("department", "ENGINEERING")
                group_key = f"{cat}::{dept}"

                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(rec)

            summaries: List[EstimateReviewSummary] = []

            for g_key, recs in groups.items():
                cat, dept = g_key.split("::")
                valid_recs = [r for r in recs if r.planned_duration_minutes and r.actual_duration_minutes]
                if not valid_recs:
                    continue

                sample_size = len(valid_recs)
                mean_planned = sum(r.planned_duration_minutes for r in valid_recs) / sample_size
                mean_actual = sum(r.actual_duration_minutes for r in valid_recs) / sample_size
                mean_diff = mean_actual - mean_planned
                mean_pct = round((mean_diff / mean_planned) * 100.0, 2) if mean_planned > 0 else 0.0

                if mean_pct > 15.0:
                    action = EstimateReviewRecommendation.INCREASE_BUFFER
                    suggested_buf = int(round(mean_diff))
                    notes = (
                        f"Chronic duration overrun detected (+{mean_pct}%). Tasks consistently exceed nominal window. "
                        f"Recommend expanding planning allowance by +{suggested_buf} minutes in next catalog version."
                    )
                elif mean_pct < -15.0:
                    action = EstimateReviewRecommendation.DECREASE_BUFFER
                    suggested_buf = int(round(abs(mean_diff)))
                    notes = (
                        f"Work consistently completed early ({mean_pct}%). Track possession may be over-reserved. "
                        f"Recommend reducing planning allowance by -{suggested_buf} minutes."
                    )
                else:
                    action = EstimateReviewRecommendation.MAINTAIN_CURRENT
                    suggested_buf = 0
                    notes = "Observed durations fall within standard ±15% operational tolerance. Maintain existing buffer."

                summaries.append(EstimateReviewSummary(
                    task_category=cat,
                    department=dept,
                    sample_size=sample_size,
                    mean_planned_minutes=round(mean_planned, 1),
                    mean_actual_minutes=round(mean_actual, 1),
                    mean_overrun_pct=mean_pct,
                    recommended_action=action,
                    suggested_buffer_minutes=suggested_buf,
                    review_notes=notes,
                    requires_policy_revision=action != EstimateReviewRecommendation.MAINTAIN_CURRENT,
                ))

            return EstimateReviewResponse(
                summaries=summaries,
                total_records_analyzed=len(self._records),
            )

    # ─── 7. Inspection Helpers ────────────────────────

    def get_record(self, record_id: str) -> Optional[ExecutionRecord]:
        """Get record by ID."""
        with self._lock:
            return self._records.get(record_id)

    def get_records_for_task(self, task_id: str) -> List[ExecutionRecord]:
        """Get all revisions of records for a task."""
        with self._lock:
            ids = self._task_records.get(task_id, [])
            return [self._records[rid] for rid in ids]

    def get_all_records(self) -> List[ExecutionRecord]:
        """Get all latest execution records."""
        with self._lock:
            return [r for r in self._records.values() if r.is_latest_revision]

    def get_residual_tasks(self) -> List[ResidualWorkTask]:
        """Get all confirmed residual tasks."""
        with self._lock:
            return list(self._residuals.values())

    def get_still_occupied_resources(self) -> Dict[str, Dict[str, Any]]:
        """Get all resources that remain occupied past nominal window."""
        with self._lock:
            return dict(self._still_occupied)


# Singleton instance
execution_engine = ExecutionFeedbackEngine()
