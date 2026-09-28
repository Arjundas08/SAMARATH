"""
Gateway API Endpoints for Corridor Ingestion, Quarantine Management, Fixtures, and Snapshot Sealing.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models import SnapshotModel, SnapshotTaskMembership
from app.schemas.snapshot import Snapshot
from app.schemas.common import ProblemDetails, utc_now
from app.gateway.service import (
    seed_vayu_kosh_corridor,
    import_tasks_payload,
    seal_snapshot_from_db,
    get_hand_checkable_fixtures,
)
from app.gateway.quarantine_store import (
    get_quarantined_records,
    get_quarantined_by_id,
    remove_quarantined_record,
    clear_quarantine,
)

router = APIRouter(prefix="/gateway", tags=["Input Gateway"])


@router.post("/seed/corridor", status_code=status.HTTP_201_CREATED)
async def seed_corridor_endpoint(db: AsyncSession = Depends(get_db)):
    """
    Seeds the 120km Vayu-Kosh Corridor (VKC) with 6 stations, 10 track segments,
    60 monthly tasks, resource calendars, and timetables.
    """
    res = await seed_vayu_kosh_corridor(db)
    return res


@router.post("/import")
async def import_data_endpoint(
    request: Request,
    dry_run: bool = Query(default=False, description="Simulate import without committing to database"),
    format_type: str = Query(default="json", description="'json' or 'csv'"),
    content_type: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingests maintenance demands via JSON or CSV with formula sanitization,
    row-level quarantine isolation, and revision tracking.
    Explicitly rejects XLSX/macro spreadsheets with 415 Unsupported Media Type.
    """
    # Check for forbidden spreadsheet types
    if content_type and any(x in content_type.lower() for x in ["spreadsheet", "excel", "vnd.ms-excel", "openxmlformats"]):
        problem = ProblemDetails(
            type="https://samarath.railnet.gov.in/errors/unsupported-media-type",
            title="Unsupported File Format",
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="XLSX and Excel formats are explicitly unsupported in this release to prevent macro security vulnerabilities and unvalidated spreadsheet formula injection. Please export to UTF-8 CSV or JSON.",
            instance=str(request.url.path),
            error_code="ERR_XLSX_UNSUPPORTED",
            timestamp=datetime.now(timezone.utc),
        )
        return JSONResponse(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            content=problem.model_dump(mode="json"),
            headers={"Content-Type": "application/problem+json"},
        )

    body_bytes = await request.body()
    body_text = body_bytes.decode("utf-8", errors="replace")

    if not body_text.strip():
        problem = ProblemDetails(
            type="https://samarath.railnet.gov.in/errors/empty-payload",
            title="Empty Request Payload",
            status=status.HTTP_400_BAD_REQUEST,
            detail="The import payload was empty.",
            instance=str(request.url.path),
            error_code="ERR_EMPTY_PAYLOAD",
            timestamp=datetime.now(timezone.utc),
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=problem.model_dump(mode="json"),
            headers={"Content-Type": "application/problem+json"},
        )

    # Auto-detect format if body starts with CSV-like header or JSON bracket
    detected_format = format_type
    trimmed = body_text.strip()
    if trimmed.startswith("[") or trimmed.startswith("{"):
        detected_format = "json"
    elif "business_key" in trimmed[:100] and "," in trimmed[:100]:
        detected_format = "csv"

    res = await import_tasks_payload(
        db=db,
        content=body_text,
        format_type=detected_format,
        dry_run=dry_run,
        user_id="gateway_importer",
    )
    return res


@router.get("/quarantine")
async def list_quarantine(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Returns malformed or invalid records captured by the input normalizer.
    """
    items, total = get_quarantined_records(limit=limit, offset=offset)
    return {
        "total_quarantined": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


@router.get("/quarantine/{quarantine_id}")
async def get_quarantine_item(quarantine_id: str):
    """
    Retrieves a single quarantined record with detailed field errors.
    """
    item = get_quarantined_by_id(quarantine_id)
    if not item:
        raise HTTPException(status_code=404, detail="Quarantine record not found")
    return item


@router.delete("/quarantine/{quarantine_id}")
async def dismiss_quarantine_item(quarantine_id: str):
    """
    Dismisses a quarantined item after correction or acknowledgement.
    """
    removed = remove_quarantined_record(quarantine_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Quarantine record not found")
    return {"status": "DISMISSED", "quarantine_id": quarantine_id}


@router.post("/quarantine/clear")
async def clear_all_quarantine():
    """
    Clears all quarantined records.
    """
    clear_quarantine()
    return {"status": "CLEARED"}


@router.get("/fixtures")
async def get_fixtures_endpoint():
    """
    Returns the 8 hand-checkable test fixtures with assumptions, units,
    expected verdicts, and deterministic fixture hashes.
    """
    fixtures = get_hand_checkable_fixtures()
    return {
        "corridor_code": "VKC",
        "provenance_mode": "TEST_FIXTURE",
        "fixtures_count": len(fixtures),
        "fixtures": fixtures,
    }


@router.post("/snapshots/seal", response_model=Snapshot, status_code=status.HTTP_201_CREATED)
async def seal_snapshot_endpoint(
    corridor_code: str = Query(default="VKC"),
    db: AsyncSession = Depends(get_db),
):
    """
    Freezes and seals an immutable Snapshot from current database state.
    Calculates deterministic canonical SHA-256 hash across sorted entities.
    """
    snapshot = await seal_snapshot_from_db(db=db, corridor_code=corridor_code)
    return snapshot


@router.get("/snapshots")
async def list_snapshots(db: AsyncSession = Depends(get_db)):
    """
    Lists sealed immutable snapshots in database.
    """
    stmt = select(SnapshotModel).order_by(SnapshotModel.created_at_utc.desc())
    res = await db.execute(stmt)
    snapshots = res.scalars().all()
    out = []
    for s in snapshots:
        # Get count of tasks in snapshot
        count_stmt = select(func.count()).select_from(SnapshotTaskMembership).where(SnapshotTaskMembership.snapshot_id == s.snapshot_id)
        count_res = await db.execute(count_stmt)
        task_count = count_res.scalar() or 0
        out.append({
            "snapshot_id": s.snapshot_id,
            "snapshot_hash": s.snapshot_hash,
            "corridor_code": s.corridor_code,
            "horizon_start_utc": s.horizon_start_utc.isoformat(),
            "horizon_end_utc": s.horizon_end_utc.isoformat(),
            "provenance_mode": s.provenance_mode.value,
            "is_sealed": s.is_sealed,
            "created_at_utc": s.created_at_utc.isoformat(),
            "created_by": s.created_by,
            "task_count": task_count,
        })
    return {"snapshots": out}


@router.post("/external/sync", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def external_sync_endpoint(request: Request):
    """
    Truthful implementation: external Railway authority integration (CRIS/COIS/ICMS)
    requires official certified credentials and is NOT_CONFIGURED in this test environment.
    Never returns fake success or fabricated operational sync data.
    """
    problem = ProblemDetails(
        type="https://samarath.railnet.gov.in/errors/not-configured",
        title="External Railway Authority Sync Not Configured",
        status=status.HTTP_501_NOT_IMPLEMENTED,
        detail="External Railway authority integration (CRIS/COIS/ICMS) requires official Ministry of Railways production certificates and secure intranet VPN connectivity. No external credentials are configured in this test environment. Use authorized CSV/JSON gateway imports.",
        instance=str(request.url.path),
        error_code="ERR_EXTERNAL_SYNC_NOT_CONFIGURED",
        timestamp=datetime.now(timezone.utc),
    )
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content=problem.model_dump(mode="json"),
        headers={"Content-Type": "application/problem+json"},
    )
