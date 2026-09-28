"""
Engine: Sparse Opportunity and Candidate Generator.
Implements Blueprint Sections 19 & 22:
- Discretizes time into a declared lattice relative to horizon origin.
- Uses spatial and temporal indexing for train paths and resource calendars (no O(N^2) global scan).
- Resolves track footprint and multi-track neutral section isolation.
- Enforces strict hard lock equality constraints.
- Emits CandidateManifest with rich metrics, truncation protection, and sound pruning reasons.
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import time

from app.schemas.enums import CriticalityTier, CompatibilityEffect
from app.schemas.task import Task
from app.schemas.snapshot import Snapshot, TrainOccupation, ResourceCalendarEntry, LockedCommitment
from app.schemas.candidate import PlacementCandidate, CandidateManifest
from app.schemas.work_package import WorkPackage
from app.domain.packages import build_singleton_package, build_bundled_package
from app.domain.spatial import resolve_task_footprint


class CandidateGenerator:
    """
    Constructs eligible spatiotemporal placement candidates for tasks and packages.
    """

    def __init__(
        self,
        snapshot: Snapshot,
        lattice_step_minutes: int = 30,
        max_candidates: int = 20000,
    ):
        self.snapshot = snapshot
        self.lattice_step_minutes = lattice_step_minutes
        self.max_candidates = max_candidates
        self.horizon_start = snapshot.horizon_start_utc
        self.horizon_end = snapshot.horizon_end_utc

        # Total minutes in horizon
        total_seconds = int((self.horizon_end - self.horizon_start).total_seconds())
        self.horizon_total_minutes = max(0, total_seconds // 60)

        # Build Spatial-Temporal Train Index: segment_id -> List[(start_min, end_min, train_num)]
        self.train_index: Dict[str, List[Tuple[int, int, str]]] = defaultdict(list)
        for tr in snapshot.train_occupations:
            self.train_index[tr.track_segment_id].append(
                (tr.start_minute, tr.end_minute, tr.train_number)
            )

        # Build Resource Outage Index: resource_id -> List[(start_min, end_min, reason)]
        self.outage_index: Dict[str, List[Tuple[int, int, str]]] = defaultdict(list)
        for cal in snapshot.resource_calendars:
            if cal.is_outage:
                s_min = max(0, int((cal.available_start_utc - self.horizon_start).total_seconds() // 60))
                e_min = min(self.horizon_total_minutes, int((cal.available_end_utc - self.horizon_start).total_seconds() // 60))
                self.outage_index[cal.resource_id].append((s_min, e_min, cal.outage_reason or "Depot Maintenance Outage"))

        # Build Hard Lock Index: task_id -> LockedCommitment
        self.lock_index: Dict[UUID, LockedCommitment] = {}
        for lock in snapshot.locked_commitments:
            self.lock_index[lock.task_id] = lock

    def generate_manifest(self, packages: Optional[List[WorkPackage]] = None) -> CandidateManifest:
        """
        Generates sparse placement candidates across the horizon.
        """
        start_wall_time = time.perf_counter()

        # If packages not explicitly provided, build singletons from snapshot tasks
        if packages is None:
            packages = []
            for t in self.snapshot.tasks:
                packages.append(build_singleton_package(t))

        candidates: List[PlacementCandidate] = []
        evaluated_windows = 0
        train_conflict_pruned = 0
        resource_outage_pruned = 0
        lock_mismatch_pruned = 0
        deadline_exceeded_pruned = 0
        is_truncated = False
        truncation_reason = None

        cand_counter = 1

        for pkg in packages:
            if not pkg.is_eligible:
                continue

            duration_min = pkg.recipe.total_duration_minutes
            if duration_min <= 0 or duration_min > self.horizon_total_minutes:
                continue

            # Determine earliest release and latest deadline across package tasks
            pkg_tasks = [t for t in self.snapshot.tasks if t.task_id in pkg.task_ids]
            if not pkg_tasks:
                continue

            latest_deadline_utc = min(t.deadline_utc for t in pkg_tasks)
            latest_deadline_min = int((latest_deadline_utc - self.horizon_start).total_seconds() // 60)

            # Check if any task in package is locked
            locked_starts = [
                int((self.lock_index[t.task_id].start_utc - self.horizon_start).total_seconds() // 60)
                for t in pkg_tasks
                if t.task_id in self.lock_index
            ]

            # Resolve track footprint for power block / neutral section
            fp = resolve_task_footprint(
                pkg.track_segment_id,
                pkg.chainage_start_km,
                pkg.chainage_end_km,
                pkg.requires_power_block,
                pkg.power_block_elementary_section,
            )
            affected_segments = [pkg.track_segment_id] + fp.affected_adjacent_tracks

            # Required resources for package
            required_res = list({
                r
                for phase in pkg.recipe.phases
                for r in phase.required_resources
            })

            # Scan start times along the lattice
            max_start = self.horizon_total_minutes - duration_min

            # If locked, only evaluate locked start minute!
            if locked_starts:
                start_ticks = [locked_starts[0]]
            else:
                start_ticks = range(0, max_start + 1, self.lattice_step_minutes)

            for s_min in start_ticks:
                evaluated_windows += 1
                e_min = s_min + duration_min

                # 1. Deadline check
                if e_min > latest_deadline_min:
                    deadline_exceeded_pruned += 1
                    continue

                # 2. Hard lock check
                if locked_starts and s_min != locked_starts[0]:
                    lock_mismatch_pruned += 1
                    continue

                # 3. Train conflict check on all affected track segments
                has_train_conflict = False
                for seg in affected_segments:
                    for t_start, t_end, train_num in self.train_index.get(seg, []):
                        # Half-open interval intersection: max(s_min, t_start) < min(e_min, t_end)
                        if max(s_min, t_start) < min(e_min, t_end):
                            has_train_conflict = True
                            break
                    if has_train_conflict:
                        break

                if has_train_conflict:
                    train_conflict_pruned += 1
                    continue

                # 4. Resource outage check
                has_resource_outage = False
                for r_id in required_res:
                    for o_start, o_end, o_reason in self.outage_index.get(r_id, []):
                        if max(s_min, o_start) < min(e_min, o_end):
                            has_resource_outage = True
                            break
                    if has_resource_outage:
                        break

                if has_resource_outage:
                    resource_outage_pruned += 1
                    continue

                # Feasible candidate placement found!
                start_utc = self.horizon_start + timedelta(minutes=s_min)
                end_utc = self.horizon_start + timedelta(minutes=e_min)

                is_locked_cand = bool(locked_starts)
                lock_text = self.lock_index[pkg_tasks[0].task_id].lock_reason if is_locked_cand else None

                cand = PlacementCandidate(
                    candidate_id=f"CAND-{cand_counter:05d}",
                    package_id=pkg.package_id,
                    task_ids=pkg.task_ids,
                    business_keys=pkg.business_keys,
                    track_segment_id=pkg.track_segment_id,
                    start_utc=start_utc,
                    end_utc=end_utc,
                    start_minute=s_min,
                    end_minute=e_min,
                    duration_minutes=duration_min,
                    start_second=s_min * 60,
                    end_second=e_min * 60,
                    duration_seconds=duration_min * 60,
                    assigned_resources=required_res,
                    phases=pkg.recipe.phases,
                    is_locked=is_locked_cand,
                    lock_reason=lock_text,
                    requires_power_block=pkg.requires_power_block,
                    power_block_elementary_section=pkg.power_block_elementary_section,
                    isolated_tracks=fp.affected_adjacent_tracks,
                    shadow_with_task_id=pkg.task_ids[1] if len(pkg.task_ids) > 1 else None,
                    is_valid_prefilter=True,
                    train_conflict_penalty=0.0,
                )
                candidates.append(cand)
                cand_counter += 1

                if len(candidates) >= self.max_candidates:
                    is_truncated = True
                    truncation_reason = f"DOMAIN_TRUNCATED: Generated candidate ceiling ({self.max_candidates}) reached. Remaining domain safely pruned."
                    break

            if is_truncated:
                break

        elapsed_ms = (time.perf_counter() - start_wall_time) * 1000.0

        return CandidateManifest(
            manifest_id=uuid4(),
            snapshot_id=self.snapshot.snapshot_id,
            total_candidates=len(candidates),
            candidates=candidates,
            is_truncated=is_truncated,
            truncation_reason=truncation_reason,
            generation_duration_ms=round(elapsed_ms, 2),
            metrics={
                "evaluated_windows": evaluated_windows,
                "train_conflict_pruned": train_conflict_pruned,
                "resource_outage_pruned": resource_outage_pruned,
                "lock_mismatch_pruned": lock_mismatch_pruned,
                "deadline_exceeded_pruned": deadline_exceeded_pruned,
                "accepted_candidates": len(candidates),
                "lattice_step_minutes": self.lattice_step_minutes,
                "generation_duration_ms": round(elapsed_ms, 2),
            },
        )
