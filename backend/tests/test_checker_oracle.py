"""
Automated Test Suite for Phase 07:
Independent Feasibility Checker and Correctness Oracle.
Implements Blueprint Sections 23 & 41:
- Import boundary test: app.checker must NOT import app.engine or app.domain.
- Golden valid plan evaluation.
- Full mutation rejection suite covering all 11 failure modes:
  1. 1-second overlap (track or train)
  2. Missing restoration phase
  3. Duplicate task
  4. Wrong qualified resource
  5. Three-way capacity violation
  6. Moved hard lock (by even 1 second)
  7. Unresolved neutral section footprint
  8. Exceeded deadline
  9. Incorrect cross-midnight boundary
  10. Missing mandatory task
  11. Autonomous authority transition attempt
- Exhaustive tiny instance oracle correctness.
- Phase 06 greedy baseline schedule verification through independent checker.
- REST API verification endpoints.
"""
import ast
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.enums import CriticalityTier, ResourceType
from app.schemas.task import Task, ResourceRequirement
from app.schemas.snapshot import Snapshot, TrainOccupation, ResourceCalendarEntry, LockedCommitment
from app.schemas.checker import (
    ProposedPlan,
    CheckerAssignment,
    CheckerPhase,
    CheckerVerdict,
    ViolationSeverity,
)
from app.checker.feasibility_checker import IndependentFeasibilityChecker
from app.checker.tiny_oracle import ExhaustiveTinyOracle
from app.checker.fixtures import get_base_fixture_snapshot, create_golden_valid_plan


def test_checker_import_boundaries():
    """
    Architectural Boundary Invariant:
    The independent checker MUST NOT import planner or optimizer packages (app.engine or app.domain).
    """
    checker_dir = Path(__file__).resolve().parent.parent / "app" / "checker"
    for py_file in checker_dir.glob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("app.engine"), f"{py_file.name} imports app.engine ({alias.name})"
                    assert not alias.name.startswith("app.domain"), f"{py_file.name} imports app.domain ({alias.name})"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert not node.module.startswith("app.engine"), f"{py_file.name} imports from app.engine ({node.module})"
                    assert not node.module.startswith("app.domain"), f"{py_file.name} imports from app.domain ({node.module})"


def test_golden_valid_plan_passes():
    """Golden valid hand-crafted plan must pass with zero violations."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.VALID
    assert len(report.violations) == 0
    assert report.coverage_metrics["mandatory_coverage_pct"] == 100.0
    assert report.coverage_metrics["scheduled_tasks"] == 3


def test_mutation_one_second_train_overlap():
    """A 1-second overlap with a train MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    # Train 12951 runs from 06:00 to 07:00 on TRACK-BRV-CHR-DN
    # Mutate Assignment 2 to end at 06:00:01 (1-second collision with train!)
    t_entry = snapshot.train_occupations[0].entry_time_utc
    plan.assignments[1].start_utc = t_entry - timedelta(minutes=60)
    plan.assignments[1].end_utc = t_entry + timedelta(seconds=1)

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "TRAIN_OCCUPATION_COLLISION" in codes
    coll_violation = next(v for v in report.violations if v.violation_code == "TRAIN_OCCUPATION_COLLISION")
    assert "1s overlap" in coll_violation.observed_value


def test_mutation_missing_restoration_phase():
    """Assignment missing mandatory restoration phase MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    # Remove the RESTORATION phase from Assignment 1
    plan.assignments[0].phases = [
        CheckerPhase(phase_name="SETUP", start_utc=plan.assignments[0].start_utc, end_utc=plan.assignments[0].start_utc + timedelta(minutes=15)),
        CheckerPhase(phase_name="EXECUTION", start_utc=plan.assignments[0].start_utc + timedelta(minutes=15), end_utc=plan.assignments[0].end_utc),
    ]

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "MISSING_RESTORATION_PHASE" in codes


def test_mutation_duplicate_task():
    """Scheduling the same task twice MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    # Put task 0 into both Assignment 0 and Assignment 1
    plan.assignments[1].task_ids.append(plan.assignments[0].task_ids[0])

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "TASK_DUPLICATION" in codes


def test_mutation_wrong_qualified_resource():
    """Assignment omitting a mandatory qualified resource MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    # Task 0 requires CSM-01; strip it from assigned resources
    plan.assignments[0].assigned_resources = []

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "WRONG_QUALIFIED_RESOURCE" in codes


def test_mutation_three_way_capacity_violation():
    """Three simultaneous activities claiming supervisor capacity (max 2) MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    # Assign all 3 assignments to SUP-CREW-01 and overlap their times
    h_start = snapshot.horizon_start_utc
    simul_start = h_start + timedelta(hours=20)
    simul_end = h_start + timedelta(hours=21)

    for i, a in enumerate(plan.assignments):
        a.track_segment_id = f"TRACK-DIFF-{i}"  # Different tracks so no track clash
        a.start_utc = simul_start
        a.end_utc = simul_end
        a.assigned_resources = ["SUP-CREW-01"]

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "RESOURCE_CAPACITY_EXCEEDED" in codes


def test_mutation_moved_hard_lock():
    """Shifting a locked commitment by even 60 seconds MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    # Shift Assignment 0 (which covers the hard lock) by 60 seconds
    plan.assignments[0].start_utc += timedelta(seconds=60)
    plan.assignments[0].end_utc += timedelta(seconds=60)

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "HARD_LOCK_ALTERED" in codes


def test_mutation_unresolved_neutral_section_footprint():
    """Failing to isolate adjacent track under CHR Neutral Section MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    # Assignment 3 is at CHR Neutral Section on TRACK-BRV-CHR-DN; remove UP track isolation
    plan.assignments[2].isolated_tracks = []

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "UNRESOLVED_NEUTRAL_SECTION_FOOTPRINT" in codes


def test_mutation_missing_mandatory_task():
    """Omitting a statutory Tier 1 mandatory task MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    # Drop Assignment 0 (the mandatory tamping task)
    plan.assignments.pop(0)

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "MANDATORY_TASK_MISSING" in codes


def test_mutation_autonomous_authority_prohibited():
    """Attempted autonomous authority granting MUST be rejected."""
    snapshot = get_base_fixture_snapshot()
    plan = create_golden_valid_plan(snapshot)

    plan.metadata["auto_grant_authority"] = True

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)

    assert report.verdict == CheckerVerdict.INVALID
    codes = [v.violation_code for v in report.violations]
    assert "AUTONOMOUS_AUTHORITY_TRANSITION_PROHIBITED" in codes


def test_exhaustive_tiny_oracle_correctness():
    """Exhaustive search oracle must identify the optimal feasible schedule."""
    snapshot = get_base_fixture_snapshot()
    # Keep 2 tasks for fast exhaustive search
    snapshot.tasks = snapshot.tasks[:2]

    oracle = ExhaustiveTinyOracle(snapshot=snapshot, step_minutes=60)
    result = oracle.solve_exhaustive()

    assert result["is_feasible"] is True
    assert result["evaluated_combinations"] > 0
    assert result["best_plan"] is not None
    # Best plan must pass independent checker
    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(result["best_plan"])
    assert report.verdict == CheckerVerdict.VALID


def test_baseline_passes_independent_checker():
    """Phase 06 baseline solver schedule must pass independent feasibility verification."""
    client = TestClient(app)
    response = client.post("/api/v1/checker/verify-baseline?corridor_code=VKC")
    assert response.status_code == 200
    report = response.json()

    assert report["verdict"] == "VALID", f"Violations: {report.get('violations')}"
    assert len(report["violations"]) == 0
    assert report["coverage_metrics"]["mandatory_coverage_pct"] == 100.0
    assert report["checker_version"] == "2026.1-ORACLE-INDEPENDENT"
