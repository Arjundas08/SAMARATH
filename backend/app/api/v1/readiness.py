"""
REST API endpoints for Multi-Dimensional Readiness Assessment.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.task import Task
from app.schemas.readiness import TaskReadinessAssessment
from app.domain.readiness import evaluate_task_readiness
from app.db.session import get_db
from app.db.models import TaskModel

router = APIRouter(prefix="/readiness", tags=["Readiness Assessment"])


@router.post("/evaluate", response_model=TaskReadinessAssessment)
async def evaluate_task(task_payload: Task):
    """Evaluate 9-dimension readiness for a provided task payload."""
    return evaluate_task_readiness(task_payload)


@router.get("/task/{task_id}", response_model=TaskReadinessAssessment)
async def evaluate_stored_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Fetch stored task from database and evaluate its current readiness."""
    result = await db.execute(select(TaskModel).where(TaskModel.task_id == str(task_id)))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task_obj = Task(
        task_id=UUID(row.task_id),
        business_key=row.business_key,
        department=row.department,
        sub_department=row.sub_department,
        work_type=row.work_type,
        description=row.description,
        station_from=row.station_from,
        station_to=row.station_to,
        track_segment_id=row.track_segment_id,
        chainage_start_km=row.chainage_start_km,
        chainage_end_km=row.chainage_end_km,
        duration_minutes=row.duration_minutes,
        setup_buffer_minutes=row.setup_buffer_minutes,
        restoration_buffer_minutes=row.restoration_buffer_minutes,
        total_block_minutes=row.total_block_minutes,
        criticality=row.criticality,
        deadline_utc=row.deadline_utc,
        requires_power_block=row.requires_power_block,
        power_block_elementary_section=row.power_block_elementary_section,
        requires_speed_restriction_after=row.requires_speed_restriction_after,
        imposed_speed_kmh=row.imposed_speed_kmh,
        provenance_mode=row.provenance_mode,
        demand_status=row.demand_status,
        created_at_utc=row.created_at_utc,
        created_by=row.created_by,
    )

    return evaluate_task_readiness(task_obj)
