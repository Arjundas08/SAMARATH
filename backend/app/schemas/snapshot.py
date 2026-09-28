"""
Immutable Snapshot schemas and deterministic canonical serialization.
"""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field

from app.schemas.common import APIModel, utc_now
from app.schemas.enums import ProvenanceMode
from app.schemas.task import Task


class TrainOccupation(APIModel):
    occupation_id: str
    train_number: str
    train_type: str  # "PASSENGER", "EXPRESS", "FREIGHT"
    track_segment_id: str
    entry_time_utc: datetime
    exit_time_utc: datetime
    start_minute: int  # Relative to horizon epoch
    end_minute: int


class ResourceCalendarEntry(APIModel):
    entry_id: str
    resource_id: str
    resource_type: str
    available_start_utc: datetime
    available_end_utc: datetime
    is_outage: bool = False
    outage_reason: Optional[str] = None


class LockedCommitment(APIModel):
    commitment_id: str
    task_id: UUID
    track_segment_id: str
    start_utc: datetime
    end_utc: datetime
    locked_by: str
    lock_reason: str


class Snapshot(APIModel):
    snapshot_id: UUID = Field(default_factory=uuid4)
    corridor_code: str = "VKC"
    horizon_start_utc: datetime
    horizon_end_utc: datetime
    provenance_mode: ProvenanceMode = ProvenanceMode.TEST
    tasks: List[Task] = Field(default_factory=list)
    train_occupations: List[TrainOccupation] = Field(default_factory=list)
    resource_calendars: List[ResourceCalendarEntry] = Field(default_factory=list)
    locked_commitments: List[LockedCommitment] = Field(default_factory=list)
    snapshot_hash: str = ""
    is_sealed: bool = True
    created_at_utc: datetime = Field(default_factory=utc_now)
    created_by: str = "system"

    def compute_canonical_hash(self) -> str:
        """
        Computes SHA-256 digest over deterministically ordered entities.
        Prevents unordered JSON dictionary mutation or timing variances.
        """
        import hashlib
        import json

        # Sort tasks by business_key
        sorted_tasks = sorted(
            [
                {
                    "business_key": t.business_key,
                    "dept": t.department.value,
                    "seg": t.track_segment_id,
                    "duration": t.duration_minutes,
                    "total_block": t.total_block_minutes,
                    "criticality": t.criticality.value,
                    "deadline": t.deadline_utc.isoformat(),
                    "power": t.requires_power_block,
                }
                for t in self.tasks
            ],
            key=lambda x: x["business_key"],
        )

        # Sort train occupations by entry time and train number
        sorted_trains = sorted(
            [
                {
                    "train": tr.train_number,
                    "seg": tr.track_segment_id,
                    "entry": tr.entry_time_utc.isoformat(),
                    "exit": tr.exit_time_utc.isoformat(),
                }
                for tr in self.train_occupations
            ],
            key=lambda x: (x["entry"], x["train"]),
        )

        # Sort resource calendars
        sorted_resources = sorted(
            [
                {
                    "res_id": rc.resource_id,
                    "start": rc.available_start_utc.isoformat(),
                    "end": rc.available_end_utc.isoformat(),
                    "outage": rc.is_outage,
                }
                for rc in self.resource_calendars
            ],
            key=lambda x: (x["res_id"], x["start"]),
        )

        # Sort locked commitments
        sorted_locks = sorted(
            [
                {
                    "task_id": str(lc.task_id),
                    "seg": lc.track_segment_id,
                    "start": lc.start_utc.isoformat(),
                    "end": lc.end_utc.isoformat(),
                }
                for lc in self.locked_commitments
            ],
            key=lambda x: (x["start"], x["task_id"]),
        )

        canonical_dict = {
            "corridor": self.corridor_code,
            "horizon_start": self.horizon_start_utc.isoformat(),
            "horizon_end": self.horizon_end_utc.isoformat(),
            "mode": self.provenance_mode.value,
            "tasks": sorted_tasks,
            "trains": sorted_trains,
            "resources": sorted_resources,
            "locks": sorted_locks,
        }

        canonical_json = json.dumps(canonical_dict, sort_keys=True, separators=(",", ":"))
        return f"sha256:{hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()}"
