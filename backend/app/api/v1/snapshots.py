"""
Snapshot creation and hash verification endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.snapshot import Snapshot
from app.db.session import get_db

router = APIRouter(prefix="/snapshots", tags=["Snapshots"])


@router.post("", response_model=Snapshot, status_code=status.HTTP_201_CREATED)
async def create_snapshot(snapshot_in: Snapshot, db: AsyncSession = Depends(get_db)):
    """
    Creates and seals an immutable Snapshot container.
    Computes deterministic SHA-256 hash over canonical ordered entities.
    """
    snapshot_hash = snapshot_in.compute_canonical_hash()
    snapshot_in.snapshot_hash = snapshot_hash
    snapshot_in.is_sealed = True
    return snapshot_in


@router.post("/verify-hash")
async def verify_snapshot_hash(snapshot_in: Snapshot):
    """
    Verifies that the snapshot hash exactly matches the canonical computed digest.
    """
    computed_hash = snapshot_in.compute_canonical_hash()
    is_valid = (snapshot_in.snapshot_hash == computed_hash)
    return {
        "provided_hash": snapshot_in.snapshot_hash,
        "computed_hash": computed_hash,
        "is_valid": is_valid,
    }
