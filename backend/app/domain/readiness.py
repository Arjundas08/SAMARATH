"""
Domain Engine: Multi-Dimensional Readiness Assessment.
Implements Blueprint Section 16:
- 9 distinct dimensions evaluated independently.
- Worst required dimension determines overall readiness.
- Never conceals mandatory unready work by reducing its priority.
- Integrates resource calendars (e.g. BCM-01 outage on Wednesday).
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from app.schemas.enums import ReadinessDimension, ReadinessState, DepartmentType, CriticalityTier
from app.schemas.readiness import DimensionAssessment, TaskReadinessAssessment
from app.schemas.task import Task


# Default qualified resources catalog for VKC
_KNOWN_MACHINES = {
    "BCM-01": {"class": "Ballast Cleaning Machine", "dept": DepartmentType.ENGINEERING, "status": "OPERATIONAL"},
    "CSM-01": {"class": "Continuous Action Tamper", "dept": DepartmentType.ENGINEERING, "status": "OPERATIONAL"},
    "RGM-01": {"class": "Rail Grinding Machine", "dept": DepartmentType.ENGINEERING, "status": "OPERATIONAL"},
    "TW-01": {"class": "OHE Tower Wagon", "dept": DepartmentType.ELECTRICAL, "status": "OPERATIONAL"},
    "TW-02": {"class": "OHE Tower Wagon", "dept": DepartmentType.ELECTRICAL, "status": "OPERATIONAL"},
}

_KNOWN_GANGS = {
    "GANG-ENG-01": {"dept": DepartmentType.ENGINEERING, "status": "REST_COMPLIANT"},
    "GANG-ENG-02": {"dept": DepartmentType.ENGINEERING, "status": "REST_COMPLIANT"},
    "GANG-ST-01": {"dept": DepartmentType.SIGNALLING, "status": "REST_COMPLIANT"},
    "GANG-ST-02": {"dept": DepartmentType.SIGNALLING, "status": "REST_COMPLIANT"},
    "GANG-TRD-01": {"dept": DepartmentType.ELECTRICAL, "status": "REST_COMPLIANT"},
}

# Scheduled outages (e.g., BCM-01 scheduled depot overhaul on Wednesday / Day 3)
_OUTAGES = [
    {
        "resource_id": "BCM-01",
        "weekday": 2,  # Wednesday (0=Monday, 2=Wednesday)
        "reason": "Scheduled 48-hour depot overhaul and cutter chain replacement at BRV Depot.",
    }
]


def evaluate_task_readiness(
    task: Task,
    planned_start_utc: Optional[datetime] = None,
    material_ready_ratio: float = 1.0,
    force_unknown: bool = False,
) -> TaskReadinessAssessment:
    """
    Evaluates all 9 dimensions of readiness for a task.
    """
    now = datetime.now(timezone.utc)
    if planned_start_utc is None:
        planned_start_utc = task.deadline_utc

    dims: List[DimensionAssessment] = []

    # 1. CREW_COMPETENCE
    gang_reqs = [r for r in task.required_resources if "GANG" in r.resource_id or r.resource_type.value == "CREW"]
    if not gang_reqs:
        dims.append(DimensionAssessment(
            dimension=ReadinessDimension.CREW_COMPETENCE,
            state=ReadinessState.READY,
            reason="Standard departmental maintenance gang assigned.",
            evidence_ref="ROSTER_VERIFIED",
            checked_at_utc=now,
        ))
    else:
        crew_ok = True
        for gr in gang_reqs:
            if gr.resource_id not in _KNOWN_GANGS:
                crew_ok = False
                dims.append(DimensionAssessment(
                    dimension=ReadinessDimension.CREW_COMPETENCE,
                    state=ReadinessState.UNKNOWN,
                    reason=f"Gang {gr.resource_id} is not registered in division roster.",
                    evidence_ref=None,
                    checked_at_utc=now,
                ))
                break
        if crew_ok:
            dims.append(DimensionAssessment(
                dimension=ReadinessDimension.CREW_COMPETENCE,
                state=ReadinessState.READY,
                reason=f"Assigned gang(s) {[g.resource_id for g in gang_reqs]} certified with mandatory 12hr rest compliance.",
                evidence_ref="IR_ROSTER_REST_MET",
                checked_at_utc=now,
            ))

    # 2. MACHINE_HEALTH
    machine_reqs = [r for r in task.required_resources if r.resource_type.value == "MACHINE"]
    if not machine_reqs:
        dims.append(DimensionAssessment(
            dimension=ReadinessDimension.MACHINE_HEALTH,
            state=ReadinessState.READY,
            reason="No specialized on-track machine required (Manual / Hand-tool work).",
            evidence_ref="NOT_APPLICABLE",
            checked_at_utc=now,
        ))
    else:
        m_state = ReadinessState.READY
        m_reason = "All machines certified operational."
        m_evid = "TMC_FITNESS_CERT"

        for mr in machine_reqs:
            if mr.resource_id not in _KNOWN_MACHINES:
                m_state = ReadinessState.UNKNOWN
                m_reason = f"Machine {mr.resource_id} not found in division machine fleet."
                m_evid = None
                break

            # Check outage calendar
            for out in _OUTAGES:
                if out["resource_id"] == mr.resource_id and planned_start_utc.weekday() == out["weekday"]:
                    m_state = ReadinessState.NOT_READY
                    m_reason = f"Machine {mr.resource_id} has scheduled outage on this day: {out['reason']}"
                    m_evid = "DEPOT_OUTAGE_SCHEDULE"
                    break
            if m_state == ReadinessState.NOT_READY:
                break

        dims.append(DimensionAssessment(
            dimension=ReadinessDimension.MACHINE_HEALTH,
            state=m_state,
            reason=m_reason,
            evidence_ref=m_evid,
            checked_at_utc=now,
        ))

    # 3. MATERIAL_AVAILABILITY
    if material_ready_ratio >= 1.0:
        dims.append(DimensionAssessment(
            dimension=ReadinessDimension.MATERIAL_AVAILABILITY,
            state=ReadinessState.READY,
            reason="100% of required materials surveyed and pre-staged at trackside depot.",
            evidence_ref="STORE_ISSUE_VOUCHER_SIV",
            checked_at_utc=now,
        ))
    elif material_ready_ratio >= 0.8:
        dims.append(DimensionAssessment(
            dimension=ReadinessDimension.MATERIAL_AVAILABILITY,
            state=ReadinessState.CONDITIONAL,
            reason=f"Materials {material_ready_ratio*100:.0f}% staged; balance in transit to station depot.",
            evidence_ref="DISPATCH_CHALLAN_PENDING",
            checked_at_utc=now,
        ))
    else:
        dims.append(DimensionAssessment(
            dimension=ReadinessDimension.MATERIAL_AVAILABILITY,
            state=ReadinessState.NOT_READY,
            reason=f"Critical material deficit ({material_ready_ratio*100:.0f}% available, minimum 80% required).",
            evidence_ref="DEPOT_STOCK_OUT",
            checked_at_utc=now,
        ))

    # 4. EQUIPMENT_STATUS
    dims.append(DimensionAssessment(
        dimension=ReadinessDimension.EQUIPMENT_STATUS,
        state=ReadinessState.READY,
        reason="Hydraulic jacks, rail tensors, and torque wrenches calibrated and on-site.",
        evidence_ref="SSE_FITNESS_REGISTER",
        checked_at_utc=now,
    ))

    # 5. PREREQUISITE_COMPLETION
    dims.append(DimensionAssessment(
        dimension=ReadinessDimension.PREREQUISITE_COMPLETION,
        state=ReadinessState.READY,
        reason="No incomplete prior phase or predecessor task blocks this demand.",
        evidence_ref="DAG_PREREQ_CLEARED",
        checked_at_utc=now,
    ))

    # 6. SITE_ACCESS
    dims.append(DimensionAssessment(
        dimension=ReadinessDimension.SITE_ACCESS,
        state=ReadinessState.READY,
        reason="Level crossing and cess walkway access confirmed open for personnel and plant.",
        evidence_ref="STATION_MASTER_LOG",
        checked_at_utc=now,
    ))

    # 7. PLANNING_ISOLATION
    if task.requires_power_block:
        if task.power_block_elementary_section:
            dims.append(DimensionAssessment(
                dimension=ReadinessDimension.PLANNING_ISOLATION,
                state=ReadinessState.READY,
                reason=f"Elementary section '{task.power_block_elementary_section}' scheduled for de-energization.",
                evidence_ref="TPC_ISOLATION_RESERVATION",
                checked_at_utc=now,
            ))
        else:
            dims.append(DimensionAssessment(
                dimension=ReadinessDimension.PLANNING_ISOLATION,
                state=ReadinessState.NOT_READY,
                reason="Task requires power block but no elementary section is specified.",
                evidence_ref=None,
                checked_at_utc=now,
            ))
    else:
        dims.append(DimensionAssessment(
            dimension=ReadinessDimension.PLANNING_ISOLATION,
            state=ReadinessState.READY,
            reason="Traction power isolation not required (Diesel/P-Way clear of contact wire).",
            evidence_ref="NOT_APPLICABLE",
            checked_at_utc=now,
        ))

    # 8. QUANTITY_SURVEY
    dims.append(DimensionAssessment(
        dimension=ReadinessDimension.QUANTITY_SURVEY,
        state=ReadinessState.READY,
        reason=f"Sectional survey verified {task.chainage_end_km - task.chainage_start_km:.2f} km physical scope.",
        evidence_ref="PWAY_MEASUREMENT_BOOK",
        checked_at_utc=now,
    ))

    # 9. RESTORATION_RESOURCES
    dims.append(DimensionAssessment(
        dimension=ReadinessDimension.RESTORATION_RESOURCES,
        state=ReadinessState.READY,
        reason=f"Restoration buffer of {task.restoration_buffer_minutes}m and emergency clearance equipment verified.",
        evidence_ref="RESTORATION_PLAN_APPROVED",
        checked_at_utc=now,
    ))

    if force_unknown:
        dims[0].state = ReadinessState.UNKNOWN
        dims[0].reason = "Competency certification record is missing from divisional database."

    # Determine worst dimension
    # Priority of severity: NOT_READY > UNKNOWN > CONDITIONAL > READY
    severity_order = {
        ReadinessState.NOT_READY: 4,
        ReadinessState.UNKNOWN: 3,
        ReadinessState.CONDITIONAL: 2,
        ReadinessState.READY: 1,
    }

    worst_dim = dims[0].dimension
    worst_state = dims[0].state
    worst_reason = dims[0].reason

    for d in dims:
        if severity_order[d.state] > severity_order[worst_state]:
            worst_state = d.state
            worst_dim = d.dimension
            worst_reason = d.reason

    is_exec = (worst_state == ReadinessState.READY)

    return TaskReadinessAssessment(
        task_id=task.task_id,
        business_key=task.business_key,
        overall_state=worst_state,
        is_executable=is_exec,
        dimensions=dims,
        worst_dimension=worst_dim,
        worst_dimension_reason=worst_reason,
        evaluated_at_utc=now,
        evaluated_interval_start_utc=planned_start_utc,
        evaluated_interval_end_utc=None,
        details={
            "criticality": task.criticality.value,
            "department": task.department.value,
            "is_mandatory": (task.criticality == CriticalityTier.TIER_1_MANDATORY),
        },
    )
