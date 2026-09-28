"""
Corridor topology, stations, tracks, and electrical elementary sections.
"""
from typing import List, Optional
from pydantic import Field

from app.schemas.common import APIModel
from app.schemas.enums import TrackDirection


class Station(APIModel):
    station_code: str = Field(..., max_length=10)
    station_name: str
    chainage_km: float = Field(..., ge=0.0)
    absolute_distance_meters: int = Field(..., ge=0)
    total_lines: int = Field(default=2, ge=1)
    has_crossover: bool = False
    signaling_type: str = "ELECTRONIC_INTERLOCKING"


class TrackSegment(APIModel):
    segment_id: str = Field(..., description="e.g. SEC-01-UP")
    station_from: str
    station_to: str
    direction: TrackDirection
    chainage_start_km: float
    chainage_end_km: float
    length_meters: int
    max_permissible_speed_kmh: int = 130
    elementary_section_id: str


class ElementarySection(APIModel):
    elementary_section_id: str
    substation_id: str
    chainage_start_km: float
    chainage_end_km: float
    is_neutral_section: bool = False


class CorridorTopology(APIModel):
    corridor_code: str = "VKC"
    corridor_name: str = "Vayu-Kosh Corridor"
    total_length_km: float = 120.0
    stations: List[Station] = Field(default_factory=list)
    track_segments: List[TrackSegment] = Field(default_factory=list)
    elementary_sections: List[ElementarySection] = Field(default_factory=list)
