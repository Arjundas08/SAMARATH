"""
Task and Maintenance Demand API endpoints.
Provides complete querying, filtering, inspection, and revision tracking.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.schemas.task import Task, TaskCreate, TaskBase
from app.schemas.enums import DepartmentType, DemandStatus, CriticalityTier
from app.db.session import get_db
from app.db.models import TaskModel

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("")
async def list_tasks(
    department: Optional[DepartmentType] = Query(None, description="Filter by railway department"),
    criticality: Optional[CriticalityTier] = Query(None, description="Filter by criticality tier"),
    demand_status: Optional[DemandStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by business key or description"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Lists maintenance demands with department, criticality, and search filters.
    All displayed records and counts derive from live database queries.
    """
    query = select(TaskModel)

    if department:
        query = query.where(TaskModel.department == department)
    if criticality:
        query = query.where(TaskModel.criticality == criticality)
    if demand_status:
        query = query.where(TaskModel.demand_status == demand_status)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                TaskModel.business_key.ilike(search_pattern),
                TaskModel.description.ilike(search_pattern),
                TaskModel.track_segment_id.ilike(search_pattern),
            )
        )

    # Count total matching
    count_query = select(func.count()).select_from(query.subquery())
    count_res = await db.execute(count_query)
    total_count = count_res.scalar() or 0

    # Paginate
    query = query.order_by(TaskModel.business_key.asc()).offset(offset).limit(limit)
    res = await db.execute(query)
    db_tasks = res.scalars().all()

    # Convert to DTO
    tasks_out = []
    for t in db_tasks:
        tasks_out.append({
            "task_id": t.task_id,
            "business_key": t.business_key,
            "department": t.department.value,
            "sub_department": t.sub_department,
            "work_type": t.work_type,
            "description": t.description,
            "station_from": t.station_from,
            "station_to": t.station_to,
            "track_segment_id": t.track_segment_id,
            "chainage_start_km": t.chainage_start_km,
            "chainage_end_km": t.chainage_end_km,
            "duration_minutes": t.duration_minutes,
            "setup_buffer_minutes": t.setup_buffer_minutes,
            "restoration_buffer_minutes": t.restoration_buffer_minutes,
            "total_block_minutes": t.total_block_minutes,
            "criticality": t.criticality.value,
            "deadline_utc": t.deadline_utc.isoformat() + "Z" if t.deadline_utc else None,
            "required_resources": t.required_resources or [],
            "requires_power_block": t.requires_power_block,
            "power_block_elementary_section": t.power_block_elementary_section,
            "requires_speed_restriction_after": t.requires_speed_restriction_after,
            "imposed_speed_kmh": t.imposed_speed_kmh,
            "demand_status": t.demand_status.value,
            "provenance_mode": t.provenance_mode.value,
            "created_at_utc": t.created_at_utc.isoformat() + "Z" if t.created_at_utc else None,
            "created_by": t.created_by,
        })

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "tasks": tasks_out,
    }


@router.get("/{identifier}")
async def get_task(identifier: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves a single maintenance demand by UUID or business key.
    """
    stmt = select(TaskModel).where(
        or_(TaskModel.task_id == identifier, TaskModel.business_key == identifier)
    )
    res = await db.execute(stmt)
    t = res.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": t.task_id,
        "business_key": t.business_key,
        "department": t.department.value,
        "sub_department": t.sub_department,
        "work_type": t.work_type,
        "description": t.description,
        "station_from": t.station_from,
        "station_to": t.station_to,
        "track_segment_id": t.track_segment_id,
        "chainage_start_km": t.chainage_start_km,
        "chainage_end_km": t.chainage_end_km,
        "duration_minutes": t.duration_minutes,
        "setup_buffer_minutes": t.setup_buffer_minutes,
        "restoration_buffer_minutes": t.restoration_buffer_minutes,
        "total_block_minutes": t.total_block_minutes,
        "criticality": t.criticality.value,
        "deadline_utc": t.deadline_utc.isoformat() + "Z" if t.deadline_utc else None,
        "required_resources": t.required_resources or [],
        "requires_power_block": t.requires_power_block,
        "power_block_elementary_section": t.power_block_elementary_section,
        "requires_speed_restriction_after": t.requires_speed_restriction_after,
        "imposed_speed_kmh": t.imposed_speed_kmh,
        "demand_status": t.demand_status.value,
        "provenance_mode": t.provenance_mode.value,
        "created_at_utc": t.created_at_utc.isoformat() + "Z" if t.created_at_utc else None,
        "created_by": t.created_by,
    }


@router.put("/{identifier}")
async def update_task(
    identifier: str,
    update_data: TaskBase,
    db: AsyncSession = Depends(get_db),
):
    """
    Updates a maintenance demand. Preserves lineage and recalculates total_block_minutes.
    """
    stmt = select(TaskModel).where(
        or_(TaskModel.task_id == identifier, TaskModel.business_key == identifier)
    )
    res = await db.execute(stmt)
    task = res.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    task.department = update_data.department
    task.sub_department = update_data.sub_department
    task.work_type = update_data.work_type
    task.description = update_data.description
    task.station_from = update_data.station_from
    task.station_to = update_data.station_to
    task.track_segment_id = update_data.track_segment_id
    task.chainage_start_km = update_data.chainage_start_km
    task.chainage_end_km = update_data.chainage_end_km
    task.duration_minutes = update_data.duration_minutes
    task.setup_buffer_minutes = update_data.setup_buffer_minutes
    task.restoration_buffer_minutes = update_data.restoration_buffer_minutes
    task.total_block_minutes = (
        update_data.duration_minutes
        + update_data.setup_buffer_minutes
        + update_data.restoration_buffer_minutes
    )
    task.criticality = update_data.criticality
    task.deadline_utc = update_data.deadline_utc.replace(tzinfo=None)
    task.required_resources = [r.model_dump(mode="json") for r in update_data.required_resources]
    task.requires_power_block = update_data.requires_power_block
    task.power_block_elementary_section = update_data.power_block_elementary_section
    task.requires_speed_restriction_after = update_data.requires_speed_restriction_after
    task.imposed_speed_kmh = update_data.imposed_speed_kmh

    await db.commit()

    return {
        "status": "UPDATED",
        "task_id": task.task_id,
        "business_key": task.business_key,
        "total_block_minutes": task.total_block_minutes,
    }


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    """
    Ingest and validate an engineering maintenance demand.
    """
    new_task = Task.from_create(task_in)
    db_task = TaskModel(
        task_id=str(new_task.task_id),
        business_key=new_task.business_key,
        department=new_task.department,
        sub_department=new_task.sub_department,
        work_type=new_task.work_type,
        description=new_task.description,
        station_from=new_task.station_from,
        station_to=new_task.station_to,
        track_segment_id=new_task.track_segment_id,
        chainage_start_km=new_task.chainage_start_km,
        chainage_end_km=new_task.chainage_end_km,
        duration_minutes=new_task.duration_minutes,
        setup_buffer_minutes=new_task.setup_buffer_minutes,
        restoration_buffer_minutes=new_task.restoration_buffer_minutes,
        total_block_minutes=new_task.total_block_minutes,
        criticality=new_task.criticality,
        deadline_utc=new_task.deadline_utc.replace(tzinfo=None),
        preferred_windows=[w.model_dump(mode="json") for w in new_task.preferred_windows],
        required_resources=[r.model_dump(mode="json") for r in new_task.required_resources],
        requires_power_block=new_task.requires_power_block,
        power_block_elementary_section=new_task.power_block_elementary_section,
        requires_speed_restriction_after=new_task.requires_speed_restriction_after,
        imposed_speed_kmh=new_task.imposed_speed_kmh,
        demand_status=new_task.demand_status,
        provenance_mode=new_task.provenance_mode,
        created_at_utc=new_task.created_at_utc.replace(tzinfo=None),
        created_by=new_task.created_by,
    )
    db.add(db_task)
    await db.commit()
    return new_task
