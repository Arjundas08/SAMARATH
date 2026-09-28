"""
API Router: Independent Feasibility Checker & Correctness Oracle.
Implements Blueprint Sections 23 & 41:
- POST /api/v1/checker/verify: Verifies any proposed plan against sealed snapshot.
- POST /api/v1/checker/verify-baseline: Verifies Phase 06 greedy baseline against checker.
- GET /api/v1/checker/rules: Returns regulatory rule catalog.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.db.session import get_db
from app.gateway.service import seal_snapshot_from_db
from app.schemas.snapshot import Snapshot
from app.schemas.checker import (
    ProposedPlan,
    CheckerAssignment,
    CheckerPhase,
    CheckerReport,
    CheckerVerdict,
)
from app.checker.feasibility_checker import IndependentFeasibilityChecker
from app.engine.candidate_generator import CandidateGenerator
from app.engine.greedy_baseline import GreedyBaselineSolver

router = APIRouter(prefix="/checker", tags=["Independent Checker Oracle"])


@router.get("/rules")
def get_checker_regulatory_rules() -> Dict[str, Any]:
    """Returns regulatory rule catalog and source references evaluated by oracle."""
    return {
        "checker_version": IndependentFeasibilityChecker.VERSION,
        "model_evidence_set": IndependentFeasibilityChecker.MODEL_EVIDENCE_SET,
        "supported_checks": [
            {
                "code": "TRAIN_OCCUPATION_COLLISION",
                "authority": "IR General Rules 4.19 / Safety Regulation 2026",
                "resolution": "1-second exact interval sweep",
            },
            {
                "code": "TRACK_COLLISION",
                "authority": "IR G&SR 2026 Para 4.21",
                "resolution": "Spatial segment disjointness",
            },
            {
                "code": "HARD_LOCK_ALTERED",
                "authority": "ADR-006 / Blueprint Sec 22 Inv 1",
                "resolution": "Strict equality mathematical constraint (0s tolerance)",
            },
            {
                "code": "RESOURCE_CAPACITY_EXCEEDED",
                "authority": "Blueprint Sec 23.4 / Capacity Register",
                "resolution": "Discrete event sweep line algorithm",
            },
            {
                "code": "RESOURCE_OUTAGE_CONFLICT",
                "authority": "Section 16 / Depot Overhaul Calendar",
                "resolution": "Calendar outage containment sweep",
            },
            {
                "code": "MANDATORY_TASK_MISSING",
                "authority": "IR Safety Directorate Circular 2026/Safety/01",
                "resolution": "100% statutory Tier-1 coverage",
            },
            {
                "code": "TASK_DUPLICATION",
                "authority": "IR Operating Code Rule 12.4",
                "resolution": "At-most-once task assignment",
            },
            {
                "code": "UNRESOLVED_NEUTRAL_SECTION_FOOTPRINT",
                "authority": "ACTM Vol II Para 20433 / Joint Safety Circular 14",
                "resolution": "Charlie (CHR km 48.0) dual-track isolation",
            },
            {
                "code": "MISSING_RESTORATION_PHASE",
                "authority": "IR Block Working Manual Para 15.2",
                "resolution": "Explicit line clearance & testing verification",
            },
            {
                "code": "AUTONOMOUS_AUTHORITY_TRANSITION_PROHIBITED",
                "authority": "IR Operating Code Rule 4.02",
                "resolution": "Human Section Controller reservation check",
            },
        ],
    }


@router.post("/verify", response_model=CheckerReport)
async def verify_proposed_plan(
    plan: ProposedPlan,
    db: AsyncSession = Depends(get_db),
) -> CheckerReport:
    """
    Independently verifies a proposed plan against the active sealed snapshot.
    Verdict is immutable and computed deterministically.
    """
    snapshot = await seal_snapshot_from_db(db, corridor_code=plan.corridor_code, user_id="checker")
    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)
    return report


@router.post("/verify-baseline", response_model=CheckerReport)
async def verify_baseline_schedule(
    corridor_code: str = "VKC",
    db: AsyncSession = Depends(get_db),
) -> CheckerReport:
    """
    Executes the greedy baseline solver from Phase 06 and passes its materialized
    schedule directly into the independent feasibility checker.
    """
    snapshot = await seal_snapshot_from_db(db, corridor_code=corridor_code, user_id="checker")

    # 1. Generate candidates
    generator = CandidateGenerator(snapshot=snapshot, lattice_step_minutes=30)
    manifest = generator.generate_manifest()

    # 2. Run greedy baseline
    solver = GreedyBaselineSolver(snapshot=snapshot, manifest=manifest)
    baseline_result = solver.solve()

    # 3. Materialize baseline assignments into ProposedPlan
    assignments: List[CheckerAssignment] = []
    for a in baseline_result.assignments:
        phases = [
            CheckerPhase(
                phase_name="SETUP",
                start_utc=a.start_utc,
                end_utc=a.start_utc + timedelta(minutes=15),
                required_resources=a.assigned_resources,
            ),
            CheckerPhase(
                phase_name="EXECUTION",
                start_utc=a.start_utc + timedelta(minutes=15),
                end_utc=a.end_utc - timedelta(minutes=15),
                required_resources=a.assigned_resources,
            ),
            CheckerPhase(
                phase_name="RESTORATION",
                start_utc=a.end_utc - timedelta(minutes=15),
                end_utc=a.end_utc,
                required_resources=a.assigned_resources,
            ),
        ]

        # Resolve neutral section isolation if CHR
        isolated = []
        if "CHR" in a.track_segment_id:
            if "DN" in a.track_segment_id:
                isolated.append(a.track_segment_id.replace("DN", "UP"))
            elif "UP" in a.track_segment_id:
                isolated.append(a.track_segment_id.replace("UP", "DN"))

        assignments.append(
            CheckerAssignment(
                assignment_id=a.assignment_id,
                task_ids=a.task_ids,
                business_keys=a.business_keys,
                track_segment_id=a.track_segment_id,
                start_utc=a.start_utc,
                end_utc=a.end_utc,
                assigned_resources=a.assigned_resources,
                phases=phases,
                requires_power_block=bool(isolated),
                isolated_tracks=isolated,
                is_locked=a.is_locked,
            )
        )

    plan = ProposedPlan(
        plan_id=f"PLAN-BASELINE-{int(datetime.now(timezone.utc).timestamp())}",
        corridor_code=corridor_code,
        snapshot_id=snapshot.snapshot_id,
        snapshot_hash=snapshot.snapshot_hash,
        assignments=assignments,
        metadata={"generator": "GREEDY_BASELINE_V1"},
    )

    checker = IndependentFeasibilityChecker(snapshot)
    report = checker.verify_plan(plan)
    return report
