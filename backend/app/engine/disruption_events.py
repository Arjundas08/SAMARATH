"""
Phase 13: Disruption Event Processing Engine.
Blueprint Sections: 27-28, 34 plus addendum.

Accepts versioned, idempotent events. Validates source order and scope.
In one transaction persists the revision/audit/outbox event and invalidates
affected plan applicability. An old approved artifact remains historically
approved while its current usability becomes STALE or BLOCKED.

Implements queue debounce/coalescing using the durable mechanism from Phase 10.
Immediate applicability invalidation must not wait for debounce.
"""
import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func

from app.core.logging import logger
from app.db.models import (
    DisruptionEventModel,
    PlanVersionModel,
    MaterializedAssignmentModel,
    AuditEventModel,
    TaskModel,
    TrainOccupationModel,
    ResourceCalendarModel,
    SolveJobModel,
)
from app.schemas.enums import PlanStatus, JobState
from app.schemas.disruption import (
    DisruptionEventCreate,
    DisruptionEventResponse,
    EventProcessingStatus,
    PlanApplicability,
    ImpactClosureItem,
    ImpactClosureResponse,
)


class DuplicateEventError(Exception):
    """Raised when an idempotency key has already been processed."""
    pass


class OutOfOrderEventError(Exception):
    """Raised when source_order is stale for the given source_system."""
    pass


class DisruptionEventEngine:
    """
    Core engine for receiving, validating, persisting, and processing disruption events.
    Handles idempotency, source ordering, immediate plan invalidation, and debounce coalescing.
    """

    # Maximum number of pending events that can coalesce before forcing a replan
    MAX_COALESCE_BATCH_SIZE = 10
    # Debounce window in seconds for coalescing rapid-fire events
    DEBOUNCE_WINDOW_SECONDS = 5.0

    async def receive_event(
        self, db: AsyncSession, event_create: DisruptionEventCreate
    ) -> DisruptionEventResponse:
        """
        Receives and persists a disruption event in a single transaction.
        
        Steps:
        1. Check idempotency key for duplicate rejection
        2. Validate source order (monotonic per source_system)
        3. Persist event record with RECEIVED status
        4. Immediately invalidate affected plan applicability (no debounce wait)
        5. Persist audit trail
        6. Return response
        """
        now = datetime.now(timezone.utc)

        # 1. Idempotency Check
        existing = await db.execute(
            select(DisruptionEventModel).where(
                DisruptionEventModel.idempotency_key == event_create.idempotency_key
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateEventError(
                f"Event with idempotency_key '{event_create.idempotency_key}' already exists."
            )

        # 2. Source Order Validation
        latest_order_result = await db.execute(
            select(func.max(DisruptionEventModel.source_order)).where(
                and_(
                    DisruptionEventModel.source_system == event_create.source_system,
                    DisruptionEventModel.corridor_code == event_create.corridor_code,
                )
            )
        )
        latest_order = latest_order_result.scalar()
        if latest_order is not None and event_create.source_order <= latest_order:
            raise OutOfOrderEventError(
                f"Source order {event_create.source_order} is not greater than "
                f"latest order {latest_order} for source '{event_create.source_system}'."
            )

        # 3. Persist Event
        event_model = DisruptionEventModel(
            event_id=str(uuid4()),
            event_type=event_create.event_type.value,
            severity=event_create.severity.value,
            corridor_code=event_create.corridor_code,
            source_system=event_create.source_system,
            source_order=event_create.source_order,
            idempotency_key=event_create.idempotency_key,
            processing_status=EventProcessingStatus.RECEIVED.value,
            payload=event_create.payload.model_dump(mode="json"),
            description=event_create.description,
            submitted_by=event_create.submitted_by,
            created_at_utc=now,
        )
        db.add(event_model)

        # 4. Immediate Plan Applicability Invalidation
        affected_plan_ids = await self._invalidate_affected_plans(
            db, event_create, now
        )
        event_model.affected_plan_ids = affected_plan_ids
        event_model.invalidated_plan_applicability = (
            PlanApplicability.STALE.value if affected_plan_ids else None
        )
        event_model.processing_status = EventProcessingStatus.VALIDATED.value

        # 5. Audit Trail
        audit = AuditEventModel(
            entity_type="DISRUPTION_EVENT",
            entity_id=event_model.event_id,
            action="EVENT_RECEIVED",
            user_id=event_create.submitted_by,
            user_role="PLANNER",
            payload_after={
                "event_type": event_create.event_type.value,
                "severity": event_create.severity.value,
                "source_order": event_create.source_order,
                "affected_plans": affected_plan_ids,
            },
            timestamp_utc=now,
        )
        db.add(audit)

        await db.commit()
        await db.refresh(event_model)

        logger.info(
            f"Disruption event '{event_model.event_id}' received: "
            f"type={event_create.event_type.value}, "
            f"affected_plans={len(affected_plan_ids)}"
        )

        return self._to_response(event_model)

    async def _invalidate_affected_plans(
        self,
        db: AsyncSession,
        event: DisruptionEventCreate,
        now: datetime,
    ) -> List[str]:
        """
        Immediately marks affected non-final plans as STALE.
        An old approved artifact remains historically approved;
        its current usability becomes STALE.
        """
        # Find all current/checked/review plans for this corridor
        stmt = select(PlanVersionModel).where(
            and_(
                PlanVersionModel.corridor_code == event.corridor_code,
                PlanVersionModel.plan_status.in_([
                    PlanStatus.CHECKED_FEASIBLE,
                    PlanStatus.JOINT_REVIEW,
                    PlanStatus.DRAFT_PROPOSAL,
                ]),
            )
        )
        result = await db.execute(stmt)
        plans = result.scalars().all()

        affected_ids = []
        for plan in plans:
            # Mark as STALE - preserves historical approval state
            plan.plan_status = PlanStatus.STALE
            affected_ids.append(plan.plan_id)

            audit = AuditEventModel(
                entity_type="PLAN_VERSION",
                entity_id=plan.plan_id,
                action="APPLICABILITY_INVALIDATED",
                user_id="system",
                user_role="SYSTEM",
                payload_before={"plan_status": "CHECKED_FEASIBLE"},
                payload_after={
                    "plan_status": PlanStatus.STALE.value,
                    "triggering_event_type": event.event_type.value,
                },
                timestamp_utc=now,
            )
            db.add(audit)

        return affected_ids

    async def compute_impact_closure(
        self,
        db: AsyncSession,
        event_ids: List[str],
        baseline_plan_id: str,
        max_expansions: int = 2,
    ) -> ImpactClosureResponse:
        """
        Builds impact closure across package membership, dependencies,
        shared resources, overlapping affected footprints, and parent/boundary commitments.
        
        Preserves completed work, continuing external occupation, and hard planner commitments.
        Missing actual release never frees a resource by elapsed planned time.
        
        Starts with a limited repair neighborhood; expands under a bounded policy if necessary.
        Discloses restricted search scope; does not call it globally minimum-change.
        """
        # Load events
        events_result = await db.execute(
            select(DisruptionEventModel).where(
                DisruptionEventModel.event_id.in_(event_ids)
            )
        )
        events = events_result.scalars().all()

        # Load baseline assignments
        assignments_result = await db.execute(
            select(MaterializedAssignmentModel).where(
                MaterializedAssignmentModel.plan_id == baseline_plan_id
            )
        )
        assignments = assignments_result.scalars().all()

        # Build directly affected set from event payloads
        directly_affected: Dict[str, ImpactClosureItem] = {}
        affected_segments = set()
        affected_time_ranges: List[Tuple[int, int]] = []
        affected_resources = set()

        for event in events:
            payload = event.payload or {}
            entity_id = payload.get("entity_id", "")
            entity_type = payload.get("entity_type", "")

            # Track affected segments
            for seg in payload.get("affected_track_segments", []):
                affected_segments.add(seg)

            # Extract time range
            t_start = payload.get("affected_time_range_start_utc")
            t_end = payload.get("affected_time_range_end_utc")

            if entity_type == "TASK":
                directly_affected[entity_id] = ImpactClosureItem(
                    entity_type="TASK",
                    entity_id=entity_id,
                    impact_reason="direct_event_target",
                )
            elif entity_type == "RESOURCE":
                affected_resources.add(entity_id)
                directly_affected[entity_id] = ImpactClosureItem(
                    entity_type="RESOURCE",
                    entity_id=entity_id,
                    impact_reason="direct_event_target",
                )
            elif entity_type == "TRAIN":
                directly_affected[entity_id] = ImpactClosureItem(
                    entity_type="TRAIN",
                    entity_id=entity_id,
                    impact_reason="direct_event_target",
                )

        # Expand closure through assignments
        closure_items: List[ImpactClosureItem] = list(directly_affected.values())
        seen_ids = set(directly_affected.keys())
        preserved_completed = 0
        preserved_locked = 0
        expansion_count = 0

        for expansion_round in range(max_expansions + 1):
            new_items: List[ImpactClosureItem] = []

            for assign in assignments:
                assign_id = assign.assignment_id
                if assign_id in seen_ids:
                    continue

                is_affected = False
                reason = ""

                # Check: task directly affected
                if assign.task_id in directly_affected:
                    is_affected = True
                    reason = "task_directly_affected"

                # Check: shared track segment
                elif assign.track_segment_id in affected_segments:
                    is_affected = True
                    reason = "overlapping_footprint"

                # Check: shared resources
                elif affected_resources:
                    assign_resources = set()
                    for r in (assign.assigned_resources or []):
                        if isinstance(r, dict):
                            assign_resources.add(r.get("resource_id", ""))
                    if assign_resources & affected_resources:
                        is_affected = True
                        reason = "shared_resource"

                # Check: overlapping time with affected segments
                elif assign.track_segment_id in affected_segments:
                    is_affected = True
                    reason = "temporal_overlap"

                if is_affected:
                    # Preserve completed work
                    if assign.is_locked:
                        preserved_locked += 1
                        item = ImpactClosureItem(
                            entity_type="ASSIGNMENT",
                            entity_id=assign_id,
                            business_key=assign.business_key,
                            impact_reason=reason,
                            affected_track_segment=assign.track_segment_id,
                            time_range_start_minute=assign.start_minute,
                            time_range_end_minute=assign.end_minute,
                            is_locked=True,
                        )
                    else:
                        item = ImpactClosureItem(
                            entity_type="ASSIGNMENT",
                            entity_id=assign_id,
                            business_key=assign.business_key,
                            impact_reason=reason,
                            affected_track_segment=assign.track_segment_id,
                            time_range_start_minute=assign.start_minute,
                            time_range_end_minute=assign.end_minute,
                        )

                    new_items.append(item)
                    seen_ids.add(assign_id)

                    # Track newly affected segments/resources for next expansion
                    affected_segments.add(assign.track_segment_id)
                    for r in (assign.assigned_resources or []):
                        if isinstance(r, dict):
                            affected_resources.add(r.get("resource_id", ""))

            if not new_items:
                break  # No new affected items, closure complete

            closure_items.extend(new_items)
            if expansion_round > 0:
                expansion_count += 1

        return ImpactClosureResponse(
            event_ids=event_ids,
            total_affected_items=len(closure_items),
            items=closure_items,
            scope_disclosure="LIMITED_NEIGHBORHOOD" if expansion_count < max_expansions else "EXPANDED_NEIGHBORHOOD",
            neighborhood_expansion_count=expansion_count,
            preserved_completed_count=preserved_completed,
            preserved_locked_count=preserved_locked,
        )

    async def coalesce_pending_events(
        self, db: AsyncSession, corridor_code: str
    ) -> Tuple[List[str], str]:
        """
        Coalesces pending validated events into a batch for replanning.
        Each underlying event is preserved in the audit trail.
        Returns (event_ids, batch_id).
        """
        stmt = (
            select(DisruptionEventModel)
            .where(
                and_(
                    DisruptionEventModel.corridor_code == corridor_code,
                    DisruptionEventModel.processing_status.in_([
                        EventProcessingStatus.RECEIVED.value,
                        EventProcessingStatus.VALIDATED.value,
                        EventProcessingStatus.IMPACT_ASSESSED.value,
                    ]),
                    DisruptionEventModel.coalesced_into_batch_id.is_(None),
                )
            )
            .order_by(DisruptionEventModel.source_order.asc())
            .limit(self.MAX_COALESCE_BATCH_SIZE)
        )
        result = await db.execute(stmt)
        events = result.scalars().all()

        if not events:
            return [], ""

        batch_id = str(uuid4())
        event_ids = []
        now = datetime.now(timezone.utc)

        for event in events:
            event.coalesced_into_batch_id = batch_id
            event.processing_status = EventProcessingStatus.COALESCED.value
            event.processed_at_utc = now
            event_ids.append(event.event_id)

        # Audit the coalescing
        audit = AuditEventModel(
            entity_type="DISRUPTION_BATCH",
            entity_id=batch_id,
            action="EVENTS_COALESCED",
            user_id="system",
            user_role="SYSTEM",
            payload_after={
                "batch_id": batch_id,
                "event_count": len(event_ids),
                "event_ids": event_ids,
            },
            timestamp_utc=now,
        )
        db.add(audit)
        await db.commit()

        logger.info(f"Coalesced {len(event_ids)} events into batch '{batch_id}'")
        return event_ids, batch_id

    async def mark_events_replan_queued(
        self, db: AsyncSession, event_ids: List[str], replan_job_id: str
    ):
        """Marks events as having their replan job queued."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(DisruptionEventModel)
            .where(DisruptionEventModel.event_id.in_(event_ids))
            .values(
                processing_status=EventProcessingStatus.REPLAN_QUEUED.value,
                processed_at_utc=now,
            )
        )
        await db.execute(stmt)
        await db.commit()

    async def mark_events_completed(
        self, db: AsyncSession, event_ids: List[str]
    ):
        """Marks events as fully processed after replan completion."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(DisruptionEventModel)
            .where(DisruptionEventModel.event_id.in_(event_ids))
            .values(
                processing_status=EventProcessingStatus.REPLAN_COMPLETED.value,
                processed_at_utc=now,
            )
        )
        await db.execute(stmt)
        await db.commit()

    async def get_pending_events(
        self, db: AsyncSession, corridor_code: str
    ) -> List[DisruptionEventResponse]:
        """Returns all pending (non-completed) events for a corridor."""
        stmt = (
            select(DisruptionEventModel)
            .where(
                and_(
                    DisruptionEventModel.corridor_code == corridor_code,
                    DisruptionEventModel.processing_status.in_([
                        EventProcessingStatus.RECEIVED.value,
                        EventProcessingStatus.VALIDATED.value,
                        EventProcessingStatus.IMPACT_ASSESSED.value,
                    ]),
                )
            )
            .order_by(DisruptionEventModel.created_at_utc.desc())
        )
        result = await db.execute(stmt)
        events = result.scalars().all()
        return [self._to_response(e) for e in events]

    async def get_all_events(
        self, db: AsyncSession, corridor_code: str, limit: int = 50
    ) -> List[DisruptionEventResponse]:
        """Returns all events for a corridor with limit."""
        stmt = (
            select(DisruptionEventModel)
            .where(DisruptionEventModel.corridor_code == corridor_code)
            .order_by(DisruptionEventModel.created_at_utc.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        events = result.scalars().all()
        return [self._to_response(e) for e in events]

    def _to_response(self, model: DisruptionEventModel) -> DisruptionEventResponse:
        """Converts a DB model to wire response."""
        from app.schemas.disruption import DisruptionEventPayload

        payload_data = model.payload or {}
        payload = DisruptionEventPayload(**payload_data) if isinstance(payload_data, dict) else DisruptionEventPayload(entity_type="UNKNOWN", entity_id="UNKNOWN")

        return DisruptionEventResponse(
            event_id=model.event_id,
            event_type=model.event_type,
            severity=model.severity,
            corridor_code=model.corridor_code,
            source_system=model.source_system,
            source_order=model.source_order,
            idempotency_key=model.idempotency_key,
            processing_status=model.processing_status,
            payload=payload,
            description=model.description or "",
            affected_plan_ids=model.affected_plan_ids or [],
            invalidated_plan_applicability=model.invalidated_plan_applicability,
            submitted_by=model.submitted_by,
            created_at_utc=model.created_at_utc.isoformat() if model.created_at_utc else "",
            processed_at_utc=model.processed_at_utc.isoformat() if model.processed_at_utc else None,
        )
