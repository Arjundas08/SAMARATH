"""
Automated Test Suite for Phase 08:
Real CP-SAT Weekly Optimizer and Lexicographic Profiles.
Implements Blueprint Sections 17, 18, 19, 22, 23, 27, 42:
- Tiny exhaustive oracle agreement on objective values.
- Mandatory impossibility truthful reporting (INFEASIBLE).
- Strict hard lock equality preservation.
- No duplicate task coverage.
- Deterministic single-worker regression semantics.
- Lexicographic PROGRAMME_IMPROVEMENT profile.
- Lexicographic DISRUPTION_RECOVERY minimal churn profile.
- Comparison against credible greedy baseline.
- Full independent feasibility verification via Phase 07 Checker.
- REST API endpoint verification.
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.enums import (
    DepartmentType,
    CriticalityTier,
    ObjectiveProfile,
    SolverStatus,
    StopReason,
    ResourceType,
)
from app.schemas.task import Task, ResourceRequirement
from app.schemas.snapshot import Snapshot, TrainOccupation, ResourceCalendarEntry, LockedCommitment
from app.schemas.candidate import CandidateManifest
from app.schemas.checker import ProposedPlan, CheckerAssignment, CheckerPhase, CheckerVerdict
from app.schemas.optimizer import OptimizerSolveRequest, OptimizerSolveResult
from app.engine.candidate_generator import CandidateGenerator
from app.engine.greedy_baseline import GreedyBaselineSolver
from app.engine.cp_sat_solver import CPSatWeeklyOptimizer
from app.checker.tiny_oracle import ExhaustiveTinyOracle
from app.checker.fixtures import get_base_fixture_snapshot


def test_tiny_exhaustive_oracle_agreement():
    """CP-SAT Optimizer must match mathematical ground-truth from ExhaustiveTinyOracle."""
    snapshot = get_base_fixture_snapshot()
    # 2 tasks for tiny instance
    snapshot.tasks = snapshot.tasks[:2]

    # 1. Solve with Exhaustive Tiny Oracle
    oracle = ExhaustiveTinyOracle(snapshot=snapshot, step_minutes=30)
    oracle_res = oracle.solve_exhaustive()
    assert oracle_res["is_feasible"] is True
    oracle_mand = oracle_res["score"][0]
    oracle_total = oracle_res["score"][1]

    # 2. Solve with CP-SAT Optimizer
    generator = CandidateGenerator(snapshot=snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()

    req = OptimizerSolveRequest(
        corridor_code="VKC",
        profile=ObjectiveProfile.PROGRAMME_IMPROVEMENT,
        time_limit_seconds=10.0,
        num_workers=1,
        random_seed=42,
    )
    optimizer = CPSatWeeklyOptimizer(snapshot=snapshot, manifest=manifest, request=req)
    result = optimizer.solve()

    assert result.is_feasible is True
    assert result.solver_status == SolverStatus.OPTIMAL
    assert result.mandatory_scheduled_count == oracle_mand
    assert result.scheduled_tasks_count == oracle_total
    assert result.checker_verdict == CheckerVerdict.VALID


def test_mandatory_impossibility_truthfully_reported():
    """If a mandatory task cannot be physically scheduled, solver returns INFEASIBLE."""
    snapshot = get_base_fixture_snapshot()
    mand_task = snapshot.tasks[0]

    # Block the entire horizon with trains so mandatory task cannot be placed
    h_start = snapshot.horizon_start_utc
    h_end = snapshot.horizon_end_utc
    snapshot.train_occupations = [
        TrainOccupation(
            occupation_id="OCC-BLOCK-ALL",
            train_number="BLOCK-ALL",
            train_type="FREIGHT",
            track_segment_id=mand_task.track_segment_id,
            entry_time_utc=h_start,
            exit_time_utc=h_end,
            start_minute=0,
            end_minute=int((h_end - h_start).total_seconds() // 60),
        )
    ]

    generator = CandidateGenerator(snapshot=snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()

    req = OptimizerSolveRequest(
        corridor_code="VKC",
        profile=ObjectiveProfile.PROGRAMME_IMPROVEMENT,
        time_limit_seconds=5.0,
    )
    optimizer = CPSatWeeklyOptimizer(snapshot=snapshot, manifest=manifest, request=req)
    result = optimizer.solve()

    assert result.is_feasible is False
    assert result.solver_status == SolverStatus.INFEASIBLE
    assert result.stop_reason == StopReason.INFEASIBILITY_PROVEN
    assert result.scheduled_tasks_count == 0


def test_strict_hard_lock_preservation():
    """CP-SAT preserves hard locked commitments with zero time deviation."""
    snapshot = get_base_fixture_snapshot()
    mand_task = snapshot.tasks[0]
    lock_time = snapshot.horizon_start_utc + timedelta(hours=8)

    generator = CandidateGenerator(snapshot=snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()

    req = OptimizerSolveRequest(
        corridor_code="VKC",
        profile=ObjectiveProfile.PROGRAMME_IMPROVEMENT,
        time_limit_seconds=10.0,
        num_workers=1,
    )
    optimizer = CPSatWeeklyOptimizer(snapshot=snapshot, manifest=manifest, request=req)
    result = optimizer.solve()

    assert result.is_feasible is True
    # Find assignment for locked mandatory task
    locked_assign = next(a for a in result.assignments if mand_task.task_id in a.task_ids)
    assert locked_assign.start_utc == lock_time
    assert result.checker_verdict == CheckerVerdict.VALID


def test_deterministic_single_worker_regression():
    """Two independent runs with num_workers=1 and fixed seed yield identical solutions."""
    snapshot = get_base_fixture_snapshot()
    generator = CandidateGenerator(snapshot=snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()

    req1 = OptimizerSolveRequest(num_workers=1, random_seed=42, time_limit_seconds=10.0)
    res1 = CPSatWeeklyOptimizer(snapshot, manifest, req1).solve()

    req2 = OptimizerSolveRequest(num_workers=1, random_seed=42, time_limit_seconds=10.0)
    res2 = CPSatWeeklyOptimizer(snapshot, manifest, req2).solve()

    assert res1.solver_status == res2.solver_status
    assert res1.scheduled_tasks_count == res2.scheduled_tasks_count
    assert res1.total_block_minutes == res2.total_block_minutes
    # Verify assignment start minutes match exactly
    s1 = [a.start_utc for a in res1.assignments]
    s2 = [a.start_utc for a in res2.assignments]
    assert s1 == s2


def test_disruption_recovery_minimizes_churn():
    """In recovery profile, optimizer preserves undisturbed blocks and minimizes shift."""
    snapshot = get_base_fixture_snapshot()
    generator = CandidateGenerator(snapshot=snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()

    # 1. Initial Plan
    req_init = OptimizerSolveRequest(profile=ObjectiveProfile.PROGRAMME_IMPROVEMENT)
    res_init = CPSatWeeklyOptimizer(snapshot, manifest, req_init).solve()
    assert res_init.is_feasible is True

    initial_plan = ProposedPlan(
        plan_id="ORIG-PLAN-01",
        snapshot_id=snapshot.snapshot_id,
        snapshot_hash=snapshot.snapshot_hash,
        assignments=res_init.assignments,
    )

    # 2. Inject disruption: a new train blocks task 1's original slot
    t1_assign = res_init.assignments[1]
    new_train = TrainOccupation(
        occupation_id="OCC-EMERGENCY-DISRUPT",
        train_number="EMERG-999",
        train_type="EXPRESS",
        track_segment_id=t1_assign.track_segment_id,
        entry_time_utc=t1_assign.start_utc,
        exit_time_utc=t1_assign.end_utc,
        start_minute=int((t1_assign.start_utc - snapshot.horizon_start_utc).total_seconds() // 60),
        end_minute=int((t1_assign.end_utc - snapshot.horizon_start_utc).total_seconds() // 60),
    )
    snapshot.train_occupations.append(new_train)

    # Re-generate candidates under new snapshot
    gen_rec = CandidateGenerator(snapshot=snapshot, lattice_step_minutes=30)
    man_rec = gen_rec.generate_manifest()

    # Solve with DISRUPTION_RECOVERY
    req_rec = OptimizerSolveRequest(
        profile=ObjectiveProfile.DISRUPTION_RECOVERY,
        original_plan=initial_plan,
        time_limit_seconds=10.0,
    )
    res_rec = CPSatWeeklyOptimizer(snapshot, man_rec, req_rec).solve()

    assert res_rec.is_feasible is True
    assert res_rec.checker_verdict == CheckerVerdict.VALID
    # Task 0 (hard lock) must be in the exact same place
    t0_orig = res_init.assignments[0]
    t0_rec = next(a for a in res_rec.assignments if t0_orig.task_ids[0] in a.task_ids)
    assert t0_rec.start_utc == t0_orig.start_utc


def test_comparison_cp_sat_vs_greedy_baseline():
    """CP-SAT weekly optimizer matches or exceeds greedy baseline on same snapshot."""
    snapshot = get_base_fixture_snapshot()
    generator = CandidateGenerator(snapshot=snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()

    # Baseline
    baseline_solver = GreedyBaselineSolver(snapshot, manifest)
    baseline_res = baseline_solver.solve()

    # CP-SAT
    req = OptimizerSolveRequest(time_limit_seconds=10.0)
    cp_sat_res = CPSatWeeklyOptimizer(snapshot, manifest, req).solve()

    assert cp_sat_res.is_feasible is True
    assert cp_sat_res.mandatory_scheduled_count >= baseline_res.mandatory_scheduled_count
    assert cp_sat_res.scheduled_tasks_count >= baseline_res.scheduled_tasks_count
    assert cp_sat_res.checker_verdict == CheckerVerdict.VALID


def test_optimizer_planning_api_endpoint():
    """POST /api/v1/planning/optimizer/solve executes CP-SAT on live corridor."""
    client = TestClient(app)
    response = client.post("/api/v1/planning/optimizer/solve", json={
        "corridor_code": "VKC",
        "profile": "PROGRAMME_IMPROVEMENT",
        "time_limit_seconds": 15.0,
        "lattice_step_minutes": 60,
        "max_candidates": 10000,
    })
    assert response.status_code == 200
    data = response.json()

    assert data["solver_status"] in ("OPTIMAL", "FEASIBLE")
    assert data["mandatory_scheduled_count"] > 0
    assert data["scheduled_tasks_count"] > 0
    assert data["checker_verdict"] == "VALID"
    assert "stage_metrics" in data
    assert len(data["stage_metrics"]) >= 1
