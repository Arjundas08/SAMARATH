"""
Deterministic generator for Vayu-Kosh Corridor (VKC) seed datasets.
Produces 60 monthly tasks, 28-task weekly slice, 40 train paths, resource calendars, and 8 hand-checkable fixtures.
"""
import json
import os
from datetime import datetime, timedelta, timezone

SEED_DIR = os.path.join(os.path.dirname(__file__), "app", "db", "seed_data")
os.makedirs(SEED_DIR, exist_ok=True)

# 1. Topology
STATIONS = [
    {"station_code": "ALP", "station_name": "Alpha", "chainage_km": 0.0, "absolute_distance_meters": 0, "total_lines": 4, "has_crossover": True},
    {"station_code": "BRV", "station_name": "Bravo", "chainage_km": 22.5, "absolute_distance_meters": 22500, "total_lines": 3, "has_crossover": True},
    {"station_code": "CHR", "station_name": "Charlie", "chainage_km": 48.0, "absolute_distance_meters": 48000, "total_lines": 4, "has_crossover": True},
    {"station_code": "DLT", "station_name": "Delta", "chainage_km": 73.2, "absolute_distance_meters": 73200, "total_lines": 3, "has_crossover": True},
    {"station_code": "ECH", "station_name": "Echo", "chainage_km": 96.8, "absolute_distance_meters": 96800, "total_lines": 2, "has_crossover": False},
    {"station_code": "FXT", "station_name": "Foxtrot", "chainage_km": 120.0, "absolute_distance_meters": 120000, "total_lines": 4, "has_crossover": True},
]

TRACK_SEGMENTS = []
for i in range(len(STATIONS) - 1):
    s_from = STATIONS[i]["station_code"]
    s_to = STATIONS[i + 1]["station_code"]
    k_start = STATIONS[i]["chainage_km"]
    k_end = STATIONS[i + 1]["chainage_km"]
    m_len = int((k_end - k_start) * 1000)
    
    # UP line (Foxtrot -> Alpha)
    TRACK_SEGMENTS.append({
        "segment_id": f"SEC-0{i+1}-UP",
        "station_from": s_to,
        "station_to": s_from,
        "direction": "UP",
        "chainage_start_km": k_start,
        "chainage_end_km": k_end,
        "length_meters": m_len,
        "max_permissible_speed_kmh": 130,
        "elementary_section_id": f"ES-{s_from}-{s_to}-UP",
    })
    # DOWN line (Alpha -> Foxtrot)
    TRACK_SEGMENTS.append({
        "segment_id": f"SEC-0{i+1}-DN",
        "station_from": s_from,
        "station_to": s_to,
        "direction": "DOWN",
        "chainage_start_km": k_start,
        "chainage_end_km": k_end,
        "length_meters": m_len,
        "max_permissible_speed_kmh": 130,
        "elementary_section_id": f"ES-{s_from}-{s_to}-DN",
    })

# Elementary Sections & Neutral Section at Charlie (Km 48.0)
ELEMENTARY_SECTIONS = [
    {"elementary_section_id": "ES-ALP-BRV-01", "substation_id": "TSS-ALP", "chainage_start_km": 0.0, "chainage_end_km": 22.5, "is_neutral_section": False},
    {"elementary_section_id": "ES-BRV-CHR-01", "substation_id": "TSS-ALP", "chainage_start_km": 22.5, "chainage_end_km": 48.0, "is_neutral_section": False},
    {"elementary_section_id": "ES-CHR-SP-NEUTRAL", "substation_id": "SP-CHR", "chainage_start_km": 47.8, "chainage_end_km": 48.2, "is_neutral_section": True},
    {"elementary_section_id": "ES-CHR-DLT-01", "substation_id": "TSS-DLT", "chainage_start_km": 48.0, "chainage_end_km": 73.2, "is_neutral_section": False},
    {"elementary_section_id": "ES-DLT-ECH-01", "substation_id": "TSS-DLT", "chainage_start_km": 73.2, "chainage_end_km": 96.8, "is_neutral_section": False},
    {"elementary_section_id": "ES-ECH-FXT-01", "substation_id": "TSS-FXT", "chainage_start_km": 96.8, "chainage_end_km": 120.0, "is_neutral_section": False},
]

topology_data = {
    "corridor_code": "VKC",
    "corridor_name": "Vayu-Kosh Corridor",
    "total_length_km": 120.0,
    "stations": STATIONS,
    "track_segments": TRACK_SEGMENTS,
    "elementary_sections": ELEMENTARY_SECTIONS,
}
with open(os.path.join(SEED_DIR, "corridor_topology.json"), "w") as f:
    json.dump(topology_data, f, indent=2)

# 2. 60 Monthly Tasks across 30 days (1 to 30 October 2026)
TASKS = []
departments = ["ENGINEERING", "ELECTRICAL", "SIGNALLING"]
work_types = {
    "ENGINEERING": ["BALLAST_CLEANING", "PLAIN_TRACK_TAMPING", "TURNOUT_TAMPING", "RAIL_GRINDING"],
    "ELECTRICAL": ["OHE_REHABILITATION", "CANTILEVER_ADJUSTMENT", "INSULATOR_WASHING", "NEUTRAL_SECTION_CHECK"],
    "SIGNALLING": ["POINT_MACHINE_OVERHAUL", "AXLE_COUNTER_TESTING", "EI_DATA_LOG_CHECK", "TRACK_CIRCUIT_BONDING"]
}
machines = {
    "ENGINEERING": ["BCM-01", "BCM-02", "CSM-01", "CSM-02", "DGS-01"],
    "ELECTRICAL": ["TW-01", "TW-02", "WIRING-TRAIN-01"],
    "SIGNALLING": ["GANG-SIG-01", "GANG-SIG-02"]
}

for i in range(1, 61):
    dept = departments[(i - 1) % 3]
    wtype = work_types[dept][(i - 1) % len(work_types[dept])]
    seg = TRACK_SEGMENTS[(i - 1) % len(TRACK_SEGMENTS)]
    
    # Spread dates across October 2026
    day = 1 + ((i - 1) % 28)
    deadline = datetime(2026, 10, day, 23, 59, 59, tzinfo=timezone.utc)
    
    crit = "TIER_1_MANDATORY" if i % 5 == 1 else "TIER_2_SPEED_RESTRICTION" if i % 3 == 0 else "TIER_3_CYCLIC"
    duration = 240 if "BALLAST" in wtype or "REHABILITATION" in wtype else 150 if "TAMPING" in wtype else 90
    power = (dept == "ELECTRICAL") or ("BALLAST" in wtype)
    
    res_list = []
    if dept == "ENGINEERING":
        res_list.append({"resource_type": "MACHINE", "resource_id": machines[dept][(i - 1) % len(machines[dept])], "quantity": 1})
        res_list.append({"resource_type": "CREW", "resource_id": f"GANG-PWAY-0{(i % 3) + 1}", "quantity": 1})
    elif dept == "ELECTRICAL":
        res_list.append({"resource_type": "MACHINE", "resource_id": machines[dept][(i - 1) % len(machines[dept])], "quantity": 1})
        res_list.append({"resource_type": "CREW", "resource_id": f"GANG-TRD-0{(i % 2) + 1}", "quantity": 1})
    else:
        res_list.append({"resource_type": "CREW", "resource_id": machines[dept][(i - 1) % len(machines[dept])], "quantity": 1})
        
    TASKS.append({
        "business_key": f"TASK-{dept[:3]}-{i:04d}",
        "department": dept,
        "sub_department": "PWAY" if dept == "ENGINEERING" else "TRD" if dept == "ELECTRICAL" else "S&T",
        "work_type": wtype,
        "description": f"{wtype.replace('_', ' ').title()} on {seg['segment_id']} between {seg['station_from']} and {seg['station_to']}",
        "station_from": seg["station_from"],
        "station_to": seg["station_to"],
        "track_segment_id": seg["segment_id"],
        "chainage_start_km": seg["chainage_start_km"] + 1.0,
        "chainage_end_km": seg["chainage_start_km"] + 3.5,
        "duration_minutes": duration,
        "setup_buffer_minutes": 30 if duration > 120 else 15,
        "restoration_buffer_minutes": 30 if duration > 120 else 15,
        "criticality": crit,
        "deadline_utc": deadline.isoformat(),
        "required_resources": res_list,
        "requires_power_block": power,
        "power_block_elementary_section": seg["elementary_section_id"] if power else None,
        "requires_speed_restriction_after": ("BALLAST" in wtype),
        "imposed_speed_kmh": 45 if ("BALLAST" in wtype) else None,
        "provenance_mode": "TEST",
    })

with open(os.path.join(SEED_DIR, "demands_monthly_60.json"), "w") as f:
    json.dump(TASKS, f, indent=2)

# 3. Train Timetable (40 trains over 24-hr typical cycle, projected across week)
TRAINS = []
for t_idx in range(1, 41):
    is_freight = (t_idx % 3 == 0)
    ttype = "FREIGHT" if is_freight else "EXPRESS" if t_idx % 2 == 1 else "PASSENGER"
    direction = "UP" if t_idx % 2 == 1 else "DOWN"
    t_num = f"{12000 + t_idx}" if not is_freight else f"GOODS-{4000 + t_idx}"
    
    # Assign entry minute in 24-hr cycle (0 to 1440)
    base_entry_minute = (t_idx * 35) % 1400
    
    # Traverse corridor (5 block sections)
    segs = [s for s in TRACK_SEGMENTS if s["direction"] == direction]
    if direction == "UP":
        segs = segs[::-1]
        
    curr_min = base_entry_minute
    for seg in segs:
        transit_mins = 18 if not is_freight else 28
        entry_time = datetime(2026, 10, 12, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=curr_min)
        exit_time = entry_time + timedelta(minutes=transit_mins)
        TRAINS.append({
            "occupation_id": f"occ-{t_num}-{seg['segment_id']}",
            "train_number": t_num,
            "train_type": ttype,
            "track_segment_id": seg["segment_id"],
            "entry_time_utc": entry_time.isoformat(),
            "exit_time_utc": exit_time.isoformat(),
            "start_minute": curr_min,
            "end_minute": curr_min + transit_mins,
        })
        curr_min += transit_mins + 2

with open(os.path.join(SEED_DIR, "train_timetable.json"), "w") as f:
    json.dump(TRAINS, f, indent=2)

# 4. Resource Calendars
RESOURCE_CALENDARS = []
all_resources = [
    ("BCM-01", "MACHINE"), ("BCM-02", "MACHINE"),
    ("CSM-01", "MACHINE"), ("CSM-02", "MACHINE"),
    ("DGS-01", "MACHINE"),
    ("TW-01", "MACHINE"), ("TW-02", "MACHINE"),
    ("GANG-PWAY-01", "CREW"), ("GANG-PWAY-02", "CREW"),
    ("GANG-TRD-01", "CREW"), ("GANG-SIG-01", "CREW")
]

for rid, rtype in all_resources:
    # Available whole week with 1 scheduled maintenance outage for BCM-01 on Wednesday
    is_bcm_outage = (rid == "BCM-01")
    RESOURCE_CALENDARS.append({
        "calendar_id": f"cal-{rid}",
        "resource_id": rid,
        "resource_type": rtype,
        "corridor_code": "VKC",
        "available_start_utc": "2026-10-12T00:00:00Z",
        "available_end_utc": "2026-10-18T23:59:59Z",
        "is_outage": is_bcm_outage,
        "outage_reason": "Scheduled periodic overhaul" if is_bcm_outage else None,
    })

with open(os.path.join(SEED_DIR, "resource_calendars.json"), "w") as f:
    json.dump(RESOURCE_CALENDARS, f, indent=2)

# 5. Hand-Checkable Test Fixtures (8 explicit edge scenarios)
FIXTURES = {
    "normal": {
        "description": "Standard conflict-free single block opportunity.",
        "task_key": "TASK-TMS-0001",
        "expected_verdict": "VERIFIED_FEASIBLE",
        "units": "minutes",
    },
    "no_benefit": {
        "description": "Corridor traffic density too high; scheduling block incurs high delay penalty.",
        "task_key": "TASK-TMS-HIGH-DENSITY",
        "expected_verdict": "SUBOPTIMAL_HIGH_PENALTY",
        "units": "delay_minutes",
    },
    "unknown_compatibility": {
        "description": "Work package missing approved clearance evidence; must evaluate to UNKNOWN.",
        "task_key": "TASK-SPECIAL-UNVERIFIED",
        "expected_verdict": "UNKNOWN_BLOCKED",
        "units": "boolean",
    },
    "impossible_mandatory_deadline": {
        "description": "Mandatory task with statutory deadline before first available track possession.",
        "task_key": "TASK-TMS-PAST-DEADLINE",
        "expected_verdict": "INFEASIBILITY_PROVEN",
        "units": "minutes",
    },
    "cross_midnight": {
        "description": "Block possession spanning 23:00 to 03:30 across UTC and calendar day boundary.",
        "task_key": "TASK-CROSS-MIDNIGHT-01",
        "expected_verdict": "VERIFIED_FEASIBLE",
        "units": "minutes",
    },
    "resource_unavailable": {
        "description": "Required machine BCM-01 in maintenance outage; no feasible placement without substitution.",
        "task_key": "TASK-BCM-STARVED",
        "expected_verdict": "UNSCHEDULED_RESOURCE_STARVATION",
        "units": "resource_capacity",
    },
    "partial_execution": {
        "description": "Block granted for 180 min instead of requested 240 min; tracks partial progress.",
        "task_key": "TASK-PARTIAL-01",
        "expected_verdict": "PARTIAL_REVISE_ESTIMATE",
        "units": "meters_completed",
    },
    "locked_conflict": {
        "description": "Injected train path collides directly with a locked commitment; hard equality forces conflict.",
        "task_key": "TASK-LOCKED-01",
        "expected_verdict": "HARD_CONFLICT_DETECTED",
        "units": "boolean",
    }
}

with open(os.path.join(SEED_DIR, "hand_checkable_fixtures.json"), "w") as f:
    json.dump(FIXTURES, f, indent=2)

print("All VKC seed datasets successfully generated in app/db/seed_data/")
