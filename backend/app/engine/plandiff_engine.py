"""
Phase 13: PlanDiff Engine.
Blueprint Sections: 27-28, 34 plus addendum.

Calculates PlanDiff: unchanged, shifted, resource_changed, repackaged,
added, cancelled, now_unscheduled, and completed.

Stores from/to versions and reason/event links.
Distinguishes actual cancellation from an omitted assignment and from residual work.
"""
from datetime import datetime, timezone
from typing import List, Dict, Optional, Set, Tuple, Any
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logging import logger
from app.db.models import (
    PlanVersionModel,
    MaterializedAssignmentModel,
    PlanDiffModel,
    AuditEventModel,
)
from app.schemas.disruption import (
    DiffCategory,
    AssignmentDiffEntry,
    PlanDiffSummaryV2,
    PlanDiffV2,
)


class PlanDiffEngine:
    """
    Computes a comprehensive diff between two plan versions.
    
    Categories:
    - UNCHANGED: Same task, same time, same resource, same package
    - SHIFTED: Same task/resource but different time slot
    - RESOURCE_CHANGED: Same task but different resource assignment
    - REPACKAGED: Same task but different package/bundle composition
    - ADDED: New assignment not in baseline
    - CANCELLED: Explicitly cancelled (task withdrawn)
    - NOW_UNSCHEDULED: Was scheduled in baseline, omitted in target (not cancelled)
    - COMPLETED: Executed work preserved across replan
    
    "Changed" is defined as time/resource/recipe/week/removal changes,
    not only a moved start. Added work is kept separate in denominators.
    """

    # Tolerance for considering time "unchanged" (in minutes)
    TIME_TOLERANCE_MINUTES = 0

    async def compute_diff(
        self,
        db: AsyncSession,
        from_plan_id: str,
        to_plan_id: str,
        triggering_event_ids: Optional[List[str]] = None,
        cancelled_task_ids: Optional[Set[str]] = None,
        completed_task_ids: Optional[Set[str]] = None,
    ) -> PlanDiffV2:
        """
        Computes a full diff between two plan versions.
        
        Args:
            from_plan_id: Baseline plan
            to_plan_id: Target plan (result of replanning)
            triggering_event_ids: Events that triggered the replan
            cancelled_task_ids: Tasks explicitly cancelled (distinct from unscheduled)
            completed_task_ids: Tasks that were completed and preserved
        """
        cancelled_task_ids = cancelled_task_ids or set()
        completed_task_ids = completed_task_ids or set()
        triggering_event_ids = triggering_event_ids or []

        # Load plan versions
        from_plan = await self._load_plan(db, from_plan_id)
        to_plan = await self._load_plan(db, to_plan_id)

        if not from_plan or not to_plan:
            raise ValueError(f"Plan not found: from={from_plan_id}, to={to_plan_id}")

        # Load assignments
        from_assignments = await self._load_assignments(db, from_plan_id)
        to_assignments = await self._load_assignments(db, to_plan_id)

        # Build task-indexed maps
        from_by_task: Dict[str, MaterializedAssignmentModel] = {
            a.task_id: a for a in from_assignments
        }
        to_by_task: Dict[str, MaterializedAssignmentModel] = {
            a.task_id: a for a in to_assignments
        }

        all_task_ids = set(from_by_task.keys()) | set(to_by_task.keys())

        entries: List[AssignmentDiffEntry] = []

        for task_id in sorted(all_task_ids):
            from_assign = from_by_task.get(task_id)
            to_assign = to_by_task.get(task_id)

            entry = self._classify_assignment(
                task_id=task_id,
                from_assign=from_assign,
                to_assign=to_assign,
                from_plan_id=from_plan_id,
                to_plan_id=to_plan_id,
                cancelled_task_ids=cancelled_task_ids,
                completed_task_ids=completed_task_ids,
                triggering_event_ids=triggering_event_ids,
            )
            entries.append(entry)

        # Compute summary
        summary = self._compute_summary(entries, all_task_ids)

        diff = PlanDiffV2(
            diff_id=str(uuid4()),
            from_plan_id=from_plan_id,
            from_plan_version=from_plan.plan_version_number,
            to_plan_id=to_plan_id,
            to_plan_version=to_plan.plan_version_number,
            summary=summary,
            entries=entries,
            triggering_event_ids=triggering_event_ids,
        )

        # Persist the diff
        await self._persist_diff(db, diff)

        logger.info(
            f"PlanDiff computed: {from_plan_id} -> {to_plan_id}, "
            f"unchanged={summary.unchanged_count}, "
            f"shifted={summary.shifted_count}, "
            f"resource_changed={summary.resource_changed_count}, "
            f"added={summary.added_count}, "
            f"cancelled={summary.cancelled_count}, "
            f"unscheduled={summary.now_unscheduled_count}, "
            f"churn={summary.churn_score:.3f}"
        )

        return diff

    def _classify_assignment(
        self,
        task_id: str,
        from_assign: Optional[MaterializedAssignmentModel],
        to_assign: Optional[MaterializedAssignmentModel],
        from_plan_id: str,
        to_plan_id: str,
        cancelled_task_ids: Set[str],
        completed_task_ids: Set[str],
        triggering_event_ids: List[str],
    ) -> AssignmentDiffEntry:
        """Classifies a single task's change between two plans."""

        # Case: COMPLETED (preserved executed work)
        if task_id in completed_task_ids:
            assign = from_assign or to_assign
            return AssignmentDiffEntry(
                task_id=task_id,
                business_key=assign.business_key if assign else task_id,
                diff_category=DiffCategory.COMPLETED,
                from_plan_id=from_plan_id if from_assign else None,
                from_assignment_id=from_assign.assignment_id if from_assign else None,
                from_start_utc=from_assign.start_utc.isoformat() if from_assign and from_assign.start_utc else None,
                from_end_utc=from_assign.end_utc.isoformat() if from_assign and from_assign.end_utc else None,
                from_start_minute=from_assign.start_minute if from_assign else None,
                from_end_minute=from_assign.end_minute if from_assign else None,
                to_plan_id=to_plan_id if to_assign else None,
                to_assignment_id=to_assign.assignment_id if to_assign else None,
                to_start_utc=to_assign.start_utc.isoformat() if to_assign and to_assign.start_utc else None,
                to_end_utc=to_assign.end_utc.isoformat() if to_assign and to_assign.end_utc else None,
                to_start_minute=to_assign.start_minute if to_assign else None,
                to_end_minute=to_assign.end_minute if to_assign else None,
                is_completed=True,
                change_description="Completed work preserved across replan",
                reason_event_ids=triggering_event_ids,
            )

        # Case: ADDED - only in target plan
        if not from_assign and to_assign:
            return AssignmentDiffEntry(
                task_id=task_id,
                business_key=to_assign.business_key,
                diff_category=DiffCategory.ADDED,
                to_plan_id=to_plan_id,
                to_assignment_id=to_assign.assignment_id,
                to_start_utc=to_assign.start_utc.isoformat() if to_assign.start_utc else None,
                to_end_utc=to_assign.end_utc.isoformat() if to_assign.end_utc else None,
                to_start_minute=to_assign.start_minute,
                to_end_minute=to_assign.end_minute,
                to_track_segment_id=to_assign.track_segment_id,
                to_resources=self._extract_resource_ids(to_assign),
                change_description="New assignment added in target plan",
                reason_event_ids=triggering_event_ids,
            )

        # Case: CANCELLED or NOW_UNSCHEDULED - only in baseline
        if from_assign and not to_assign:
            if task_id in cancelled_task_ids:
                category = DiffCategory.CANCELLED
                desc = "Task explicitly cancelled"
            else:
                category = DiffCategory.NOW_UNSCHEDULED
                desc = "Was scheduled but now omitted (not explicitly cancelled)"

            return AssignmentDiffEntry(
                task_id=task_id,
                business_key=from_assign.business_key,
                diff_category=category,
                from_plan_id=from_plan_id,
                from_assignment_id=from_assign.assignment_id,
                from_start_utc=from_assign.start_utc.isoformat() if from_assign.start_utc else None,
                from_end_utc=from_assign.end_utc.isoformat() if from_assign.end_utc else None,
                from_start_minute=from_assign.start_minute,
                from_end_minute=from_assign.end_minute,
                from_track_segment_id=from_assign.track_segment_id,
                from_resources=self._extract_resource_ids(from_assign),
                is_locked=from_assign.is_locked,
                change_description=desc,
                reason_event_ids=triggering_event_ids,
            )

        # Both exist - compare for changes
        assert from_assign is not None and to_assign is not None

        time_changed = self._is_time_changed(from_assign, to_assign)
        resource_changed = self._is_resource_changed(from_assign, to_assign)
        package_changed = self._is_package_changed(from_assign, to_assign)

        if not time_changed and not resource_changed and not package_changed:
            category = DiffCategory.UNCHANGED
            desc = "No changes between plan versions"
        elif resource_changed and not time_changed:
            category = DiffCategory.RESOURCE_CHANGED
            desc = "Resource assignment changed"
        elif package_changed and not time_changed and not resource_changed:
            category = DiffCategory.REPACKAGED
            desc = "Package composition changed"
        elif time_changed:
            category = DiffCategory.SHIFTED
            desc = f"Time shifted by {to_assign.start_minute - from_assign.start_minute} minutes"
        else:
            category = DiffCategory.SHIFTED
            desc = "Multiple attributes changed"

        shift = (to_assign.start_minute - from_assign.start_minute) if time_changed else 0

        return AssignmentDiffEntry(
            task_id=task_id,
            business_key=from_assign.business_key,
            diff_category=category,
            from_plan_id=from_plan_id,
            from_assignment_id=from_assign.assignment_id,
            from_start_utc=from_assign.start_utc.isoformat() if from_assign.start_utc else None,
            from_end_utc=from_assign.end_utc.isoformat() if from_assign.end_utc else None,
            from_start_minute=from_assign.start_minute,
            from_end_minute=from_assign.end_minute,
            from_track_segment_id=from_assign.track_segment_id,
            from_resources=self._extract_resource_ids(from_assign),
            from_package_ids=[str(t) for t in (from_assign.bundled_with_task_ids or [])],
            to_plan_id=to_plan_id,
            to_assignment_id=to_assign.assignment_id,
            to_start_utc=to_assign.start_utc.isoformat() if to_assign.start_utc else None,
            to_end_utc=to_assign.end_utc.isoformat() if to_assign.end_utc else None,
            to_start_minute=to_assign.start_minute,
            to_end_minute=to_assign.end_minute,
            to_track_segment_id=to_assign.track_segment_id,
            to_resources=self._extract_resource_ids(to_assign),
            to_package_ids=[str(t) for t in (to_assign.bundled_with_task_ids or [])],
            shift_minutes=shift,
            is_locked=from_assign.is_locked or to_assign.is_locked,
            change_description=desc,
            reason_event_ids=triggering_event_ids if category != DiffCategory.UNCHANGED else [],
        )

    def _is_time_changed(
        self, a: MaterializedAssignmentModel, b: MaterializedAssignmentModel
    ) -> bool:
        """Time changed means start_minute or end_minute differs beyond tolerance."""
        return (
            abs(a.start_minute - b.start_minute) > self.TIME_TOLERANCE_MINUTES
            or abs(a.end_minute - b.end_minute) > self.TIME_TOLERANCE_MINUTES
        )

    def _is_resource_changed(
        self, a: MaterializedAssignmentModel, b: MaterializedAssignmentModel
    ) -> bool:
        """Resource changed means different resource IDs assigned."""
        a_resources = set(self._extract_resource_ids(a))
        b_resources = set(self._extract_resource_ids(b))
        return a_resources != b_resources

    def _is_package_changed(
        self, a: MaterializedAssignmentModel, b: MaterializedAssignmentModel
    ) -> bool:
        """Package changed means different bundle composition."""
        a_bundle = set(str(t) for t in (a.bundled_with_task_ids or []))
        b_bundle = set(str(t) for t in (b.bundled_with_task_ids or []))
        return a_bundle != b_bundle

    def _extract_resource_ids(self, assign: MaterializedAssignmentModel) -> List[str]:
        """Extracts resource IDs from an assignment's assigned_resources JSON."""
        resources = []
        for r in (assign.assigned_resources or []):
            if isinstance(r, dict):
                resources.append(r.get("resource_id", "unknown"))
            elif isinstance(r, str):
                resources.append(r)
        return resources

    def _compute_summary(
        self, entries: List[AssignmentDiffEntry], all_task_ids: Set[str]
    ) -> PlanDiffSummaryV2:
        """Computes summary statistics from diff entries."""
        counts = {cat: 0 for cat in DiffCategory}
        for entry in entries:
            counts[DiffCategory(entry.diff_category)] += 1

        total = len(entries)
        unchanged = counts[DiffCategory.UNCHANGED]
        added = counts[DiffCategory.ADDED]

        # Changed = total - unchanged - completed - added (added is separate in denominator)
        # Churn score = changed / (total - added) if total > added else 0
        denominator = total - added
        changed = denominator - unchanged - counts[DiffCategory.COMPLETED]
        churn_score = changed / denominator if denominator > 0 else 0.0
        stability_ratio = unchanged / denominator if denominator > 0 else 1.0

        return PlanDiffSummaryV2(
            unchanged_count=unchanged,
            shifted_count=counts[DiffCategory.SHIFTED],
            resource_changed_count=counts[DiffCategory.RESOURCE_CHANGED],
            repackaged_count=counts[DiffCategory.REPACKAGED],
            added_count=added,
            cancelled_count=counts[DiffCategory.CANCELLED],
            now_unscheduled_count=counts[DiffCategory.NOW_UNSCHEDULED],
            completed_count=counts[DiffCategory.COMPLETED],
            total_changes=changed,
            churn_score=round(churn_score, 4),
            stability_ratio=round(stability_ratio, 4),
            scope_disclosure="LIMITED_NEIGHBORHOOD",
        )

    async def _load_plan(self, db: AsyncSession, plan_id: str) -> Optional[PlanVersionModel]:
        result = await db.execute(
            select(PlanVersionModel).where(PlanVersionModel.plan_id == plan_id)
        )
        return result.scalar_one_or_none()

    async def _load_assignments(
        self, db: AsyncSession, plan_id: str
    ) -> List[MaterializedAssignmentModel]:
        result = await db.execute(
            select(MaterializedAssignmentModel).where(
                MaterializedAssignmentModel.plan_id == plan_id
            )
        )
        return list(result.scalars().all())

    async def _persist_diff(self, db: AsyncSession, diff: PlanDiffV2):
        """Persists a computed diff to the database."""
        diff_model = PlanDiffModel(
            diff_id=diff.diff_id,
            from_plan_id=diff.from_plan_id,
            from_plan_version=diff.from_plan_version,
            to_plan_id=diff.to_plan_id,
            to_plan_version=diff.to_plan_version,
            summary=diff.summary.model_dump(mode="json"),
            entries=[e.model_dump(mode="json") for e in diff.entries],
            triggering_event_ids=diff.triggering_event_ids,
            created_at_utc=datetime.now(timezone.utc),
        )
        db.add(diff_model)

        audit = AuditEventModel(
            entity_type="PLAN_DIFF",
            entity_id=diff.diff_id,
            action="DIFF_COMPUTED",
            user_id="system",
            user_role="SYSTEM",
            payload_after={
                "from_plan_id": diff.from_plan_id,
                "to_plan_id": diff.to_plan_id,
                "total_entries": len(diff.entries),
                "churn_score": diff.summary.churn_score,
            },
            timestamp_utc=datetime.now(timezone.utc),
        )
        db.add(audit)
        await db.commit()

    async def get_diff(self, db: AsyncSession, diff_id: str) -> Optional[PlanDiffV2]:
        """Retrieves a persisted diff by ID."""
        result = await db.execute(
            select(PlanDiffModel).where(PlanDiffModel.diff_id == diff_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None

        return PlanDiffV2(
            diff_id=model.diff_id,
            from_plan_id=model.from_plan_id,
            from_plan_version=model.from_plan_version,
            to_plan_id=model.to_plan_id,
            to_plan_version=model.to_plan_version,
            summary=PlanDiffSummaryV2(**model.summary),
            entries=[AssignmentDiffEntry(**e) for e in model.entries],
            triggering_event_ids=model.triggering_event_ids or [],
            created_at_utc=model.created_at_utc.isoformat() if model.created_at_utc else "",
        )

    async def get_diffs_for_plan(
        self, db: AsyncSession, plan_id: str
    ) -> List[PlanDiffV2]:
        """Returns all diffs where this plan is either source or target."""
        from sqlalchemy import or_
        result = await db.execute(
            select(PlanDiffModel).where(
                or_(
                    PlanDiffModel.from_plan_id == plan_id,
                    PlanDiffModel.to_plan_id == plan_id,
                )
            ).order_by(PlanDiffModel.created_at_utc.desc())
        )
        models = result.scalars().all()
        diffs = []
        for model in models:
            diffs.append(PlanDiffV2(
                diff_id=model.diff_id,
                from_plan_id=model.from_plan_id,
                from_plan_version=model.from_plan_version,
                to_plan_id=model.to_plan_id,
                to_plan_version=model.to_plan_version,
                summary=PlanDiffSummaryV2(**model.summary),
                entries=[AssignmentDiffEntry(**e) for e in model.entries],
                triggering_event_ids=model.triggering_event_ids or [],
                created_at_utc=model.created_at_utc.isoformat() if model.created_at_utc else "",
            ))
        return diffs
