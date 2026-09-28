"""
Gateway Service for Corridor Seeding, Task Import / Revision, and Snapshot Sealing.
"""
from typing import List, Dict, Any, Optional
import os
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.models import (
    CorridorModel,
    StationModel,
    TrackSegmentModel,
    TaskModel,
    ResourceCalendarModel,
    SnapshotModel,
    SnapshotTaskMembership,
)
from app.schemas.enums import (
    DepartmentType,
    CriticalityTier,
    DemandStatus,
    ProvenanceMode,
    TrackDirection,
)
from app.schemas.task import Task, TaskCreate
from app.schemas.snapshot import Snapshot, TrainOccupation, ResourceCalendarEntry
from app.gateway.normalizer import ingest_csv_content, ingest_json_records, IngestionResult
from app.gateway.quarantine_store import record_quarantine_batch
from app.core.logging import logger

SEED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "seed_data")


async def seed_vayu_kosh_corridor(db: AsyncSession) -> Dict[str, Any]:
    """
    Deterministically seeds the Vayu-Kosh Corridor (VKC):
    - 1 Corridor, 6 Stations, 10 Track Segments
    - 60 Monthly Tasks
    - 11 Resource Calendars
    Idempotent: clears prior VKC corridor data before reseeding.
    """
    topology_path = os.path.join(SEED_DIR, "corridor_topology.json")
    tasks_path = os.path.join(SEED_DIR, "demands_monthly_60.json")
    calendars_path = os.path.join(SEED_DIR, "resource_calendars.json")

    with open(topology_path, "r") as f:
        topology = json.load(f)
    with open(tasks_path, "r") as f:
        tasks_data = json.load(f)
    with open(calendars_path, "r") as f:
        calendars_data = json.load(f)

    # Clean existing VKC tasks and corridor
    await db.execute(delete(TaskModel).where(TaskModel.track_segment_id.like("SEC-%")))
    await db.execute(delete(ResourceCalendarModel).where(ResourceCalendarModel.corridor_code == "VKC"))
    await db.execute(delete(TrackSegmentModel).where(TrackSegmentModel.corridor_code == "VKC"))
    await db.execute(delete(StationModel).where(StationModel.corridor_code == "VKC"))
    await db.execute(delete(CorridorModel).where(CorridorModel.corridor_code == "VKC"))
    await db.commit()

    # 1. Create Corridor
    corridor = CorridorModel(
        corridor_code=topology["corridor_code"],
        corridor_name=topology["corridor_name"],
        total_length_km=topology["total_length_km"],
    )
    db.add(corridor)
    await db.flush()

    # 2. Create Stations
    for st in topology["stations"]:
        db.add(StationModel(
            station_code=st["station_code"],
            corridor_code="VKC",
            station_name=st["station_name"],
            chainage_km=st["chainage_km"],
            absolute_distance_meters=st["absolute_distance_meters"],
            total_lines=st["total_lines"],
            has_crossover=st["has_crossover"],
        ))
    await db.flush()

    # 3. Create Track Segments
    for seg in topology["track_segments"]:
        db.add(TrackSegmentModel(
            segment_id=seg["segment_id"],
            corridor_code="VKC",
            station_from=seg["station_from"],
            station_to=seg["station_to"],
            direction=TrackDirection(seg["direction"]),
            chainage_start_km=seg["chainage_start_km"],
            chainage_end_km=seg["chainage_end_km"],
            length_meters=seg["length_meters"],
            max_permissible_speed_kmh=seg["max_permissible_speed_kmh"],
            elementary_section_id=seg["elementary_section_id"],
        ))
    await db.flush()

    # 4. Create 60 Monthly Tasks
    ingestion_res = ingest_json_records(tasks_data)
    seeded_tasks_count = 0
    for create_dto in ingestion_res.accepted_tasks:
        total_block = create_dto.duration_minutes + create_dto.setup_buffer_minutes + create_dto.restoration_buffer_minutes
        db_task = TaskModel(
            task_id=str(uuid.uuid4()),
            business_key=create_dto.business_key,
            department=create_dto.department,
            sub_department=create_dto.sub_department,
            work_type=create_dto.work_type,
            description=create_dto.description,
            station_from=create_dto.station_from,
            station_to=create_dto.station_to,
            track_segment_id=create_dto.track_segment_id,
            chainage_start_km=create_dto.chainage_start_km,
            chainage_end_km=create_dto.chainage_end_km,
            duration_minutes=create_dto.duration_minutes,
            setup_buffer_minutes=create_dto.setup_buffer_minutes,
            restoration_buffer_minutes=create_dto.restoration_buffer_minutes,
            total_block_minutes=total_block,
            criticality=create_dto.criticality,
            deadline_utc=create_dto.deadline_utc.replace(tzinfo=None),
            preferred_windows=[w.model_dump(mode="json") for w in create_dto.preferred_windows],
            required_resources=[r.model_dump(mode="json") for r in create_dto.required_resources],
            requires_power_block=create_dto.requires_power_block,
            power_block_elementary_section=create_dto.power_block_elementary_section,
            requires_speed_restriction_after=create_dto.requires_speed_restriction_after,
            imposed_speed_kmh=create_dto.imposed_speed_kmh,
            demand_status=DemandStatus.VALIDATED,
            provenance_mode=create_dto.provenance_mode,
            created_by="system-seed",
        )
        db.add(db_task)
        seeded_tasks_count += 1
    await db.flush()

    # 5. Create Resource Calendars
    for cal in calendars_data:
        db.add(ResourceCalendarModel(
            calendar_id=cal["calendar_id"],
            resource_id=cal["resource_id"],
            resource_type=cal["resource_type"],
            corridor_code=cal["corridor_code"],
            available_start_utc=datetime.fromisoformat(cal["available_start_utc"].replace("Z", "+00:00")).replace(tzinfo=None),
            available_end_utc=datetime.fromisoformat(cal["available_end_utc"].replace("Z", "+00:00")).replace(tzinfo=None),
            is_outage=cal["is_outage"],
            outage_reason=cal.get("outage_reason"),
        ))

    await db.commit()

    return {
        "status": "SUCCESS",
        "corridor_code": "VKC",
        "stations_count": len(topology["stations"]),
        "track_segments_count": len(topology["track_segments"]),
        "tasks_seeded": seeded_tasks_count,
        "resource_calendars_count": len(calendars_data),
        "quarantined_count": ingestion_res.quarantine_count,
        "provenance_mode": "TEST",
    }


async def import_tasks_payload(
    db: AsyncSession,
    content: str,
    format_type: str = "json",
    dry_run: bool = False,
    user_id: str = "planner",
) -> Dict[str, Any]:
    """
    Imports tasks from CSV or JSON with validation, quarantine isolation, and revision tracking.
    """
    if format_type.lower() == "csv":
        ingestion_result = ingest_csv_content(content)
    else:
        try:
            records = json.loads(content)
            if not isinstance(records, list):
                records = [records]
        except Exception as ex:
            # Entire JSON malformed
            quarantine_batch = record_quarantine_batch([{
                "row_index": 0,
                "business_key": "PAYLOAD_PARSE_ERROR",
                "raw_data": {"content": content[:200]},
                "error_type": "JSONDecodeError",
                "error_detail": str(ex),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }])
            return {
                "dry_run": dry_run,
                "total_rows": 0,
                "accepted_count": 0,
                "quarantined_count": 1,
                "quarantined_items": quarantine_batch,
                "accepted_tasks": [],
            }
        ingestion_result = ingest_json_records(records)

    # Save quarantined records to global quarantine store
    quarantined_stamped = []
    if ingestion_result.quarantined_rows:
        quarantined_stamped = record_quarantine_batch(ingestion_result.quarantined_rows)

    accepted_responses = []

    if not dry_run and ingestion_result.accepted_tasks:
        for create_dto in ingestion_result.accepted_tasks:
            # Check if task with business_key already exists
            stmt = select(TaskModel).where(TaskModel.business_key == create_dto.business_key)
            result = await db.execute(stmt)
            existing_task = result.scalars().first()

            total_block = create_dto.duration_minutes + create_dto.setup_buffer_minutes + create_dto.restoration_buffer_minutes

            if existing_task:
                # Update existing task (idempotent / revision update)
                existing_task.department = create_dto.department
                existing_task.sub_department = create_dto.sub_department
                existing_task.work_type = create_dto.work_type
                existing_task.description = create_dto.description
                existing_task.station_from = create_dto.station_from
                existing_task.station_to = create_dto.station_to
                existing_task.track_segment_id = create_dto.track_segment_id
                existing_task.chainage_start_km = create_dto.chainage_start_km
                existing_task.chainage_end_km = create_dto.chainage_end_km
                existing_task.duration_minutes = create_dto.duration_minutes
                existing_task.setup_buffer_minutes = create_dto.setup_buffer_minutes
                existing_task.restoration_buffer_minutes = create_dto.restoration_buffer_minutes
                existing_task.total_block_minutes = total_block
                existing_task.criticality = create_dto.criticality
                existing_task.deadline_utc = create_dto.deadline_utc.replace(tzinfo=None)
                existing_task.preferred_windows = [w.model_dump(mode="json") for w in create_dto.preferred_windows]
                existing_task.required_resources = [r.model_dump(mode="json") for r in create_dto.required_resources]
                existing_task.requires_power_block = create_dto.requires_power_block
                existing_task.power_block_elementary_section = create_dto.power_block_elementary_section
                existing_task.requires_speed_restriction_after = create_dto.requires_speed_restriction_after
                existing_task.imposed_speed_kmh = create_dto.imposed_speed_kmh
                accepted_responses.append({"business_key": create_dto.business_key, "action": "UPDATED_REVISION"})
            else:
                # Create brand new task
                db_task = TaskModel(
                    task_id=str(uuid.uuid4()),
                    business_key=create_dto.business_key,
                    department=create_dto.department,
                    sub_department=create_dto.sub_department,
                    work_type=create_dto.work_type,
                    description=create_dto.description,
                    station_from=create_dto.station_from,
                    station_to=create_dto.station_to,
                    track_segment_id=create_dto.track_segment_id,
                    chainage_start_km=create_dto.chainage_start_km,
                    chainage_end_km=create_dto.chainage_end_km,
                    duration_minutes=create_dto.duration_minutes,
                    setup_buffer_minutes=create_dto.setup_buffer_minutes,
                    restoration_buffer_minutes=create_dto.restoration_buffer_minutes,
                    total_block_minutes=total_block,
                    criticality=create_dto.criticality,
                    deadline_utc=create_dto.deadline_utc.replace(tzinfo=None),
                    preferred_windows=[w.model_dump(mode="json") for w in create_dto.preferred_windows],
                    required_resources=[r.model_dump(mode="json") for r in create_dto.required_resources],
                    requires_power_block=create_dto.requires_power_block,
                    power_block_elementary_section=create_dto.power_block_elementary_section,
                    requires_speed_restriction_after=create_dto.requires_speed_restriction_after,
                    imposed_speed_kmh=create_dto.imposed_speed_kmh,
                    demand_status=DemandStatus.VALIDATED,
                    provenance_mode=create_dto.provenance_mode,
                    created_by=user_id,
                )
                db.add(db_task)
                accepted_responses.append({"business_key": create_dto.business_key, "action": "CREATED"})

        await db.commit()
    else:
        for t in ingestion_result.accepted_tasks:
            accepted_responses.append({"business_key": t.business_key, "action": "DRY_RUN_VALID"})

    return {
        "dry_run": dry_run,
        "total_rows": ingestion_result.total_rows,
        "accepted_count": ingestion_result.success_count,
        "quarantined_count": ingestion_result.quarantine_count,
        "quarantined_items": quarantined_stamped,
        "results": accepted_responses,
    }


async def seal_snapshot_from_db(
    db: AsyncSession,
    corridor_code: str = "VKC",
    horizon_start: Optional[datetime] = None,
    horizon_end: Optional[datetime] = None,
    user_id: str = "system",
) -> Snapshot:
    """
    Creates an immutable, sealed Snapshot container with canonical SHA-256 hash.
    Pulls tasks, resource calendars, and train occupations from the database/seed.
    """
    if horizon_start is None:
        horizon_start = datetime(2026, 10, 12, 0, 0, 0, tzinfo=timezone.utc)
    if horizon_end is None:
        horizon_end = datetime(2026, 10, 18, 23, 59, 59, tzinfo=timezone.utc)

    # 1. Query active tasks
    stmt = select(TaskModel).where(TaskModel.track_segment_id.like("SEC-%"))
    res = await db.execute(stmt)
    db_tasks = res.scalars().all()

    tasks_dto: List[Task] = []
    for t in db_tasks:
        tasks_dto.append(
            Task(
                task_id=uuid.UUID(t.task_id),
                business_key=t.business_key,
                department=t.department,
                sub_department=t.sub_department,
                work_type=t.work_type,
                description=t.description,
                station_from=t.station_from,
                station_to=t.station_to,
                track_segment_id=t.track_segment_id,
                chainage_start_km=t.chainage_start_km,
                chainage_end_km=t.chainage_end_km,
                duration_minutes=t.duration_minutes,
                setup_buffer_minutes=t.setup_buffer_minutes,
                restoration_buffer_minutes=t.restoration_buffer_minutes,
                total_block_minutes=t.total_block_minutes,
                criticality=t.criticality,
                deadline_utc=horizon_end if t.deadline_utc.replace(tzinfo=timezone.utc) < horizon_start else t.deadline_utc.replace(tzinfo=timezone.utc),
                preferred_windows=[],
                required_resources=[],
                requires_power_block=t.requires_power_block,
                power_block_elementary_section=t.power_block_elementary_section,
                requires_speed_restriction_after=t.requires_speed_restriction_after,
                imposed_speed_kmh=t.imposed_speed_kmh,
                demand_status=t.demand_status,
                provenance_mode=t.provenance_mode,
                created_at_utc=t.created_at_utc.replace(tzinfo=timezone.utc),
                created_by=t.created_by,
            )
        )

    # 2. Resource Calendars
    cal_stmt = select(ResourceCalendarModel).where(ResourceCalendarModel.corridor_code == corridor_code)
    cal_res = await db.execute(cal_stmt)
    db_cals = cal_res.scalars().all()
    cals_dto: List[ResourceCalendarEntry] = [
        ResourceCalendarEntry(
            entry_id=c.calendar_id,
            resource_id=c.resource_id,
            resource_type=c.resource_type,
            available_start_utc=c.available_start_utc.replace(tzinfo=timezone.utc),
            available_end_utc=c.available_end_utc.replace(tzinfo=timezone.utc),
            is_outage=c.is_outage,
            outage_reason=c.outage_reason,
        )
        for c in db_cals
    ]

    # 3. Train Occupations (from train_timetable.json)
    train_path = os.path.join(SEED_DIR, "train_timetable.json")
    trains_dto: List[TrainOccupation] = []
    if os.path.exists(train_path):
        with open(train_path, "r") as f:
            train_data = json.load(f)
            for tr in train_data:
                trains_dto.append(
                    TrainOccupation(
                        occupation_id=tr["occupation_id"],
                        train_number=tr["train_number"],
                        train_type=tr["train_type"],
                        track_segment_id=tr["track_segment_id"],
                        entry_time_utc=datetime.fromisoformat(tr["entry_time_utc"]),
                        exit_time_utc=datetime.fromisoformat(tr["exit_time_utc"]),
                        start_minute=tr["start_minute"],
                        end_minute=tr["end_minute"],
                    )
                )

    snapshot_id = uuid.uuid4()
    snapshot = Snapshot(
        snapshot_id=snapshot_id,
        corridor_code=corridor_code,
        horizon_start_utc=horizon_start,
        horizon_end_utc=horizon_end,
        provenance_mode=ProvenanceMode.TEST,
        tasks=tasks_dto,
        train_occupations=trains_dto,
        resource_calendars=cals_dto,
        locked_commitments=[],
        is_sealed=True,
        created_by=user_id,
    )
    # Compute deterministic canonical hash
    canonical_hash = snapshot.compute_canonical_hash()
    snapshot.snapshot_hash = canonical_hash

    # Check if a snapshot with this exact canonical hash already exists (idempotent seal)
    existing_stmt = select(SnapshotModel).where(SnapshotModel.snapshot_hash == canonical_hash)
    existing_res = await db.execute(existing_stmt)
    existing_snap = existing_res.scalars().first()
    if existing_snap:
        snapshot.snapshot_id = uuid.UUID(existing_snap.snapshot_id)
        snapshot.created_at_utc = existing_snap.created_at_utc.replace(tzinfo=timezone.utc)
        return snapshot

    # Persist snapshot metadata to DB
    db_snapshot = SnapshotModel(
        snapshot_id=str(snapshot_id),
        snapshot_hash=canonical_hash,
        corridor_code=corridor_code,
        horizon_start_utc=horizon_start.replace(tzinfo=None),
        horizon_end_utc=horizon_end.replace(tzinfo=None),
        provenance_mode=ProvenanceMode.TEST,
        is_sealed=True,
        created_by=user_id,
    )
    db.add(db_snapshot)
    await db.flush()

    for t in tasks_dto:
        db.add(SnapshotTaskMembership(
            snapshot_id=str(snapshot_id),
            task_id=str(t.task_id),
        ))

    await db.commit()
    return snapshot


def get_hand_checkable_fixtures() -> Dict[str, Any]:
    fixtures_path = os.path.join(SEED_DIR, "hand_checkable_fixtures.json")
    if os.path.exists(fixtures_path):
        with open(fixtures_path, "r") as f:
            data = json.load(f)
            # Add provenance badges and canonical scenario hashes
            import hashlib
            enriched = {}
            for name, fixture in data.items():
                fixture_hash = hashlib.sha256(json.dumps(fixture, sort_keys=True).encode("utf-8")).hexdigest()[:12]
                enriched[name] = {
                    **fixture,
                    "fixture_hash": f"FIX-{fixture_hash}",
                    "provenance_mode": "TEST_FIXTURE",
                    "provenance_badge": "[SYNTHETIC_SCENARIO]",
                }
            return enriched
    return {}
