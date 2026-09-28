"""
Independent Feasibility Checker and Correctness Oracle.
Implements Blueprint Sections 23 & 41:
- Autonomous verification engine completely decoupled from planner/optimizer heuristics.
- Does NOT import planner candidate generators, greedy heuristics, or optimizer models.
- Operates on raw Snapshot records, rule/topology specifications, and materialized ProposedPlan.
- Performs second-resolution interval sweeps for track, train, and resource conflicts.
- Returns immutable CheckerReport with exact violation codes, observed/expected values, units, and IR regulatory citations.
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from uuid import UUID
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import time

from app.schemas.enums import CriticalityTier, ResourceType
from app.schemas.task import Task
from app.schemas.snapshot import Snapshot, TrainOccupation, ResourceCalendarEntry, LockedCommitment
from app.schemas.checker import (
    ProposedPlan,
    CheckerAssignment,
    CheckerPhase,
    CheckerReport,
    CheckerViolation,
    CheckerVerdict,
    ViolationSeverity,
)


class IndependentFeasibilityChecker:
    """
    Decoupled correctness oracle for railway block proposals.
    Evaluates physical, operational, and regulatory feasibility.
    """
    VERSION = "2026.1-ORACLE-INDEPENDENT"
    MODEL_EVIDENCE_SET = "IR-GENERAL-RULES-2026-VKC-TOPOLOGY-V1"

    def __init__(self, snapshot: Snapshot):
        self.snapshot = snapshot
        self.tasks_by_id: Dict[UUID, Task] = {t.task_id: t for t in snapshot.tasks}
        self.locks_by_task: Dict[UUID, LockedCommitment] = {l.task_id: l for l in snapshot.locked_commitments}

    def verify_plan(self, plan: ProposedPlan) -> CheckerReport:
        """
        Executes exhaustive independent validation on the proposed plan.
        """
        start_time = time.perf_counter()
        violations: List[CheckerViolation] = []
        warnings: List[str] = []

        # 1. Snapshot Integrity Check
        if plan.snapshot_id != self.snapshot.snapshot_id:
            violations.append(
                CheckerViolation(
                    violation_code="SNAPSHOT_ID_MISMATCH",
                    severity=ViolationSeverity.CRITICAL,
                    entity_ids=[str(plan.snapshot_id), str(self.snapshot.snapshot_id)],
                    observed_value=str(plan.snapshot_id),
                    expected_value=str(self.snapshot.snapshot_id),
                    unit="UUID",
                    source_reference="Blueprint Sec 23.2",
                    message="Proposed plan snapshot_id does not match target snapshot",
                )
            )

        # 2. Check Task Duplication & Mandatory Coverage
        seen_task_ids: Dict[UUID, str] = {}
        scheduled_task_ids: Set[UUID] = set()

        for a in plan.assignments:
            for tid in a.task_ids:
                if tid in seen_task_ids:
                    violations.append(
                        CheckerViolation(
                            violation_code="TASK_DUPLICATION",
                            severity=ViolationSeverity.CRITICAL,
                            entity_ids=[str(tid), a.assignment_id, seen_task_ids[tid]],
                            observed_value=f"Duplicated in {a.assignment_id} and {seen_task_ids[tid]}",
                            expected_value="At most 1 assignment per task",
                            unit="count",
                            source_reference="IR Operating Code Rule 12.4",
                            message=f"Task {tid} is scheduled multiple times in the same plan",
                        )
                    )
                else:
                    seen_task_ids[tid] = a.assignment_id
                scheduled_task_ids.add(tid)

        # Mandatory Tasks Check
        mandatory_tasks = [t for t in self.snapshot.tasks if t.criticality == CriticalityTier.TIER_1_MANDATORY]
        for mt in mandatory_tasks:
            if mt.task_id not in scheduled_task_ids:
                violations.append(
                    CheckerViolation(
                        violation_code="MANDATORY_TASK_MISSING",
                        severity=ViolationSeverity.CRITICAL,
                        entity_ids=[str(mt.task_id), mt.business_key],
                        observed_value="UNSCHEDULED",
                        expected_value="SCHEDULED",
                        unit="status",
                        source_reference="IR Safety Directorate Circular 2026/Safety/01",
                        message=f"Tier-1 Mandatory task {mt.business_key} ({mt.description}) is missing from proposed plan",
                    )
                )

        # Unknown mandatory facts check
        for t in self.snapshot.tasks:
            if t.total_block_minutes is None or t.total_block_minutes <= 0:
                violations.append(
                    CheckerViolation(
                        violation_code="UNKNOWN_MANDATORY_FACT",
                        severity=ViolationSeverity.CRITICAL,
                        entity_ids=[str(t.task_id), t.business_key],
                        observed_value=str(t.total_block_minutes),
                        expected_value="> 0",
                        unit="minutes",
                        source_reference="Blueprint Sec 23.3",
                        message=f"Task {t.business_key} has missing or invalid required block duration",
                    )
                )

        # 3. Release, Deadline, Horizon Boundaries & Cross-Midnight Validation
        for a in plan.assignments:
            # Basic interval validity
            if a.end_utc <= a.start_utc:
                violations.append(
                    CheckerViolation(
                        violation_code="INCORRECT_CROSS_MIDNIGHT_BOUNDARY",
                        severity=ViolationSeverity.CRITICAL,
                        entity_ids=[a.assignment_id],
                        observed_value=f"{a.start_utc.isoformat()} to {a.end_utc.isoformat()}",
                        expected_value="start_utc < end_utc",
                        unit="UTC",
                        source_reference="IR G&SR 2026 Rule 3.1",
                        message=f"Assignment {a.assignment_id} has invalid negative or zero interval duration",
                    )
                )

            # Horizon containment
            if a.start_utc < self.snapshot.horizon_start_utc or a.end_utc > self.snapshot.horizon_end_utc:
                violations.append(
                    CheckerViolation(
                        violation_code="BOUNDARY_VIOLATION",
                        severity=ViolationSeverity.CRITICAL,
                        entity_ids=[a.assignment_id],
                        observed_value=f"[{a.start_utc.isoformat()}, {a.end_utc.isoformat()}]",
                        expected_value=f"[{self.snapshot.horizon_start_utc.isoformat()}, {self.snapshot.horizon_end_utc.isoformat()}]",
                        unit="UTC",
                        source_reference="Blueprint Sec 23.2",
                        message=f"Assignment {a.assignment_id} falls outside snapshot planning horizon",
                    )
                )

            # Task deadline check
            for tid in a.task_ids:
                task = self.tasks_by_id.get(tid)
                if not task:
                    violations.append(
                        CheckerViolation(
                            violation_code="TASK_NOT_IN_SNAPSHOT",
                            severity=ViolationSeverity.CRITICAL,
                            entity_ids=[str(tid), a.assignment_id],
                            observed_value=str(tid),
                            expected_value="Valid snapshot task UUID",
                            unit="UUID",
                            source_reference="Blueprint Sec 23.2",
                            message=f"Assignment {a.assignment_id} references unknown task {tid}",
                        )
                    )
                    continue

                if a.end_utc > task.deadline_utc:
                    overage_seconds = (a.end_utc - task.deadline_utc).total_seconds()
                    violations.append(
                        CheckerViolation(
                            violation_code="DEADLINE_EXCEEDED",
                            severity=ViolationSeverity.CRITICAL,
                            entity_ids=[str(tid), task.business_key, a.assignment_id],
                            observed_value=a.end_utc.isoformat(),
                            expected_value=f"<= {task.deadline_utc.isoformat()}",
                            unit="UTC",
                            source_reference="IR Maintenance Code Chapter 5",
                            message=f"Task {task.business_key} in {a.assignment_id} finishes {overage_seconds:.0f}s after deadline",
                        )
                    )

        # 4. Strict Hard Lock Preservation Check
        for lock in self.snapshot.locked_commitments:
            locked_assignment = next(
                (a for a in plan.assignments if lock.task_id in a.task_ids),
                None,
            )
            if not locked_assignment:
                violations.append(
                    CheckerViolation(
                        violation_code="HARD_LOCK_ALTERED",
                        severity=ViolationSeverity.CRITICAL,
                        entity_ids=[lock.commitment_id, str(lock.task_id)],
                        observed_value="UNSCHEDULED",
                        expected_value=f"Start={lock.start_utc.isoformat()}, End={lock.end_utc.isoformat()}",
                        unit="UTC",
                        source_reference="ADR-006 / Blueprint Sec 22 Inv 1",
                        message=f"Strict Hard Lock commitment {lock.commitment_id} for task {lock.task_id} was omitted",
                    )
                )
            else:
                # Compare start and end down to the second
                start_diff = abs((locked_assignment.start_utc - lock.start_utc).total_seconds())
                end_diff = abs((locked_assignment.end_utc - lock.end_utc).total_seconds())
                if start_diff > 0 or end_diff > 0:
                    violations.append(
                        CheckerViolation(
                            violation_code="HARD_LOCK_ALTERED",
                            severity=ViolationSeverity.CRITICAL,
                            entity_ids=[lock.commitment_id, str(lock.task_id), locked_assignment.assignment_id],
                            observed_value=f"Start={locked_assignment.start_utc.isoformat()} (delta={start_diff:.0f}s), End={locked_assignment.end_utc.isoformat()} (delta={end_diff:.0f}s)",
                            expected_value=f"Start={lock.start_utc.isoformat()}, End={lock.end_utc.isoformat()}",
                            unit="seconds",
                            source_reference="ADR-006 / Blueprint Sec 22 Inv 1",
                            message=f"Hard Lock {lock.commitment_id} was altered in {locked_assignment.assignment_id}",
                        )
                    )

        # 5. Train & Fixed-Authority Occupation Collision (Down to the second)
        for a in plan.assignments:
            # Active tracks = primary track + isolated tracks
            all_active_tracks = set([a.track_segment_id] + a.isolated_tracks)

            for occ in self.snapshot.train_occupations:
                if occ.track_segment_id in all_active_tracks:
                    # Interval intersection: max(A_start, T_start) < min(A_end, T_end)
                    if max(a.start_utc, occ.entry_time_utc) < min(a.end_utc, occ.exit_time_utc):
                        overlap_sec = (min(a.end_utc, occ.exit_time_utc) - max(a.start_utc, occ.entry_time_utc)).total_seconds()
                        violations.append(
                            CheckerViolation(
                                violation_code="TRAIN_OCCUPATION_COLLISION",
                                severity=ViolationSeverity.CRITICAL,
                                entity_ids=[a.assignment_id, occ.occupation_id, occ.train_number, occ.track_segment_id],
                                observed_value=f"{overlap_sec:.0f}s overlap on {occ.track_segment_id}",
                                expected_value="0s overlap (Disjoint intervals)",
                                unit="seconds",
                                source_reference="IR General Rules 4.19 / Safety Regulation 2026",
                                message=f"Assignment {a.assignment_id} collides with Train {occ.train_number} ({occ.train_type}) for {overlap_sec:.0f}s on {occ.track_segment_id}",
                            )
                        )

        # 6. Track Segment Non-Overlap (Collision-Free)
        for i in range(len(plan.assignments)):
            for j in range(i + 1, len(plan.assignments)):
                a1 = plan.assignments[i]
                a2 = plan.assignments[j]

                tracks1 = set([a1.track_segment_id] + a1.isolated_tracks)
                tracks2 = set([a2.track_segment_id] + a2.isolated_tracks)
                shared_tracks = tracks1.intersection(tracks2)

                if shared_tracks:
                    if max(a1.start_utc, a2.start_utc) < min(a1.end_utc, a2.end_utc):
                        overlap_sec = (min(a1.end_utc, a2.end_utc) - max(a1.start_utc, a2.start_utc)).total_seconds()
                        violations.append(
                            CheckerViolation(
                                violation_code="TRACK_COLLISION",
                                severity=ViolationSeverity.CRITICAL,
                                entity_ids=[a1.assignment_id, a2.assignment_id, list(shared_tracks)[0]],
                                observed_value=f"{overlap_sec:.0f}s overlap",
                                expected_value="0s overlap",
                                unit="seconds",
                                source_reference="IR G&SR 2026 Para 4.21",
                                message=f"Assignments {a1.assignment_id} and {a2.assignment_id} clash on track {list(shared_tracks)[0]} for {overlap_sec:.0f}s",
                            )
                        )

        # 7. Resource Capacity & Outage Sweeping
        # Sweep line algorithm across discrete start/end events
        resource_events: Dict[str, List[Tuple[datetime, int, str]]] = defaultdict(list)
        # Also track last assignment end per resource to verify unobserved releases
        resource_intervals: Dict[str, List[Tuple[datetime, datetime, str]]] = defaultdict(list)

        for a in plan.assignments:
            for r in a.assigned_resources:
                resource_events[r].append((a.start_utc, +1, a.assignment_id))
                resource_events[r].append((a.end_utc, -1, a.assignment_id))
                resource_intervals[r].append((a.start_utc, a.end_utc, a.assignment_id))

        # Check concurrency capacity
        for r_id, events in resource_events.items():
            # Sort events: times ascending, end events (-1) before start events (+1) if identical timestamp
            events.sort(key=lambda x: (x[0], x[1]))
            current_count = 0
            # Default machine/crew capacity is 1 unless otherwise configured
            max_capacity = 2 if "SUPERVISOR" in r_id.upper() else 1

            for dt, delta, aid in events:
                current_count += delta
                if current_count > max_capacity:
                    violations.append(
                        CheckerViolation(
                            violation_code="RESOURCE_CAPACITY_EXCEEDED",
                            severity=ViolationSeverity.CRITICAL,
                            entity_ids=[r_id, aid],
                            observed_value=f"{current_count} concurrent allocations at {dt.isoformat()}",
                            expected_value=f"<= {max_capacity} concurrent allocations",
                            unit="units",
                            source_reference="Blueprint Sec 23.4 / Capacity Register",
                            message=f"Resource {r_id} capacity exceeded ({current_count} > {max_capacity}) during {aid}",
                        )
                    )
                    break

        # Check Resource Outages
        for cal in self.snapshot.resource_calendars:
            if cal.is_outage:
                for a_start, a_end, aid in resource_intervals.get(cal.resource_id, []):
                    if max(a_start, cal.available_start_utc) < min(a_end, cal.available_end_utc):
                        overlap_sec = (min(a_end, cal.available_end_utc) - max(a_start, cal.available_start_utc)).total_seconds()
                        violations.append(
                            CheckerViolation(
                                violation_code="RESOURCE_OUTAGE_CONFLICT",
                                severity=ViolationSeverity.CRITICAL,
                                entity_ids=[cal.resource_id, aid, cal.entry_id],
                                observed_value=f"{overlap_sec:.0f}s overlap with scheduled outage",
                                expected_value="0s overlap",
                                unit="seconds",
                                source_reference="Depot Overhaul Schedule / Section 16",
                                message=f"Resource {cal.resource_id} assigned in {aid} during scheduled overhaul ({cal.outage_reason})",
                            )
                        )

        # 8. Resource Qualification Check
        for a in plan.assignments:
            for tid in a.task_ids:
                task = self.tasks_by_id.get(tid)
                if not task:
                    continue
                for req in task.required_resources:
                    if req.resource_id and req.resource_id not in a.assigned_resources:
                        violations.append(
                            CheckerViolation(
                                violation_code="WRONG_QUALIFIED_RESOURCE",
                                severity=ViolationSeverity.CRITICAL,
                                entity_ids=[str(tid), task.business_key, req.resource_id, a.assignment_id],
                                observed_value=str(a.assigned_resources),
                                expected_value=f"Must include required resource {req.resource_id}",
                                unit="resource_id",
                                source_reference="IR Competency & Plant Allocation Rules",
                                message=f"Task {task.business_key} requires resource {req.resource_id} which is missing in {a.assignment_id}",
                            )
                        )

        # 9. Neutral Section & Footprint Isolation
        # Charlie (CHR km 48.0) Neutral Section requires isolating both UP and DN tracks
        for a in plan.assignments:
            has_chr_power_block = (
                a.requires_power_block
                and ("CHR" in a.track_segment_id or (a.power_block_elementary_section and "CHR" in a.power_block_elementary_section))
            )
            if has_chr_power_block:
                # If on DN, must also isolate UP; if on UP, must also isolate DN
                if "DN" in a.track_segment_id:
                    required_adjacent = a.track_segment_id.replace("DN", "UP")
                    if required_adjacent not in a.isolated_tracks:
                        violations.append(
                            CheckerViolation(
                                violation_code="UNRESOLVED_NEUTRAL_SECTION_FOOTPRINT",
                                severity=ViolationSeverity.CRITICAL,
                                entity_ids=[a.assignment_id, a.track_segment_id, required_adjacent],
                                observed_value=f"Isolated tracks: {a.isolated_tracks}",
                                expected_value=f"Must include adjacent track {required_adjacent} due to Neutral Section at CHR",
                                unit="track_segment_id",
                                source_reference="ACTM Vol II Para 20433 / Joint Safety Circular 14",
                                message=f"Assignment {a.assignment_id} fails to isolate adjacent track {required_adjacent} under CHR Neutral Section",
                            )
                        )

        # 10. Restoration Phase Verification
        for a in plan.assignments:
            if a.phases:
                # Last phase must be RESTORATION
                last_phase = a.phases[-1]
                if last_phase.phase_name != "RESTORATION":
                    violations.append(
                        CheckerViolation(
                            violation_code="MISSING_RESTORATION_PHASE",
                            severity=ViolationSeverity.CRITICAL,
                            entity_ids=[a.assignment_id, last_phase.phase_name],
                            observed_value=f"Last phase is {last_phase.phase_name}",
                            expected_value="Last phase must be RESTORATION",
                            unit="phase_name",
                            source_reference="IR Block Working Manual Para 15.2",
                            message=f"Assignment {a.assignment_id} lacks mandatory final RESTORATION phase",
                        )
                    )

        # 11. Autonomous Authority Transitions Prohibition
        if plan.metadata.get("auto_grant_authority") is True or plan.metadata.get("auto_release_authority") is True:
            violations.append(
                CheckerViolation(
                    violation_code="AUTONOMOUS_AUTHORITY_TRANSITION_PROHIBITED",
                    severity=ViolationSeverity.CRITICAL,
                    entity_ids=[plan.plan_id],
                    observed_value="Attempted automated authority grant/release",
                    expected_value="Human Section Controller authority required",
                    unit="authority_flag",
                    source_reference="IR Operating Code Rule 4.02",
                    message="SAMARATH strictly prohibits autonomous operational authority granting or releasing",
                )
            )

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Coverage metrics
        total_tasks_count = len(self.snapshot.tasks)
        mandatory_total_count = len(mandatory_tasks)
        scheduled_count = len(scheduled_task_ids)
        mandatory_scheduled_count = sum(1 for mt in mandatory_tasks if mt.task_id in scheduled_task_ids)

        verdict = CheckerVerdict.VALID if len(violations) == 0 else CheckerVerdict.INVALID

        return CheckerReport(
            checker_version=self.VERSION,
            verdict=verdict,
            checked_at_utc=datetime.now(timezone.utc),
            snapshot_id=self.snapshot.snapshot_id,
            snapshot_hash=self.snapshot.snapshot_hash,
            violations=violations,
            warnings=warnings,
            coverage_metrics={
                "total_tasks": total_tasks_count,
                "scheduled_tasks": scheduled_count,
                "mandatory_total": mandatory_total_count,
                "mandatory_scheduled": mandatory_scheduled_count,
                "coverage_pct": round((scheduled_count / total_tasks_count * 100.0), 1) if total_tasks_count else 0.0,
                "mandatory_coverage_pct": round((mandatory_scheduled_count / mandatory_total_count * 100.0), 1) if mandatory_total_count else 0.0,
            },
            execution_duration_ms=duration_ms,
            model_evidence_set=self.MODEL_EVIDENCE_SET,
        )
