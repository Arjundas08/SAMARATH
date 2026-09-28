"""
Quarantine Store for malformed or rejected records.
Holds records failing schema validation with RFC 7807 problem details.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import uuid

# In-memory quarantine store (can be synced to DB table in future migrations)
_QUARANTINE_RECORDS: List[Dict[str, Any]] = []


def record_quarantine_batch(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    global _QUARANTINE_RECORDS
    stamped_errors = []
    for err in errors:
        item = dict(err)
        if "quarantine_id" not in item:
            item["quarantine_id"] = str(uuid.uuid4())
        if "timestamp_utc" not in item:
            item["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        stamped_errors.append(item)
    _QUARANTINE_RECORDS.extend(stamped_errors)
    return stamped_errors


def get_quarantined_records(limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    global _QUARANTINE_RECORDS
    total = len(_QUARANTINE_RECORDS)
    items = _QUARANTINE_RECORDS[offset : offset + limit]
    return items, total


def get_quarantined_by_id(quarantine_id: str) -> Optional[Dict[str, Any]]:
    global _QUARANTINE_RECORDS
    for item in _QUARANTINE_RECORDS:
        if item.get("quarantine_id") == quarantine_id:
            return item
    return None


def remove_quarantined_record(quarantine_id: str) -> bool:
    global _QUARANTINE_RECORDS
    initial_len = len(_QUARANTINE_RECORDS)
    _QUARANTINE_RECORDS = [item for item in _QUARANTINE_RECORDS if item.get("quarantine_id") != quarantine_id]
    return len(_QUARANTINE_RECORDS) < initial_len


def clear_quarantine():
    global _QUARANTINE_RECORDS
    _QUARANTINE_RECORDS.clear()
