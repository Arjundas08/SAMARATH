"""
Domain Engine: Spatial Track Topology and Electrical Footprint Resolver.
Implements Blueprint Section 14.
Invariants:
- Integer metres / chainage precision.
- Nearby km coordinates are insufficient alone: must share verified track segments and electrical boundaries.
- Electrical footprint can affect more than one track (e.g. Neutral Section at CHR km 48.0 affecting UP and DN).
- Unknown mapping blocks candidate generation and produces structured UNKNOWN_MAPPING reason.
"""
from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel

from app.schemas.enums import TrackDirection


class TrackFootprint(BaseModel):
    track_segment_id: str
    direction: TrackDirection
    chainage_start_km: float
    chainage_end_km: float
    elementary_sections: List[str] = []
    affected_adjacent_tracks: List[str] = []
    is_neutral_section: bool = False
    is_resolved: bool = True
    unresolved_reason: Optional[str] = None


# Known Vayu-Kosh Corridor Segment Catalog
_SEGMENT_BOUNDS = {
    "TRACK-ALP-BRV-UP": {"start": 0.0, "end": 25.0, "dir": TrackDirection.UP, "station_from": "BRV", "station_to": "ALP"},
    "TRACK-ALP-BRV-DN": {"start": 0.0, "end": 25.0, "dir": TrackDirection.DOWN, "station_from": "ALP", "station_to": "BRV"},
    "TRACK-BRV-CHR-UP": {"start": 25.0, "end": 50.0, "dir": TrackDirection.UP, "station_from": "CHR", "station_to": "BRV"},
    "TRACK-BRV-CHR-DN": {"start": 25.0, "end": 50.0, "dir": TrackDirection.DOWN, "station_from": "BRV", "station_to": "CHR"},
    "TRACK-CHR-DLT-UP": {"start": 50.0, "end": 75.0, "dir": TrackDirection.UP, "station_from": "DLT", "station_to": "CHR"},
    "TRACK-CHR-DLT-DN": {"start": 50.0, "end": 75.0, "dir": TrackDirection.DOWN, "station_from": "CHR", "station_to": "DLT"},
    "TRACK-DLT-ECH-UP": {"start": 75.0, "end": 95.0, "dir": TrackDirection.UP, "station_from": "ECH", "station_to": "DLT"},
    "TRACK-DLT-ECH-DN": {"start": 75.0, "end": 95.0, "dir": TrackDirection.DOWN, "station_from": "DLT", "station_to": "ECH"},
    # VKC Corridor Canonical Segments
    "SEC-01-UP": {"start": 0.0, "end": 25.0, "dir": TrackDirection.UP, "station_from": "BRV", "station_to": "ALP"},
    "SEC-01-DN": {"start": 0.0, "end": 25.0, "dir": TrackDirection.DOWN, "station_from": "ALP", "station_to": "BRV"},
    "SEC-02-UP": {"start": 20.0, "end": 50.0, "dir": TrackDirection.UP, "station_from": "CHR", "station_to": "BRV"},
    "SEC-02-DN": {"start": 20.0, "end": 50.0, "dir": TrackDirection.DOWN, "station_from": "BRV", "station_to": "CHR"},
    "SEC-03-UP": {"start": 45.0, "end": 75.0, "dir": TrackDirection.UP, "station_from": "DLT", "station_to": "CHR"},
    "SEC-03-DN": {"start": 45.0, "end": 75.0, "dir": TrackDirection.DOWN, "station_from": "CHR", "station_to": "DLT"},
    "SEC-04-UP": {"start": 70.0, "end": 100.0, "dir": TrackDirection.UP, "station_from": "ECH", "station_to": "DLT"},
    "SEC-04-DN": {"start": 70.0, "end": 100.0, "dir": TrackDirection.DOWN, "station_from": "DLT", "station_to": "ECH"},
    "SEC-05-UP": {"start": 95.0, "end": 125.0, "dir": TrackDirection.UP, "station_from": "FXT", "station_to": "ECH"},
    "SEC-05-DN": {"start": 95.0, "end": 125.0, "dir": TrackDirection.DOWN, "station_from": "ECH", "station_to": "FXT"},
}

# Neutral Section at CHR km 48.0: de-energization affects both UP and DOWN lines
_NEUTRAL_SECTION_KM = 48.0
_NEUTRAL_SECTION_BUFFER_KM = 2.0  # 46.0 to 50.0 km


def resolve_task_footprint(
    track_segment_id: str,
    chainage_start_km: float,
    chainage_end_km: float,
    requires_power_block: bool = False,
    elementary_section: Optional[str] = None,
) -> TrackFootprint:
    """
    Resolves physical track segment and electrical isolation footprint for a task.
    """
    meta = _SEGMENT_BOUNDS.get(track_segment_id)
    if not meta:
        return TrackFootprint(
            track_segment_id=track_segment_id,
            direction=TrackDirection.BOTH,
            chainage_start_km=chainage_start_km,
            chainage_end_km=chainage_end_km,
            is_resolved=False,
            unresolved_reason=f"Unknown track segment '{track_segment_id}'. Unregistered spatial resource blocks planning eligibility.",
        )

    # Check bounds containment
    seg_start = meta["start"]
    seg_end = meta["end"]
    if chainage_start_km < seg_start or chainage_end_km > seg_end:
        return TrackFootprint(
            track_segment_id=track_segment_id,
            direction=meta["dir"],
            chainage_start_km=chainage_start_km,
            chainage_end_km=chainage_end_km,
            is_resolved=False,
            unresolved_reason=f"Task chainage [{chainage_start_km:.1f} - {chainage_end_km:.1f} km] exceeds segment boundaries [{seg_start:.1f} - {seg_end:.1f} km].",
        )

    elem_sections = []
    affected_adjacent = []
    is_ns = False

    # Check if this task intersects the Charlie Neutral Section or requires CHR power block
    near_ns = not (chainage_end_km < (_NEUTRAL_SECTION_KM - _NEUTRAL_SECTION_BUFFER_KM) or chainage_start_km > (_NEUTRAL_SECTION_KM + _NEUTRAL_SECTION_BUFFER_KM))
    has_chr_ref = "CHR" in track_segment_id or (elementary_section and "CHR" in elementary_section) or track_segment_id in ("SEC-02-UP", "SEC-02-DN", "SEC-03-UP", "SEC-03-DN")
    if (near_ns and has_chr_ref) or (requires_power_block and has_chr_ref):
        is_ns = True
        elem_sections.append("ELEM-CHR-NS-01")
        # If power block is required at neutral section, it isolates BOTH UP and DN tracks!
        if requires_power_block:
            if "UP" in track_segment_id:
                affected_adjacent.append(track_segment_id.replace("UP", "DN"))
            elif "DN" in track_segment_id:
                affected_adjacent.append(track_segment_id.replace("DN", "UP"))

    if requires_power_block and elementary_section:
        if elementary_section not in elem_sections:
            elem_sections.append(elementary_section)

    return TrackFootprint(
        track_segment_id=track_segment_id,
        direction=meta["dir"],
        chainage_start_km=chainage_start_km,
        chainage_end_km=chainage_end_km,
        elementary_sections=elem_sections,
        affected_adjacent_tracks=affected_adjacent,
        is_neutral_section=is_ns,
        is_resolved=True,
    )


def are_spatially_colocated(fp_a: TrackFootprint, fp_b: TrackFootprint) -> bool:
    """
    Checks if two footprints can share a traffic possession block.
    They must be on the same track segment and have overlapping or abutting chainage.
    """
    if not fp_a.is_resolved or not fp_b.is_resolved:
        return False

    if fp_a.track_segment_id != fp_b.track_segment_id:
        return False

    # Check chainage overlap or proximity within 2.0 km
    max_start = max(fp_a.chainage_start_km, fp_b.chainage_start_km)
    min_end = min(fp_a.chainage_end_km, fp_b.chainage_end_km)

    if max_start <= min_end:
        # Overlapping
        return True

    # Check if within 2.0 km on same segment
    gap = max_start - min_end
    return gap <= 2.0
