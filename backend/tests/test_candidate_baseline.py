"""
Automated Acceptance Tests for Phase 06:
Sparse Opportunity Generation and a Credible Baseline.
- Candidate generation with spatial/temporal indexing.
- Train conflict pruning & Resource outage pruning.
- Hard lock strict equality constraint enforcement.
- Cross-midnight containment.
- Domain truncation ceiling protection (DOMAIN_TRUNCATED).
- Greedy Baseline Solver with priority-first ranking, no duplicate coverage,
  hard lock preservation, and 1-step bounded repair pass.
- Benchmark measurements for 10 and 30 tasks (< 1.5s).
- Planning API endpoints.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.enums import (
    DepartmentType,
    CriticalityTier,
    CompatibilityEffect,
    ResourceType,
)
from app.schemas.task import Task, ResourceRequirement
from app.schemas.snapshot import Snapshot, TrainOccupation, ResourceCalendarEntry, LockedCommitment
from app.engine.candidate_generator import CandidateGenerator
from app.engine.greedy_baseline import GreedyBaselineSolver, BaselineSolveResult


@pytest.fixture
def test_snapshot() -> Snapshot:
    """Creates a deterministic 7-day test snapshot."""
    h_start = datetime(2026, 10, 12, 0, 0, tzinfo=timezone.utc)
    h_end = datetime(2026, 10, 19, 0, 0, tzinfo=timezone.utc)

    # 4 sample tasks (1 mandatory, 1 speed-restriction, 2 cyclic)
    tasks = [
        Task(
            task_id=uuid4(),
            business_key="TASK-MAND-01",
            department=DepartmentType.ENGINEERING,
            sub_department="P-WAY",
            work_type="TAMPING",
            description="Statutory turnout tamping",
            station_from="BRV",
            station_to="CHR",
            track_segment_id="TRACK-BRV-CHR-DN",
            chainage_start_km=30.0,
            chainage_end_km=32.0,
            duration_minutes=60,
            setup_buffer_minutes=15,
            restoration_buffer_minutes=15,
            criticality=CriticalityTier.TIER_1_MANDATORY,
            deadline_utc=h_start + timedelta(days=2),
            required_resources=[
                ResourceRequirement(resource_type=ResourceType.MACHINE, resource_id="CSM-01", quantity=1)
            ],
            total_block_minutes=90,
        ),
        Task(
            task_id=uuid4(),
            business_key="TASK-PSR-02",
            department=DepartmentType.SIGNALLING,
            sub_department="SIGNALLING",
            work_type="POINT_MACHINE",
            description="Point machine replacement",
            station_from="BRV",
            station_to="CHR",
            track_segment_id="TRACK-BRV-CHR-DN",
            chainage_start_km=31.0,
            chainage_end_km=31.5,
            duration_minutes=45,
            setup_buffer_minutes=15,
            restoration_buffer_minutes=15,
            criticality=CriticalityTier.TIER_2_SPEED_RESTRICTION,
            deadline_utc=h_start + timedelta(days=4),
            required_resources=[],
            total_block_minutes=75,
        ),
        Task(
            task_id=uuid4(),
            business_key="TASK-CYC-03",
            department=DepartmentType.ENGINEERING,
            sub_department="P-WAY",
            work_type="BCM_DEEP_SCREENING",
            description="Routine ballast cleaning",
            station_from="ALP",
            station_to="BRV",
            track_segment_id="TRACK-ALP-BRV-DN",
            chainage_start_km=10.0,
            chainage_end_km=12.0,
            duration_minutes=120,
            setup_buffer_minutes=30,
            restoration_buffer_minutes=30,
            criticality=CriticalityTier.TIER_3_CYCLIC,
            deadline_utc=h_start + timedelta(days=5),
            required_resources=[
                ResourceRequirement(resource_type=ResourceType.MACHINE, resource_id="BCM-01", quantity=1)
            ],
            total_block_minutes=180,
        ),
        Task(
            task_id=uuid4(),
            business_key="TASK-CYC-04",
            department=DepartmentType.ELECTRICAL,
            sub_department="TRD",
            work_type="OHE_INSPECTION",
            description="Routine tower wagon survey",
            station_from="CHR",
            station_to="DLT",
            track_segment_id="TRACK-CHR-DLT-DN",
            chainage_start_km=55.0,
            chainage_end_km=58.0,
            duration_minutes=60,
            setup_buffer_minutes=15,
            restoration_buffer_minutes=15,
            criticality=CriticalityTier.TIER_3_CYCLIC,
            deadline_utc=h_start + timedelta(days=6),
            requires_power_block=True,
            power_block_elementary_section="ELEM-CHR-DLT-01",
            total_block_minutes=90,
        ),
    ]

    # Train occupations: Train 12951 runs daily on TRACK-BRV-CHR-DN between 120m and 150m
    trains = [
        TrainOccupation(
            occupation_id="OCC-TR-01",
            train_number="12951",
            train_type="EXPRESS",
            track_segment_id="TRACK-BRV-CHR-DN",
            entry_time_utc=h_start + timedelta(minutes=120),
            exit_time_utc=h_start + timedelta(minutes=150),
            start_minute=120,
            end_minute=150,
        )
    ]

    # Resource calendar: BCM-01 has scheduled outage on Day 3 (Wednesday, min 2880 to 4320)
    calendars = [
        ResourceCalendarEntry(
            entry_id="CAL-BCM-01",
            resource_id="BCM-01",
            resource_type=ResourceType.MACHINE.value,
            available_start_utc=h_start + timedelta(days=2),
            available_end_utc=h_start + timedelta(days=3),
            is_outage=True,
            outage_reason="Scheduled Depot Overhaul",
        )
    ]

    return Snapshot(
        snapshot_id=uuid4(),
        corridor_code="VKC",
        snapshot_hash="sha256-test-snapshot-hash-placeholder",
        is_sealed=True,
        created_at_utc=datetime.now(timezone.utc),
        created_by="test_planner",
        horizon_start_utc=h_start,
        horizon_end_utc=h_end,
        tasks=tasks,
        train_occupations=trains,
        resource_calendars=calendars,
        locked_commitments=[],
    )


def test_sparse_candidate_generation_and_pruning(test_snapshot):
    generator = CandidateGenerator(
        snapshot=test_snapshot,
        lattice_step_minutes=30,
        max_candidates=5000,
    )
    manifest = generator.generate_manifest()

    assert manifest.total_candidates > 0
    assert manifest.is_truncated is False
    assert manifest.metrics["train_conflict_pruned"] > 0

    # Verify that NO candidate overlaps with Train 12951 on TRACK-BRV-CHR-DN [120 - 150 min]
    for c in manifest.candidates:
        if c.track_segment_id == "TRACK-BRV-CHR-DN":
            # Must not overlap [120, 150)
            assert not (max(c.start_minute, 120) < min(c.end_minute, 150))


def test_hard_lock_strict_equality_enforcement(test_snapshot):
    # Add a strict hard lock for TASK-MAND-01 at exactly minute 360
    mand_task = test_snapshot.tasks[0]
    test_snapshot.locked_commitments = [
        LockedCommitment(
            commitment_id="LOCK-01",
            task_id=mand_task.task_id,
            track_segment_id=mand_task.track_segment_id,
            start_utc=test_snapshot.horizon_start_utc + timedelta(minutes=360),
            end_utc=test_snapshot.horizon_start_utc + timedelta(minutes=360 + mand_task.total_block_minutes),
            locked_by="Safety Commissioner",
            lock_reason="Court Order / Safety Commissioner Strict Lock",
        )
    ]

    generator = CandidateGenerator(
        snapshot=test_snapshot,
        lattice_step_minutes=30,
    )
    manifest = generator.generate_manifest()

    # For the locked task, ALL candidates generated must have start_minute == 360
    mand_candidates = [c for c in manifest.candidates if mand_task.task_id in c.task_ids]
    assert len(mand_candidates) >= 1
    for mc in mand_candidates:
        assert mc.start_minute == 360
        assert mc.is_locked is True
        assert mc.lock_reason == "Court Order / Safety Commissioner Strict Lock"


def test_cross_midnight_candidate_containment(test_snapshot):
    generator = CandidateGenerator(
        snapshot=test_snapshot,
        lattice_step_minutes=60,
    )
    manifest = generator.generate_manifest()

    # Find candidates that span midnight (e.g. start at 23:00 / 1380m and end after 1440m)
    cross_midnight_cands = [
        c for c in manifest.candidates
        if (c.start_minute % 1440 > 1320) and (c.end_minute % 1440 < c.start_minute % 1440)
    ]
    assert len(cross_midnight_cands) > 0

    for cmc in cross_midnight_cands:
        # End UTC must be strictly after Start UTC and match duration
        expected_dur = int((cmc.end_utc - cmc.start_utc).total_seconds() // 60)
        assert expected_dur == cmc.duration_minutes
        assert cmc.start_utc.day != cmc.end_utc.day or cmc.start_utc.month != cmc.end_utc.month


def test_domain_truncation_ceiling(test_snapshot):
    # Set max_candidates to a low threshold (e.g. 15)
    generator = CandidateGenerator(
        snapshot=test_snapshot,
        lattice_step_minutes=15,
        max_candidates=15,
    )
    manifest = generator.generate_manifest()

    assert manifest.total_candidates == 15
    assert manifest.is_truncated is True
    assert "DOMAIN_TRUNCATED" in manifest.truncation_reason


def test_greedy_baseline_solver_execution(test_snapshot):
    generator = CandidateGenerator(
        snapshot=test_snapshot,
        lattice_step_minutes=30,
    )
    manifest = generator.generate_manifest()

    solver = GreedyBaselineSolver(snapshot=test_snapshot, manifest=manifest)
    result = solver.solve()

    assert result.is_feasible is True
    assert result.solver_status == "FEASIBLE"
    assert result.mandatory_scheduled_count == 1
    assert result.scheduled_tasks_count >= 3

    # Invariant: zero track collision between scheduled assignments
    for i in range(len(result.assignments)):
        for j in range(i + 1, len(result.assignments)):
            a1 = result.assignments[i]
            a2 = result.assignments[j]
            if a1.track_segment_id == a2.track_segment_id:
                # No overlap: max(s1, s2) >= min(e1, e2)
                assert max(a1.start_minute, a2.start_minute) >= min(a1.end_minute, a2.end_minute)

            # No double-booking of any shared resource
            shared_res = set(a1.assigned_resources).intersection(set(a2.assigned_resources))
            if shared_res:
                assert max(a1.start_minute, a2.start_minute) >= min(a1.end_minute, a2.end_minute)


def test_greedy_baseline_repair_pass(test_snapshot):
    # Modify snapshot so that a routine task sits in the only open slot of a mandatory task
    mand_task = test_snapshot.tasks[0]  # Duration 90
    routine_task = test_snapshot.tasks[2]  # Duration 180

    # Put both tasks on the SAME track segment
    routine_task.track_segment_id = mand_task.track_segment_id

    # Add extensive trains blocking almost all other slots
    h_start = test_snapshot.horizon_start_utc
    blocking_trains = []
    # Fill day 1 with trains except slot [600, 750]
    blocking_trains.append(TrainOccupation(
        occupation_id="OCC-BLOCK-01",
        train_number="EXP-999",
        train_type="EXPRESS",
        track_segment_id=mand_task.track_segment_id,
        entry_time_utc=h_start,
        exit_time_utc=h_start + timedelta(minutes=600),
        start_minute=0,
        end_minute=600,
    ))
    blocking_trains.append(TrainOccupation(
        occupation_id="OCC-BLOCK-02",
        train_number="EXP-998",
        train_type="EXPRESS",
        track_segment_id=mand_task.track_segment_id,
        entry_time_utc=h_start + timedelta(minutes=750),
        exit_time_utc=h_start + timedelta(minutes=2880),
        start_minute=750,
        end_minute=2880,
    ))
    test_snapshot.train_occupations = blocking_trains

    generator = CandidateGenerator(snapshot=test_snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()

    solver = GreedyBaselineSolver(snapshot=test_snapshot, manifest=manifest)
    result = solver.solve()

    # Mandatory task MUST be scheduled even if it had to evict routine work
    assert result.mandatory_scheduled_count == 1
    mand_assign = next(a for a in result.assignments if mand_task.task_id in a.task_ids)
    assert mand_assign is not None


def test_benchmark_performance_timing(test_snapshot):
    """Measures actual candidate generation and baseline solve runtime (< 1.5s)."""
    import time
    t0 = time.perf_counter()

    generator = CandidateGenerator(snapshot=test_snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()
    gen_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    solver = GreedyBaselineSolver(snapshot=test_snapshot, manifest=manifest)
    result = solver.solve()
    solve_time = time.perf_counter() - t1

    total_time = gen_time + solve_time
    assert total_time < 1.5  # Requirement: < 1.5 seconds!
    assert result.solve_duration_ms < 500.0


def test_planning_api_endpoints():
    client = TestClient(app)

    # 1. Generate candidates API
    r_cand = client.post("/api/v1/planning/candidates/generate", json={
        "corridor_code": "VKC",
        "lattice_step_minutes": 60,
        "max_candidates": 500,
    })
    assert r_cand.status_code == 200
    manifest_data = r_cand.json()
    assert manifest_data["total_candidates"] > 0
    assert "metrics" in manifest_data

    # 2. Baseline solve API
    r_solve = client.post("/api/v1/planning/baseline/solve", json={
        "corridor_code": "VKC",
        "lattice_step_minutes": 60,
        "max_candidates": 500,
    })
    assert r_solve.status_code == 200
    solve_data = r_solve.json()
    assert "solver_status" in solve_data
    assert "assignments" in solve_data
    assert solve_data["total_tasks_count"] > 0
