"""
Engine: Coordinated Greedy Baseline Solver.
Implements Blueprint Sections 19 & 22:
- Priority-first: TIER_1_MANDATORY sorted by deadline, then TIER_2, then TIER_3.
- Compatible bundling: can select multi-department bundled candidates.
- Preserves hard lock commitments strictly.
- Enforces at-most-once task coverage and collision-free track and resource schedules.
- Includes one bounded repair pass: evicts lower-tier routine work to place blocked mandatory work.
- If mandatory coverage fails, reports BASELINE_NO_FEASIBLE_PLAN_FOUND (honest benchmark).
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone
from collections import defaultdict
import time
from pydantic import BaseModel, Field

from app.schemas.enums import CriticalityTier
from app.schemas.snapshot import Snapshot
from app.schemas.candidate import PlacementCandidate, CandidateManifest
from app.schemas.task import Task


class BaselineAssignment(BaseModel):
    assignment_id: str
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
    assigned_resources: List[str]
    isolated_tracks: List[str] = Field(default_factory=list)
    is_locked: bool = False
    is_bundled: bool = False


class BaselineSolveResult(BaseModel):
    solver_status: str
    is_feasible: bool
    total_tasks_count: int
    scheduled_tasks_count: int
    mandatory_total_count: int
    mandatory_scheduled_count: int
    total_block_minutes_scheduled: int
    assignments: List[BaselineAssignment]
    unscheduled_tasks: List[Dict[str, Any]]
    solve_duration_ms: float
    metrics: Dict[str, Any] = Field(default_factory=dict)


class GreedyBaselineSolver:
    def __init__(self, snapshot: Snapshot, manifest: CandidateManifest):
        self.snapshot = snapshot
        self.manifest = manifest
        self.candidates_by_task: Dict[UUID, List[PlacementCandidate]] = defaultdict(list)
        for c in manifest.candidates:
            for tid in c.task_ids:
                self.candidates_by_task[tid].append(c)

    def solve(self) -> BaselineSolveResult:
        start_time = time.perf_counter()

        scheduled_assignments: List[BaselineAssignment] = []
        covered_task_ids: Set[UUID] = set()

        # Track segment intervals: seg_id -> List[(start_min, end_min, assignment_idx)]
        track_occ: Dict[str, List[Tuple[int, int, int]]] = defaultdict(list)
        # Resource intervals: res_id -> List[(start_min, end_min, assignment_idx)]
        res_occ: Dict[str, List[Tuple[int, int, int]]] = defaultdict(list)

        # Helper: check interval clash
        def has_track_clash(tracks: List[str], s: int, e: int) -> bool:
            for trk in tracks:
                for cs, ce, _ in track_occ.get(trk, []):
                    if max(s, cs) < min(e, ce):
                        return True
            return False

        def has_resource_clash(resources: List[str], s: int, e: int) -> bool:
            for r in resources:
                for cs, ce, _ in res_occ.get(r, []):
                    if max(s, cs) < min(e, ce):
                        return True
            return False

        def commit_candidate(c: PlacementCandidate, is_locked: bool = False) -> int:
            idx = len(scheduled_assignments)
            assign = BaselineAssignment(
                assignment_id=f"BASE-ASSIGN-{idx+1:04d}",
                candidate_id=c.candidate_id,
                package_id=c.package_id,
                task_ids=c.task_ids,
                business_keys=c.business_keys,
                track_segment_id=c.track_segment_id,
                start_utc=c.start_utc,
                end_utc=c.end_utc,
                start_minute=c.start_minute,
                end_minute=c.end_minute,
                duration_minutes=c.duration_minutes,
                assigned_resources=c.assigned_resources,
                isolated_tracks=c.isolated_tracks,
                is_locked=is_locked or c.is_locked,
                is_bundled=len(c.task_ids) > 1,
            )
            scheduled_assignments.append(assign)
            for tid in c.task_ids:
                covered_task_ids.add(tid)

            for trk in set([c.track_segment_id] + c.isolated_tracks):
                track_occ[trk].append((c.start_minute, c.end_minute, idx))
            for r in c.assigned_resources:
                res_occ[r].append((c.start_minute, c.end_minute, idx))
            return idx

        # 1. Step 1: Enforce Hard Locked Commitments
        for lock in self.snapshot.locked_commitments:
            lock_min = int((lock.start_utc - self.snapshot.horizon_start_utc).total_seconds() // 60)
            # Find candidate matching lock
            matching_cands = [
                c for c in self.candidates_by_task.get(lock.task_id, [])
                if c.start_minute == lock_min
            ]
            if matching_cands:
                chosen = matching_cands[0]
                commit_candidate(chosen, is_locked=True)

        # 2. Step 2: Sort Remaining Tasks by Priority Tier and Deadline
        tier_weight = {
            CriticalityTier.TIER_1_MANDATORY: 1,
            CriticalityTier.TIER_2_SPEED_RESTRICTION: 2,
            CriticalityTier.TIER_3_CYCLIC: 3,
        }

        tasks_sorted = sorted(
            self.snapshot.tasks,
            key=lambda t: (tier_weight.get(t.criticality, 3), t.deadline_utc),
        )

        unscheduled_tasks: List[Dict[str, Any]] = []

        # 3. Step 3: Greedy Placement
        for task in tasks_sorted:
            if task.task_id in covered_task_ids:
                continue

            available_cands = self.candidates_by_task.get(task.task_id, [])
            placed = False

            # Try to place in eligible candidate
            for c in available_cands:
                # Check that no task in c is already covered (except current task)
                if any(other_tid in covered_task_ids for other_tid in c.task_ids if other_tid != task.task_id):
                    continue

                occupied_tracks = [c.track_segment_id] + c.isolated_tracks
                if has_track_clash(occupied_tracks, c.start_minute, c.end_minute):
                    continue

                if has_resource_clash(c.assigned_resources, c.start_minute, c.end_minute):
                    continue

                # Feasible slot found!
                commit_candidate(c)
                placed = True
                break

            # 4. Step 4: One Bounded Repair Pass for Mandatory Tasks
            if not placed and task.criticality == CriticalityTier.TIER_1_MANDATORY:
                # Attempt to evict non-mandatory, unlocked cyclic routine tasks blocking this candidate
                for c in available_cands:
                    if any(other_tid in covered_task_ids for other_tid in c.task_ids if other_tid != task.task_id):
                        continue

                    # Check which assignments clash with c
                    clashing_indices: Set[int] = set()
                    c_tracks = set([c.track_segment_id] + c.isolated_tracks)
                    for trk in c_tracks:
                        for cs, ce, aidx in track_occ.get(trk, []):
                            if max(c.start_minute, cs) < min(c.end_minute, ce):
                                clashing_indices.add(aidx)
                    for r in c.assigned_resources:
                        for cs, ce, aidx in res_occ.get(r, []):
                            if max(c.start_minute, cs) < min(c.end_minute, ce):
                                clashing_indices.add(aidx)

                    # Check if all clashing assignments are unlocked and routine (TIER_3_CYCLIC)
                    can_evict = True
                    for cidx in clashing_indices:
                        clash_assign = scheduled_assignments[cidx]
                        if clash_assign.is_locked:
                            can_evict = False
                            break
                        # Check task tiers in clashing assignment
                        clash_tasks = [t for t in self.snapshot.tasks if t.task_id in clash_assign.task_ids]
                        if any(t.criticality != CriticalityTier.TIER_3_CYCLIC for t in clash_tasks):
                            can_evict = False
                            break

                    if can_evict and clashing_indices:
                        # Perform 1-step repair: evict clashing routine tasks
                        for cidx in clashing_indices:
                            evicted = scheduled_assignments[cidx]
                            for etid in evicted.task_ids:
                                covered_task_ids.discard(etid)
                            # Remove from track and resource index
                            for trk in set([evicted.track_segment_id] + evicted.isolated_tracks):
                                track_occ[trk] = [
                                    entry for entry in track_occ[trk] if entry[2] != cidx
                                ]
                            for r in evicted.assigned_resources:
                                res_occ[r] = [
                                    entry for entry in res_occ[r] if entry[2] != cidx
                                ]
                            unscheduled_tasks.append({
                                "task_id": str(evicted.task_ids[0]),
                                "business_key": evicted.business_keys[0],
                                "reason": f"Evicted during 1-step repair pass to accommodate mandatory task {task.business_key}",
                            })

                        # Place mandatory task
                        commit_candidate(c)
                        placed = True
                        break

            if not placed:
                unscheduled_tasks.append({
                    "task_id": str(task.task_id),
                    "business_key": task.business_key,
                    "criticality": task.criticality.value,
                    "reason": "No clash-free slot found against existing train and task occupations",
                })

        mandatory_tasks = [t for t in self.snapshot.tasks if t.criticality == CriticalityTier.TIER_1_MANDATORY]
        mandatory_scheduled = [
            t for t in mandatory_tasks if t.task_id in covered_task_ids
        ]

        mandatory_success = len(mandatory_scheduled) == len(mandatory_tasks)
        status = "FEASIBLE" if mandatory_success else "BASELINE_NO_FEASIBLE_PLAN_FOUND"

        total_minutes = sum(a.duration_minutes for a in scheduled_assignments)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return BaselineSolveResult(
            solver_status=status,
            is_feasible=mandatory_success,
            total_tasks_count=len(self.snapshot.tasks),
            scheduled_tasks_count=len(covered_task_ids),
            mandatory_total_count=len(mandatory_tasks),
            mandatory_scheduled_count=len(mandatory_scheduled),
            total_block_minutes_scheduled=total_minutes,
            assignments=scheduled_assignments,
            unscheduled_tasks=unscheduled_tasks,
            solve_duration_ms=round(elapsed_ms, 2),
            metrics={
                "scheduled_percentage": round((len(covered_task_ids) / max(1, len(self.snapshot.tasks))) * 100, 1),
                "total_assignments": len(scheduled_assignments),
                "bundled_assignments_count": sum(1 for a in scheduled_assignments if a.is_bundled),
                "locked_assignments_count": sum(1 for a in scheduled_assignments if a.is_locked),
                "runtime_ms": round(elapsed_ms, 2),
            },
        )
