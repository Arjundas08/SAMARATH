"""
Hand-authored Golden and Mutation Fixtures for Checker Oracle.
Implements Blueprint Sections 23 & 41:
- Static hand-authored assignments independent of any candidate generator or solver.
- Distinct valid and mutated invalid scenarios for regression and compliance verification.
"""
from typing import Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta

from app.schemas.enums import CriticalityTier, DepartmentType, ResourceType
from app.schemas.task import Task, ResourceRequirement
from app.schemas.snapshot import Snapshot, TrainOccupation, ResourceCalendarEntry, LockedCommitment
from app.schemas.checker import ProposedPlan, CheckerAssignment, CheckerPhase




def get_base_fixture_snapshot() -> Snapshot:
    h_start = datetime(2026, 10, 12, 0, 0, tzinfo=timezone.utc)
    h_end = datetime(2026, 10, 14, 0, 0, tzinfo=timezone.utc)

    # 3 hand-crafted tasks
    task_mand = Task(
        task_id=UUID("11111111-1111-1111-1111-111111111111"),
        business_key="HAND-MAND-01",
        department=DepartmentType.ENGINEERING,
        sub_department="P-WAY",
        work_type="TAMPING",
        description="Handcrafted mandatory tamping",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=30.0,
        chainage_end_km=32.0,
        duration_minutes=60,
        setup_buffer_minutes=15,
        restoration_buffer_minutes=15,
        criticality=CriticalityTier.TIER_1_MANDATORY,
        deadline_utc=h_start + timedelta(hours=36),
        required_resources=[
            ResourceRequirement(resource_type=ResourceType.MACHINE, resource_id="CSM-01", quantity=1)
        ],
        total_block_minutes=90,
    )

    task_cyclic = Task(
        task_id=UUID("22222222-2222-2222-2222-222222222222"),
        business_key="HAND-CYC-02",
        department=DepartmentType.SIGNALLING,
        sub_department="SIGNALLING",
        work_type="POINT_MACHINE",
        description="Handcrafted routine point machine",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=31.0,
        chainage_end_km=31.5,
        duration_minutes=45,
        setup_buffer_minutes=15,
        restoration_buffer_minutes=15,
        criticality=CriticalityTier.TIER_3_CYCLIC,
        deadline_utc=h_start + timedelta(hours=40),
        required_resources=[],
        total_block_minutes=75,
    )

    task_trd = Task(
        task_id=UUID("33333333-3333-3333-3333-333333333333"),
        business_key="HAND-TRD-03",
        department=DepartmentType.ELECTRICAL,
        sub_department="TRD",
        work_type="OHE_NEUTRAL_SECTION",
        description="Handcrafted neutral section maintenance",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=47.5,
        chainage_end_km=48.5,
        duration_minutes=60,
        setup_buffer_minutes=15,
        restoration_buffer_minutes=15,
        criticality=CriticalityTier.TIER_2_SPEED_RESTRICTION,
        deadline_utc=h_start + timedelta(hours=42),
        requires_power_block=True,
        power_block_elementary_section="ELEM-CHR-01",
        required_resources=[
            ResourceRequirement(resource_type=ResourceType.CREW, resource_id="SUP-CREW-01", quantity=1)
        ],
        total_block_minutes=90,
    )

    # Train occupation
    train_occ = TrainOccupation(
        occupation_id="OCC-HAND-01",
        train_number="12951",
        train_type="EXPRESS",
        track_segment_id="TRACK-BRV-CHR-DN",
        entry_time_utc=h_start + timedelta(hours=6),
        exit_time_utc=h_start + timedelta(hours=7),
        start_minute=360,
        end_minute=420,
    )

    # Resource calendar: CSM-01 has outage on Day 2 between 14:00 and 18:00
    res_cal = ResourceCalendarEntry(
        entry_id="CAL-CSM-01",
        resource_id="CSM-01",
        resource_type=ResourceType.MACHINE.value,
        available_start_utc=h_start + timedelta(hours=38),
        available_end_utc=h_start + timedelta(hours=42),
        is_outage=True,
        outage_reason="CSM-01 Scheduled Weekly Maintenance",
    )

    # Hard lock for task_mand at 08:00 to 09:30 on Day 1
    lock = LockedCommitment(
        commitment_id="LOCK-HAND-01",
        task_id=task_mand.task_id,
        track_segment_id=task_mand.track_segment_id,
        start_utc=h_start + timedelta(hours=8),
        end_utc=h_start + timedelta(hours=9, minutes=30),
        locked_by="Senior Safety Commissioner",
        lock_reason="Court Order / Safety Mandate",
    )

    return Snapshot(
        snapshot_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        corridor_code="VKC",
        snapshot_hash="sha256-handcrafted-golden-hash-vkc-2026",
        is_sealed=True,
        created_at_utc=h_start,
        created_by="oracle_tester",
        horizon_start_utc=h_start,
        horizon_end_utc=h_end,
        tasks=[task_mand, task_cyclic, task_trd],
        train_occupations=[train_occ],
        resource_calendars=[res_cal],
        locked_commitments=[lock],
    )


def create_golden_valid_plan(snapshot: Snapshot) -> ProposedPlan:
    """Returns a 100% valid proposed plan matching all constraints."""
    h_start = snapshot.horizon_start_utc
    t_mand = snapshot.tasks[0]
    t_cyclic = snapshot.tasks[1]
    t_trd = snapshot.tasks[2]

    # Assignment 1: Exactly matches hard lock at 08:00 - 09:30
    a1_start = h_start + timedelta(hours=8)
    a1_end = h_start + timedelta(hours=9, minutes=30)
    a1 = CheckerAssignment(
        assignment_id="ASSIGN-GOLDEN-01",
        task_ids=[t_mand.task_id],
        business_keys=[t_mand.business_key],
        track_segment_id=t_mand.track_segment_id,
        start_utc=a1_start,
        end_utc=a1_end,
        assigned_resources=["CSM-01"],
        phases=[
            CheckerPhase(phase_name="SETUP", start_utc=a1_start, end_utc=a1_start + timedelta(minutes=15)),
            CheckerPhase(phase_name="EXECUTION", start_utc=a1_start + timedelta(minutes=15), end_utc=a1_end - timedelta(minutes=15)),
            CheckerPhase(phase_name="RESTORATION", start_utc=a1_end - timedelta(minutes=15), end_utc=a1_end),
        ],
        is_locked=True,
    )

    # Assignment 2: Cyclic task at 10:00 - 11:15 (No train collision, disjoint from A1)
    a2_start = h_start + timedelta(hours=10)
    a2_end = h_start + timedelta(hours=11, minutes=15)
    a2 = CheckerAssignment(
        assignment_id="ASSIGN-GOLDEN-02",
        task_ids=[t_cyclic.task_id],
        business_keys=[t_cyclic.business_key],
        track_segment_id=t_cyclic.track_segment_id,
        start_utc=a2_start,
        end_utc=a2_end,
        assigned_resources=[],
        phases=[
            CheckerPhase(phase_name="SETUP", start_utc=a2_start, end_utc=a2_start + timedelta(minutes=15)),
            CheckerPhase(phase_name="EXECUTION", start_utc=a2_start + timedelta(minutes=15), end_utc=a2_end - timedelta(minutes=15)),
            CheckerPhase(phase_name="RESTORATION", start_utc=a2_end - timedelta(minutes=15), end_utc=a2_end),
        ],
    )

    # Assignment 3: TRD Neutral Section task at 14:00 - 15:30
    # Must isolate both DN and UP track due to Neutral Section
    a3_start = h_start + timedelta(hours=14)
    a3_end = h_start + timedelta(hours=15, minutes=30)
    a3 = CheckerAssignment(
        assignment_id="ASSIGN-GOLDEN-03",
        task_ids=[t_trd.task_id],
        business_keys=[t_trd.business_key],
        track_segment_id=t_trd.track_segment_id,
        start_utc=a3_start,
        end_utc=a3_end,
        assigned_resources=["SUP-CREW-01"],
        requires_power_block=True,
        power_block_elementary_section=t_trd.power_block_elementary_section,
        isolated_tracks=["TRACK-BRV-CHR-UP"],  # Neutral Section isolation of UP track!
        phases=[
            CheckerPhase(phase_name="SETUP", start_utc=a3_start, end_utc=a3_start + timedelta(minutes=15)),
            CheckerPhase(phase_name="EXECUTION", start_utc=a3_start + timedelta(minutes=15), end_utc=a3_end - timedelta(minutes=15)),
            CheckerPhase(phase_name="RESTORATION", start_utc=a3_end - timedelta(minutes=15), end_utc=a3_end),
        ],
    )

    return ProposedPlan(
        plan_id="PLAN-GOLDEN-VALID",
        snapshot_id=snapshot.snapshot_id,
        snapshot_hash=snapshot.snapshot_hash,
        assignments=[a1, a2, a3],
    )
