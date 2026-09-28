"""
REST API endpoints for Executable Work Packages and Canonical Demonstration Fixtures.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.work_package import WorkPackage
from app.schemas.task import Task
from app.domain.packages import (
    build_singleton_package,
    build_bundled_package,
    generate_canonical_75min_package,
    generate_canonical_100min_package,
    generate_canonical_capacity_exceeded_triple,
)
from app.db.session import get_db
from app.db.models import TaskModel

router = APIRouter(prefix="/packages", tags=["Work Packages"])


class GeneratePackagesRequest(BaseModel):
    task_ids: List[UUID]
    allow_bundling: bool = True
    is_sequential: bool = False
    shared_capacity_limit: int = 2


@router.get("/fixtures", response_model=List[WorkPackage])
async def list_canonical_fixtures():
    """
    Returns the three canonical demonstration fixtures from Blueprint Section 18:
    1. 75-minute concurrent package (Eng 40m || S&T 25m in allowed parallel, setup 10m, test 15m, rest 10m).
    2. 100-minute sequential package (Eng 40m -> S&T 25m sequential due to shared exclusive crew).
    3. Cumulative capacity failure (3 tasks whose pairs pass, but triple exceeds capacity 2).
    """
    pkg_75 = generate_canonical_75min_package()
    pkg_100 = generate_canonical_100min_package()
    pkg_triple = generate_canonical_capacity_exceeded_triple()
    return [pkg_75, pkg_100, pkg_triple]


@router.post("/generate", response_model=List[WorkPackage])
async def generate_packages_for_tasks(
    request: GeneratePackagesRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generates singleton and bundled work packages for the requested task IDs.
    """
    id_strs = [str(t) for t in request.task_ids]
    result = await db.execute(select(TaskModel).where(TaskModel.task_id.in_(id_strs)))
    rows = result.scalars().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No matching tasks found for provided IDs")

    tasks: List[Task] = []
    for r in rows:
        tasks.append(Task(
            task_id=UUID(r.task_id),
            business_key=r.business_key,
            department=r.department,
            sub_department=r.sub_department,
            work_type=r.work_type,
            description=r.description,
            station_from=r.station_from,
            station_to=r.station_to,
            track_segment_id=r.track_segment_id,
            chainage_start_km=r.chainage_start_km,
            chainage_end_km=r.chainage_end_km,
            duration_minutes=r.duration_minutes,
            setup_buffer_minutes=r.setup_buffer_minutes,
            restoration_buffer_minutes=r.restoration_buffer_minutes,
            total_block_minutes=r.total_block_minutes,
            criticality=r.criticality,
            deadline_utc=r.deadline_utc,
            requires_power_block=r.requires_power_block,
            power_block_elementary_section=r.power_block_elementary_section,
            requires_speed_restriction_after=r.requires_speed_restriction_after,
            imposed_speed_kmh=r.imposed_speed_kmh,
            provenance_mode=r.provenance_mode,
            demand_status=r.demand_status,
            created_at_utc=r.created_at_utc,
            created_by=r.created_by,
        ))

    packages: List[WorkPackage] = []

    # 1. Always generate singletons
    for t in tasks:
        packages.append(build_singleton_package(t))

    # 2. If bundling requested and multiple tasks provided, generate candidate bundles
    if request.allow_bundling and len(tasks) > 1:
        # Group tasks by track segment
        from collections import defaultdict
        by_segment = defaultdict(list)
        for t in tasks:
            by_segment[t.track_segment_id].append(t)

        for seg_id, seg_tasks in by_segment.items():
            if len(seg_tasks) >= 2:
                # Generate pairwise bundles
                for i in range(len(seg_tasks)):
                    for j in range(i + 1, len(seg_tasks)):
                        pair_pkg = build_bundled_package(
                            tasks=[seg_tasks[i], seg_tasks[j]],
                            is_sequential=request.is_sequential,
                            shared_capacity_limit=request.shared_capacity_limit,
                        )
                        packages.append(pair_pkg)

    return packages
