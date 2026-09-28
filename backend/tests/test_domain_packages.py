"""
Automated Acceptance Tests for Phase 05:
- Declarative Compatibility Rules & Precedence (PROHIBITED dominates, UNKNOWN on missing evidence, expired evidence fails).
- Human 'verify' action creating approved revisions with documentary evidence.
- Multi-dimensional Readiness Engine (9 dimensions, machine outages, mandatory visibility preserved).
- Spatial Footprint & Neutral Section multi-track isolation.
- Canonical Blueprint Section 18 Work Package Fixtures (75m parallel, 100m sequential, triple capacity failure).
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.enums import (
    DepartmentType,
    CriticalityTier,
    CompatibilityEffect,
    ReadinessDimension,
    ReadinessState,
    WorkPhaseType,
)
from app.schemas.task import Task, ResourceRequirement
from app.schemas.rules import RuleVerificationRequest
from app.domain.rules import (
    evaluate_compatibility,
    get_all_rules,
    verify_rule,
    DeclarativeCompatibilityRule,
)
from app.domain.spatial import resolve_task_footprint, are_spatially_colocated
from app.domain.readiness import evaluate_task_readiness
from app.domain.packages import (
    build_singleton_package,
    build_bundled_package,
    generate_canonical_75min_package,
    generate_canonical_100min_package,
    generate_canonical_capacity_exceeded_triple,
)


def test_declarative_rules_evaluation():
    # 1. Matching ALLOWED rule (Tamping + Point Machine)
    res_allowed = evaluate_compatibility(
        dept_a=DepartmentType.ENGINEERING,
        work_a="TAMPING",
        dept_b=DepartmentType.SIGNALLING,
        work_b="POINT_MACHINE",
    )
    assert res_allowed.effect == CompatibilityEffect.ALLOWED
    assert res_allowed.is_allowed is True
    assert "RULE-IR-001" in res_allowed.matched_rule_ids

    # 2. Matching PROHIBITED rule (BCM + Axle Counter)
    res_prohibited = evaluate_compatibility(
        dept_a=DepartmentType.ENGINEERING,
        work_a="BCM_DEEP_SCREENING",
        dept_b=DepartmentType.SIGNALLING,
        work_b="AXLE_COUNTER",
    )
    assert res_prohibited.effect == CompatibilityEffect.PROHIBITED
    assert res_prohibited.is_prohibited is True
    assert "RULE-IR-002" in res_prohibited.matched_rule_ids

    # 3. Missing rule / Unregistered combination yields UNKNOWN
    res_unknown = evaluate_compatibility(
        dept_a=DepartmentType.ENGINEERING,
        work_a="EXPERIMENTAL_ROBOTIC_PACKING",
        dept_b=DepartmentType.SIGNALLING,
        work_b="UNTESTED_SENSOR",
    )
    assert res_unknown.effect == CompatibilityEffect.UNKNOWN
    assert res_unknown.is_unknown is True
    assert "Unverified combinations strictly block planning bundling" in res_unknown.explanation


def test_expired_evidence_fails():
    # Create an expired rule in memory
    from app.domain.rules import _RULES_REGISTRY
    expired_rule = DeclarativeCompatibilityRule(
        rule_id="RULE-TEST-EXPIRED",
        revision=1,
        department_a=DepartmentType.ENGINEERING,
        work_type_a="TEMP_EXPIRED_PWAY",
        department_b=DepartmentType.SIGNALLING,
        work_type_b="TEMP_EXPIRED_SIG",
        effect=CompatibilityEffect.ALLOWED,
        description="Temporary trial permission that has expired.",
        evidence_reference="TRIAL_SANCTION_2024",
        effective_from_utc=datetime(2024, 1, 1, tzinfo=timezone.utc),
        effective_to_utc=datetime(2024, 12, 31, tzinfo=timezone.utc),
    )
    _RULES_REGISTRY["RULE-TEST-EXPIRED"] = [expired_rule]

    now_2026 = datetime(2026, 9, 26, tzinfo=timezone.utc)
    res = evaluate_compatibility(
        dept_a=DepartmentType.ENGINEERING,
        work_a="TEMP_EXPIRED_PWAY",
        dept_b=DepartmentType.SIGNALLING,
        work_b="TEMP_EXPIRED_SIG",
        now_utc=now_2026,
    )
    assert res.effect == CompatibilityEffect.UNKNOWN
    assert "expired on 2024-12-31" in res.explanation


def test_rule_verify_creates_approved_revision():
    req = RuleVerificationRequest(
        rule_id="RULE-IR-005",
        new_effect=CompatibilityEffect.ALLOWED,
        evidence_document="JOINT_SAFETY_CIRCULAR_JSC_2026_09",
        notes="Sectional test completed with verified portable earthing equipment.",
        approving_officer="Principal Chief Electrical Engineer",
    )
    updated = verify_rule(req, user_id="test_reviewer")
    assert updated.revision >= 2
    assert updated.effect == CompatibilityEffect.ALLOWED
    assert updated.evidence_reference == "JOINT_SAFETY_CIRCULAR_JSC_2026_09"
    assert updated.approver == "Principal Chief Electrical Engineer"
    assert updated.superseded_by_revision is None

    # Verify that evaluation now picks up the updated revision
    eval_res = evaluate_compatibility(
        dept_a=DepartmentType.ELECTRICAL,
        work_a="NEUTRAL_SECTION_OVERHAUL",
        dept_b=DepartmentType.ENGINEERING,
        work_b="MANUAL_PACKING",
    )
    assert eval_res.effect == CompatibilityEffect.ALLOWED


def test_readiness_9_dimensions_and_outages():
    task = Task(
        task_id=uuid4(),
        business_key="TASK-READINESS-TEST-01",
        department=DepartmentType.ENGINEERING,
        sub_department="P-WAY",
        work_type="TAMPING",
        description="Routine tamping",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=30.0,
        chainage_end_km=32.0,
        duration_minutes=60,
        criticality=CriticalityTier.TIER_1_MANDATORY,
        deadline_utc=datetime(2026, 10, 15, tzinfo=timezone.utc),
        required_resources=[
            ResourceRequirement(resource_type="MACHINE", resource_id="BCM-01", quantity=1),
            ResourceRequirement(resource_type="CREW", resource_id="GANG-ENG-01", quantity=1),
        ],
        total_block_minutes=120,
    )

    # 1. Normal day (Monday Oct 12, 2026) -> READY
    monday_dt = datetime(2026, 10, 12, 10, 0, tzinfo=timezone.utc)
    assert monday_dt.weekday() == 0
    readiness_mon = evaluate_task_readiness(task, planned_start_utc=monday_dt)
    assert readiness_mon.overall_state == ReadinessState.READY
    assert len(readiness_mon.dimensions) == 9
    assert readiness_mon.is_executable is True

    # 2. Wednesday (Oct 14, 2026) -> BCM-01 has scheduled depot overhaul outage!
    wednesday_dt = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)
    assert wednesday_dt.weekday() == 2
    readiness_wed = evaluate_task_readiness(task, planned_start_utc=wednesday_dt)
    assert readiness_wed.overall_state == ReadinessState.NOT_READY
    assert readiness_wed.worst_dimension == ReadinessDimension.MACHINE_HEALTH
    assert "scheduled outage" in readiness_wed.worst_dimension_reason
    assert readiness_wed.is_executable is False

    # Invariant check: Mandatory status is NEVER lowered!
    assert readiness_wed.details["is_mandatory"] is True
    assert readiness_wed.details["criticality"] == "TIER_1_MANDATORY"


def test_spatial_neutral_section_multi_track_isolation():
    # 1. Normal section outside Neutral Section
    fp_normal = resolve_task_footprint(
        track_segment_id="TRACK-ALP-BRV-UP",
        chainage_start_km=5.0,
        chainage_end_km=8.0,
        requires_power_block=False,
    )
    assert fp_normal.is_resolved is True
    assert fp_normal.is_neutral_section is False
    assert len(fp_normal.affected_adjacent_tracks) == 0

    # 2. Section across Neutral Section at CHR km 48.0 requiring power block
    fp_ns = resolve_task_footprint(
        track_segment_id="TRACK-BRV-CHR-UP",
        chainage_start_km=47.5,
        chainage_end_km=48.5,
        requires_power_block=True,
    )
    assert fp_ns.is_resolved is True
    assert fp_ns.is_neutral_section is True
    assert "ELEM-CHR-NS-01" in fp_ns.elementary_sections
    # De-energization of neutral section isolates both UP and DOWN lines!
    assert "TRACK-BRV-CHR-DN" in fp_ns.affected_adjacent_tracks

    # 3. Unknown segment blocks candidate with UNKNOWN_MAPPING reason
    fp_bad = resolve_task_footprint(
        track_segment_id="TRACK-NONEXISTENT-XX",
        chainage_start_km=10.0,
        chainage_end_km=15.0,
    )
    assert fp_bad.is_resolved is False
    assert "Unknown track segment" in fp_bad.unresolved_reason


def test_canonical_75min_parallel_package():
    pkg = generate_canonical_75min_package()
    assert pkg.recipe.total_duration_minutes == 75
    assert pkg.recipe.is_sequential is False
    assert pkg.recipe.assumption_badge == "[TEST_ASSUMPTION]"
    assert len(pkg.recipe.phases) == 5  # 1 prep + 2 parallel task executions + 1 testing + 1 restoration

    prep = next(p for p in pkg.recipe.phases if p.phase_type == WorkPhaseType.PREPARATION)
    test = next(p for p in pkg.recipe.phases if p.phase_type == WorkPhaseType.TESTING)
    rest = next(p for p in pkg.recipe.phases if p.phase_type == WorkPhaseType.RESTORATION)
    execs = [p for p in pkg.recipe.phases if p.phase_type == WorkPhaseType.EXECUTION]

    assert prep.duration_minutes == 10
    assert len(execs) == 2
    assert max(e.duration_minutes for e in execs) == 40
    # Both parallel executions start at offset 10 (concurrency)
    assert all(e.offset_start_minutes == 10 for e in execs)
    assert test.offset_start_minutes == 50
    assert test.duration_minutes == 15
    assert rest.offset_start_minutes == 65
    assert rest.duration_minutes == 10
    assert pkg.recipe.total_duration_minutes == 75
    assert pkg.cumulative_capacity_required == 2



def test_canonical_100min_sequential_package():
    pkg = generate_canonical_100min_package()
    assert pkg.recipe.total_duration_minutes == 100
    assert pkg.recipe.is_sequential is True
    assert pkg.recipe.assumption_badge == "[TEST_ASSUMPTION]"
    assert pkg.is_eligible is True

    phases = pkg.recipe.phases
    # Setup (10) + Eng (40) + S&T (25) + Testing (15) + Restoration (10) = 100
    total_time = sum(p.duration_minutes for p in phases)
    assert total_time == 100


def test_canonical_triple_capacity_exceeded():
    pkg = generate_canonical_capacity_exceeded_triple()
    # All pairs are valid, but triple cumulative capacity (3) > available limit (2)
    assert pkg.cumulative_capacity_required == 3
    assert pkg.available_capacity == 2
    assert pkg.is_eligible is False
    assert "cumulative package demand (3 units) exceeds available shared crew capacity (2 units)" in pkg.ineligibility_reason


def test_api_rules_and_packages():
    client = TestClient(app)

    # 1. List rules
    r_rules = client.get("/api/v1/rules")
    assert r_rules.status_code == 200
    rules = r_rules.json()
    assert len(rules) >= 7

    # 2. Evaluate rule via API
    r_eval = client.post("/api/v1/rules/evaluate", json={
        "department_a": "ENGINEERING",
        "work_type_a": "TAMPING",
        "department_b": "SIGNALLING",
        "work_type_b": "POINT_MACHINE",
    })
    assert r_eval.status_code == 200
    assert r_eval.json()["effect"] == "ALLOWED"

    # 3. Canonical fixtures
    r_fix = client.get("/api/v1/packages/fixtures")
    assert r_fix.status_code == 200
    fixtures = r_fix.json()
    assert len(fixtures) == 3
    assert fixtures[0]["recipe"]["total_duration_minutes"] == 75
    assert fixtures[1]["recipe"]["total_duration_minutes"] == 100
    assert fixtures[2]["is_eligible"] is False
