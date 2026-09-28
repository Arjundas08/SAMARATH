"""
Input Gateway Normalizer and Schema Validation.
Transforms raw CSV/JSON records into typed Task models with quarantine isolation and formula safety.
"""
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
import csv
import io
import re
from pydantic import ValidationError

from app.schemas.task import TaskCreate, ResourceRequirement, PreferredWindow
from app.schemas.enums import DepartmentType, CriticalityTier, ProvenanceMode, ResourceType


class IngestionResult:
    def __init__(self):
        self.accepted_tasks: List[TaskCreate] = []
        self.quarantined_rows: List[Dict[str, Any]] = []
        self.total_rows: int = 0

    @property
    def success_count(self) -> int:
        return len(self.accepted_tasks)

    @property
    def quarantine_count(self) -> int:
        return len(self.quarantined_rows)


def sanitize_formula_injection(val: Any) -> Any:
    """
    Prevents CSV / Formula Injection attacks.
    If a string starts with =, +, -, @, \t, or \r, strip or prefix to neutralize spreadsheet execution.
    """
    if isinstance(val, str) and len(val) > 0:
        first_char = val[0]
        if first_char in ("=", "@", "\t", "\r"):
            return "'" + val
        # For + or -, only neutralize if followed by alphabetic formula character (like +SUM)
        if first_char in ("+", "-") and len(val) > 1 and val[1].isalpha():
            return "'" + val
    return val


def parse_datetime(val: str) -> datetime:
    val = val.strip()
    if val.endswith("Z"):
        val = val[:-1] + "+00:00"
    return datetime.fromisoformat(val)


def normalize_record(raw: Dict[str, Any], row_index: int) -> Tuple[Optional[TaskCreate], Optional[Dict[str, Any]]]:
    """
    Normalizes a single raw dictionary record.
    Returns (TaskCreate, None) on success or (None, QuarantineDict) on failure.
    Captures RFC 7807 structured field error information.
    """
    # Sanitize all string fields against formula injection
    sanitized_raw = {k: sanitize_formula_injection(v) for k, v in raw.items()}
    business_key = str(sanitized_raw.get("business_key", f"ROW-{row_index}")).strip()

    field_errors = []

    # 1. Parse Required Resources
    resources_raw = sanitized_raw.get("required_resources", [])
    parsed_resources: List[ResourceRequirement] = []
    if isinstance(resources_raw, list):
        for r_idx, r in enumerate(resources_raw):
            if isinstance(r, dict):
                try:
                    parsed_resources.append(ResourceRequirement(**r))
                except ValidationError as ve:
                    field_errors.append({"field": f"required_resources[{r_idx}]", "error": str(ve)})
            elif isinstance(r, str):
                tokens = r.split(":")
                try:
                    rtype = ResourceType(tokens[0].strip().upper())
                    rid = tokens[1].strip() if len(tokens) > 1 else "UNKNOWN"
                    qty = int(tokens[2].strip()) if len(tokens) > 2 else 1
                    parsed_resources.append(ResourceRequirement(resource_type=rtype, resource_id=rid, quantity=qty))
                except Exception as ex:
                    field_errors.append({"field": f"required_resources[{r_idx}]", "error": f"Invalid format '{r}': {ex}"})
    elif isinstance(resources_raw, str) and resources_raw.strip():
        # CSV string format: MACHINE:BCM-01:1,CREW:GANG-PWAY-01:1
        parts = [p.strip() for p in resources_raw.split(",") if p.strip()]
        for p in parts:
            tokens = p.split(":")
            try:
                rtype = ResourceType(tokens[0].strip().upper())
                rid = tokens[1].strip() if len(tokens) > 1 else "UNKNOWN"
                qty = int(tokens[2].strip()) if len(tokens) > 2 else 1
                parsed_resources.append(ResourceRequirement(resource_type=rtype, resource_id=rid, quantity=qty))
            except Exception as ex:
                field_errors.append({"field": "required_resources", "error": f"Failed parsing '{p}': {ex}"})

    # 2. Parse Deadline
    deadline_val = sanitized_raw.get("deadline_utc")
    parsed_deadline = None
    if not deadline_val:
        field_errors.append({"field": "deadline_utc", "error": "Missing mandatory field 'deadline_utc'"})
    else:
        try:
            parsed_deadline = parse_datetime(str(deadline_val))
        except Exception as ex:
            field_errors.append({"field": "deadline_utc", "error": f"Invalid ISO datetime '{deadline_val}': {ex}"})

    # 3. Numeric values
    chainage_start = 0.0
    chainage_end = 0.0
    duration = 0
    try:
        chainage_start = float(sanitized_raw.get("chainage_start_km", 0.0))
        chainage_end = float(sanitized_raw.get("chainage_end_km", 0.0))
        if chainage_end < chainage_start:
            field_errors.append({"field": "chainage_end_km", "error": "chainage_end_km must be >= chainage_start_km"})
    except ValueError as ve:
        field_errors.append({"field": "chainage", "error": f"Invalid chainage value: {ve}"})

    try:
        duration = int(sanitized_raw.get("duration_minutes", 0))
        if duration < 15:
            field_errors.append({"field": "duration_minutes", "error": "duration_minutes must be >= 15"})
    except ValueError as ve:
        field_errors.append({"field": "duration_minutes", "error": f"Invalid duration_minutes: {ve}"})

    # 4. Department
    dept_str = str(sanitized_raw.get("department", "")).strip().upper()
    try:
        dept = DepartmentType(dept_str)
    except ValueError:
        field_errors.append({"field": "department", "error": f"Invalid department '{dept_str}'. Must be ENGINEERING, ELECTRICAL, or SIGNALLING."})
        dept = DepartmentType.ENGINEERING

    # 5. Criticality
    crit_str = str(sanitized_raw.get("criticality", "TIER_3_CYCLIC")).strip().upper()
    try:
        crit = CriticalityTier(crit_str)
    except ValueError:
        field_errors.append({"field": "criticality", "error": f"Invalid criticality '{crit_str}'"})
        crit = CriticalityTier.TIER_3_CYCLIC

    # 6. Power Block & Elementary Section Check
    raw_power = sanitized_raw.get("requires_power_block")
    requires_power = bool(raw_power is True or str(raw_power).strip().lower() in ("true", "1", "yes"))
    
    raw_sec = sanitized_raw.get("power_block_elementary_section")
    if raw_sec is None or str(raw_sec).strip() == "" or str(raw_sec).strip().lower() in ("none", "null"):
        elem_section = None
    else:
        elem_section = str(raw_sec).strip()

    if requires_power and not elem_section:
        field_errors.append({"field": "power_block_elementary_section", "error": "power_block_elementary_section is mandatory when requires_power_block is True"})

    # If any preliminary errors occurred, quarantine immediately
    if field_errors or parsed_deadline is None:
        quarantine = {
            "row_index": row_index,
            "business_key": business_key,
            "raw_data": raw,
            "error_type": "SchemaValidationError",
            "error_detail": f"{len(field_errors)} validation errors detected",
            "field_errors": field_errors,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        return None, quarantine

    # 7. Construct Pydantic DTO
    try:
        create_dto = TaskCreate(
            business_key=business_key,
            department=dept,
            sub_department=str(sanitized_raw.get("sub_department", "GENERAL")).strip(),
            work_type=str(sanitized_raw.get("work_type", "MAINTENANCE")).strip(),
            description=str(sanitized_raw.get("description", "")).strip(),
            station_from=str(sanitized_raw.get("station_from", "")).strip().upper(),
            station_to=str(sanitized_raw.get("station_to", "")).strip().upper(),
            track_segment_id=str(sanitized_raw.get("track_segment_id", "")).strip(),
            chainage_start_km=chainage_start,
            chainage_end_km=chainage_end,
            duration_minutes=duration,
            setup_buffer_minutes=int(sanitized_raw.get("setup_buffer_minutes", 30)),
            restoration_buffer_minutes=int(sanitized_raw.get("restoration_buffer_minutes", 30)),
            criticality=crit,
            deadline_utc=parsed_deadline,
            required_resources=parsed_resources,
            requires_power_block=requires_power,
            power_block_elementary_section=elem_section,
            requires_speed_restriction_after=bool(str(sanitized_raw.get("requires_speed_restriction_after", "false")).lower() in ("true", "1", "yes")),
            imposed_speed_kmh=int(sanitized_raw["imposed_speed_kmh"]) if sanitized_raw.get("imposed_speed_kmh") else None,
            provenance_mode=ProvenanceMode(str(sanitized_raw.get("provenance_mode", "TEST")).strip().upper()),
        )
        return create_dto, None

    except ValidationError as exc:
        quarantine = {
            "row_index": row_index,
            "business_key": business_key,
            "raw_data": raw,
            "error_type": "PydanticValidationError",
            "error_detail": str(exc),
            "field_errors": [{"field": str(e["loc"]), "error": e["msg"]} for e in exc.errors()],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        return None, quarantine


def ingest_json_records(records: List[Dict[str, Any]]) -> IngestionResult:
    result = IngestionResult()
    result.total_rows = len(records)
    for idx, row in enumerate(records, start=1):
        task, error = normalize_record(row, idx)
        if task:
            result.accepted_tasks.append(task)
        else:
            result.quarantined_rows.append(error)
    return result


def ingest_csv_content(csv_text: str) -> IngestionResult:
    result = IngestionResult()
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    rows = list(reader)
    result.total_rows = len(rows)
    for idx, row in enumerate(rows, start=1):
        task, error = normalize_record(row, idx)
        if task:
            result.accepted_tasks.append(task)
        else:
            result.quarantined_rows.append(error)
    return result
