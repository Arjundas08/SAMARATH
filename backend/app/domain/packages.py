"""
Domain Engine: Executable Work Package Generator and Phase DAG Materializer.
Implements Blueprint Section 18:
- Generates singletons, pairs, and triples without destructively merging source tasks.
- Pairwise compatibility does not establish cumulative capacity: enforces whole-package capacity checks.
- Materializes Phase DAG with fixed recipe offsets (PREPARATION, EXECUTION, TESTING, RESTORATION).
- Implements exact canonical test examples:
  1. 75-minute concurrent package (Setup 10, Eng 40 || S&T 25, Test 15, Rest 10).
  2. 100-minute sequential package (Setup 10, Eng 40 -> S&T 25, Test 15, Rest 10).
  3. Cumulative capacity failure (3 tasks whose pairs pass, but triple exceeds capacity 2).
"""
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone

from app.schemas.enums import DepartmentType, CompatibilityEffect, WorkPhaseType
from app.schemas.work_package import PackagePhase, WorkPackageRecipe, WorkPackage
from app.schemas.task import Task
from app.domain.rules import evaluate_compatibility
from app.domain.spatial import resolve_task_footprint, are_spatially_colocated


def build_singleton_package(task: Task) -> WorkPackage:
    """
    Constructs an executable singleton work package for a single task.
    """
    setup = task.setup_buffer_minutes
    dur = task.duration_minutes
    rest = task.restoration_buffer_minutes
    total = task.total_block_minutes or (setup + dur + rest)

    phases = [
        PackagePhase(
            phase_type=WorkPhaseType.PREPARATION,
            duration_minutes=setup,
            offset_start_minutes=0,
            offset_end_minutes=setup,
            required_resources=[r.resource_id for r in task.required_resources],
            description=f"Possession takeover, warning flags, machine positioning for {task.business_key}",
        ),
        PackagePhase(
            phase_type=WorkPhaseType.EXECUTION,
            duration_minutes=dur,
            offset_start_minutes=setup,
            offset_end_minutes=setup + dur,
            required_resources=[r.resource_id for r in task.required_resources],
            description=f"Physical productive execution: {task.description}",
        ),
        PackagePhase(
            phase_type=WorkPhaseType.RESTORATION,
            duration_minutes=rest,
            offset_start_minutes=setup + dur,
            offset_end_minutes=total,
            required_resources=[r.resource_id for r in task.required_resources],
            description=f"Track clearance, equipment retrieval, hand-back for {task.business_key}",
        ),
    ]

    recipe = WorkPackageRecipe(
        recipe_id=f"RECIPE-SINGLE-{task.business_key}",
        name=f"Singleton Execution ({task.business_key})",
        total_duration_minutes=total,
        is_sequential=False,
        phases=phases,
        assumption_badge="[TEST_ASSUMPTION]",
    )

    return WorkPackage(
        package_id=f"PKG-SINGLE-{task.business_key}",
        task_ids=[task.task_id],
        business_keys=[task.business_key],
        departments=[task.department],
        track_segment_id=task.track_segment_id,
        chainage_start_km=task.chainage_start_km,
        chainage_end_km=task.chainage_end_km,
        requires_power_block=task.requires_power_block,
        power_block_elementary_section=task.power_block_elementary_section,
        compatibility_verdict=CompatibilityEffect.ALLOWED,
        cumulative_capacity_required=1,
        available_capacity=2,
        is_eligible=True,
        ineligibility_reason=None,
        recipe=recipe,
        metadata={"package_type": "SINGLETON"},
    )


def build_bundled_package(
    tasks: List[Task],
    is_sequential: bool = False,
    shared_capacity_limit: int = 2,
    custom_setup_min: Optional[int] = None,
    custom_test_min: Optional[int] = None,
    custom_rest_min: Optional[int] = None,
) -> WorkPackage:
    """
    Constructs a bundled multi-department work package for 2 or 3 tasks.
    Enforces:
    1. Spatial colocation on same track segment.
    2. Pairwise declarative compatibility rules.
    3. Whole-package cumulative capacity check (e.g. shared supervisor crew limit).
    4. Explicit phase DAG materialization.
    """
    if len(tasks) < 2:
        return build_singleton_package(tasks[0])

    biz_keys = [t.business_key for t in tasks]
    t_ids = [t.task_id for t in tasks]
    depts = list({t.department for t in tasks})
    seg_id = tasks[0].track_segment_id

    # 1. Spatial check
    fp0 = resolve_task_footprint(
        tasks[0].track_segment_id,
        tasks[0].chainage_start_km,
        tasks[0].chainage_end_km,
        tasks[0].requires_power_block,
        tasks[0].power_block_elementary_section,
    )

    for other in tasks[1:]:
        fpo = resolve_task_footprint(
            other.track_segment_id,
            other.chainage_start_km,
            other.chainage_end_km,
            other.requires_power_block,
            other.power_block_elementary_section,
        )
        if not are_spatially_colocated(fp0, fpo):
            return WorkPackage(
                package_id=f"PKG-INELIGIBLE-{'-'.join(biz_keys)}",
                task_ids=t_ids,
                business_keys=biz_keys,
                departments=depts,
                track_segment_id=seg_id,
                chainage_start_km=min(t.chainage_start_km for t in tasks),
                chainage_end_km=max(t.chainage_end_km for t in tasks),
                compatibility_verdict=CompatibilityEffect.PROHIBITED,
                is_eligible=False,
                ineligibility_reason=f"Tasks {tasks[0].business_key} and {other.business_key} are not spatially colocated on the same track segment.",
                recipe=WorkPackageRecipe(
                    recipe_id="RECIPE-INELIGIBLE",
                    name="Ineligible Spatial Footprint",
                    total_duration_minutes=0,
                    phases=[],
                ),
            )

    # 2. Pairwise compatibility check
    has_prohibited = False
    has_unknown = False
    prohibited_reason = None
    unknown_reason = None

    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            res = evaluate_compatibility(
                tasks[i].department,
                tasks[i].work_type,
                tasks[j].department,
                tasks[j].work_type,
            )
            if res.effect == CompatibilityEffect.PROHIBITED:
                has_prohibited = True
                prohibited_reason = res.explanation
                break
            elif res.effect == CompatibilityEffect.UNKNOWN:
                has_unknown = True
                unknown_reason = res.explanation

    overall_effect = CompatibilityEffect.ALLOWED
    if has_prohibited:
        overall_effect = CompatibilityEffect.PROHIBITED
    elif has_unknown:
        overall_effect = CompatibilityEffect.UNKNOWN

    # 3. Cumulative Capacity Check
    # Each task requires 1 unit of shared safety supervisor crew
    cumulative_demand = len(tasks)
    is_capacity_exceeded = cumulative_demand > shared_capacity_limit

    is_eligible = (overall_effect == CompatibilityEffect.ALLOWED) and not is_capacity_exceeded
    ineligibility_reason = None
    if has_prohibited:
        ineligibility_reason = prohibited_reason
    elif has_unknown:
        ineligibility_reason = unknown_reason
    elif is_capacity_exceeded:
        ineligibility_reason = f"Pairwise compatibility satisfied, but cumulative package demand ({cumulative_demand} units) exceeds available shared crew capacity ({shared_capacity_limit} units)."

    # 4. Materialize Phase DAG
    setup = custom_setup_min if custom_setup_min is not None else max(t.setup_buffer_minutes for t in tasks)
    test = custom_test_min if custom_test_min is not None else max(15, max((t.setup_buffer_minutes // 2) for t in tasks))
    rest = custom_rest_min if custom_rest_min is not None else max(t.restoration_buffer_minutes for t in tasks)

    phases: List[PackagePhase] = []
    phases.append(PackagePhase(
        phase_type=WorkPhaseType.PREPARATION,
        duration_minutes=setup,
        offset_start_minutes=0,
        offset_end_minutes=setup,
        required_resources=list({r.resource_id for t in tasks for r in t.required_resources}),
        description=f"Shared possession takeover and pre-work protection for bundle [{', '.join(biz_keys)}]",
    ))

    if is_sequential:
        # Sequential execution
        curr_offset = setup
        for t in tasks:
            phases.append(PackagePhase(
                phase_type=WorkPhaseType.EXECUTION,
                duration_minutes=t.duration_minutes,
                offset_start_minutes=curr_offset,
                offset_end_minutes=curr_offset + t.duration_minutes,
                required_resources=[r.resource_id for r in t.required_resources],
                description=f"Sequential execution of {t.business_key} ({t.description})",
            ))
            curr_offset += t.duration_minutes
        exec_end = curr_offset
    else:
        # Concurrent parallel execution
        max_dur = max(t.duration_minutes for t in tasks)
        for t in tasks:
            phases.append(PackagePhase(
                phase_type=WorkPhaseType.EXECUTION,
                duration_minutes=t.duration_minutes,
                offset_start_minutes=setup,
                offset_end_minutes=setup + t.duration_minutes,
                required_resources=[r.resource_id for r in t.required_resources],
                description=f"Parallel execution of {t.business_key} ({t.description})",
            ))
        exec_end = setup + max_dur

    phases.append(PackagePhase(
        phase_type=WorkPhaseType.TESTING,
        duration_minutes=test,
        offset_start_minutes=exec_end,
        offset_end_minutes=exec_end + test,
        required_resources=list({r.resource_id for t in tasks for r in t.required_resources}),
        description=f"Joint multi-departmental testing for bundle [{', '.join(biz_keys)}]",
    ))

    total = exec_end + test + rest
    phases.append(PackagePhase(
        phase_type=WorkPhaseType.RESTORATION,
        duration_minutes=rest,
        offset_start_minutes=exec_end + test,
        offset_end_minutes=total,
        required_resources=list({r.resource_id for t in tasks for r in t.required_resources}),
        description=f"Site normalization, emergency clearance, and track hand-back for [{', '.join(biz_keys)}]",
    ))

    recipe_name = f"Bundled {'Sequential' if is_sequential else 'Concurrent'} Package ({len(tasks)} tasks)"
    recipe = WorkPackageRecipe(
        recipe_id=f"RECIPE-BUNDLE-{'-'.join(biz_keys)}-{'SEQ' if is_sequential else 'PAR'}",
        name=recipe_name,
        total_duration_minutes=total,
        is_sequential=is_sequential,
        phases=phases,
        assumption_badge="[TEST_ASSUMPTION]",
    )

    req_pb = any(t.requires_power_block for t in tasks)
    pb_sec = next((t.power_block_elementary_section for t in tasks if t.power_block_elementary_section), None)

    return WorkPackage(
        package_id=f"PKG-BUNDLE-{'-'.join(biz_keys)}",
        task_ids=t_ids,
        business_keys=biz_keys,
        departments=depts,
        track_segment_id=seg_id,
        chainage_start_km=min(t.chainage_start_km for t in tasks),
        chainage_end_km=max(t.chainage_end_km for t in tasks),
        requires_power_block=req_pb,
        power_block_elementary_section=pb_sec,
        compatibility_verdict=overall_effect,
        cumulative_capacity_required=cumulative_demand,
        available_capacity=shared_capacity_limit,
        is_eligible=is_eligible,
        ineligibility_reason=ineligibility_reason,
        recipe=recipe,
        metadata={
            "package_type": "BUNDLE",
            "is_sequential": is_sequential,
            "tasks_count": len(tasks),
        },
    )


# =========================================================================
# Canonical Demonstration Fixtures (Blueprint Section 18)
# =========================================================================

def generate_canonical_75min_package() -> WorkPackage:
    """
    Blueprint Section 18 Canonical Example A:
    Setup 10 min -> Engineering 40 min || S&T 25 min in allowed parallel -> Testing 15 min -> Restoration 10 min.
    Total: 10 + 40 + 15 + 10 = 75 minutes.
    """
    task_eng = Task(
        task_id=uuid4(),
        business_key="TASK-ENG-DEMO-01",
        department=DepartmentType.ENGINEERING,
        sub_department="P-WAY",
        work_type="TAMPING",
        description="P-Way track tamping on turn-out zone 104",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=41.2,
        chainage_end_km=42.8,
        duration_minutes=40,
        setup_buffer_minutes=10,
        restoration_buffer_minutes=10,
        deadline_utc=datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc),
        total_block_minutes=60,
    )

    task_st = Task(
        task_id=uuid4(),
        business_key="TASK-ST-DEMO-02",
        department=DepartmentType.SIGNALLING,
        sub_department="SIGNALLING",
        work_type="POINT_MACHINE",
        description="S&T point machine overhaul & detector slide lubrication",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=41.5,
        chainage_end_km=42.0,
        duration_minutes=25,
        setup_buffer_minutes=10,
        restoration_buffer_minutes=10,
        deadline_utc=datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc),
        total_block_minutes=45,
    )

    return build_bundled_package(
        tasks=[task_eng, task_st],
        is_sequential=False,
        shared_capacity_limit=2,
        custom_setup_min=10,
        custom_test_min=15,
        custom_rest_min=10,
    )


def generate_canonical_100min_package() -> WorkPackage:
    """
    Blueprint Section 18 Canonical Example B:
    Setup 10 min -> Engineering 40 min -> S&T 25 min in sequential -> Testing 15 min -> Restoration 10 min.
    Total: 10 + (40 + 25) + 15 + 10 = 100 minutes.
    """
    task_eng = Task(
        task_id=uuid4(),
        business_key="TASK-ENG-DEMO-01",
        department=DepartmentType.ENGINEERING,
        sub_department="P-WAY",
        work_type="TAMPING",
        description="P-Way track tamping on turn-out zone 104",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=41.2,
        chainage_end_km=42.8,
        duration_minutes=40,
        setup_buffer_minutes=10,
        restoration_buffer_minutes=10,
        deadline_utc=datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc),
        total_block_minutes=60,
    )

    task_st = Task(
        task_id=uuid4(),
        business_key="TASK-ST-DEMO-02",
        department=DepartmentType.SIGNALLING,
        sub_department="SIGNALLING",
        work_type="POINT_MACHINE",
        description="S&T point machine overhaul (Shared exclusive crew)",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=41.5,
        chainage_end_km=42.0,
        duration_minutes=25,
        setup_buffer_minutes=10,
        restoration_buffer_minutes=10,
        deadline_utc=datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc),
        total_block_minutes=45,
    )

    return build_bundled_package(
        tasks=[task_eng, task_st],
        is_sequential=True,
        shared_capacity_limit=2,
        custom_setup_min=10,
        custom_test_min=15,
        custom_rest_min=10,
    )


def generate_canonical_capacity_exceeded_triple() -> WorkPackage:
    """
    Blueprint Section 18 Canonical Example C:
    Three-task combination where each individual pair is compatible (capacity <= 2),
    but the combined triple requires 3 units exceeding the available shared capacity (2).
    """
    t1 = Task(
        task_id=uuid4(),
        business_key="TASK-ENG-TRIPLE-01",
        department=DepartmentType.ENGINEERING,
        sub_department="P-WAY",
        work_type="TAMPING",
        description="Turn-out tamping",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=41.2,
        chainage_end_km=42.8,
        duration_minutes=40,
        setup_buffer_minutes=10,
        restoration_buffer_minutes=10,
        deadline_utc=datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc),
        total_block_minutes=60,
    )

    t2 = Task(
        task_id=uuid4(),
        business_key="TASK-ST-TRIPLE-02",
        department=DepartmentType.SIGNALLING,
        sub_department="SIGNALLING",
        work_type="POINT_MACHINE",
        description="Point machine overhaul",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=41.5,
        chainage_end_km=42.0,
        duration_minutes=25,
        setup_buffer_minutes=10,
        restoration_buffer_minutes=10,
        deadline_utc=datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc),
        total_block_minutes=45,
    )

    t3 = Task(
        task_id=uuid4(),
        business_key="TASK-TRD-TRIPLE-03",
        department=DepartmentType.ELECTRICAL,
        sub_department="TRD",
        work_type="OHE_INSPECTION",
        description="OHE contact wire height inspection",
        station_from="BRV",
        station_to="CHR",
        track_segment_id="TRACK-BRV-CHR-DN",
        chainage_start_km=41.0,
        chainage_end_km=43.0,
        duration_minutes=30,
        setup_buffer_minutes=10,
        restoration_buffer_minutes=10,
        deadline_utc=datetime(2026, 10, 15, 18, 0, tzinfo=timezone.utc),
        requires_power_block=True,
        power_block_elementary_section="ELEM-BRV-CHR-01",
        total_block_minutes=50,
    )

    # All pairs (t1+t2, t1+t3, t2+t3) are compatible in rules,
    # but triple has cumulative demand 3 > available capacity 2!
    return build_bundled_package(
        tasks=[t1, t2, t3],
        is_sequential=False,
        shared_capacity_limit=2,  # Limit is 2!
    )
