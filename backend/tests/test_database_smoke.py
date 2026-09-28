"""
Test database table creation and relational foreign key integrity.
"""
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import (
    CorridorModel,
    StationModel,
    TrackSegmentModel,
    TaskModel,
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


def test_schema_creation_and_relational_integrity():
    # Use in-memory SQLite database to test all model definitions and FK relations
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # 1. Insert Corridor
        corridor = CorridorModel(
            corridor_code="VKC",
            corridor_name="Vayu-Kosh Corridor",
            total_length_km=120.0,
        )
        session.add(corridor)
        session.commit()

        # 2. Insert Stations
        stn1 = StationModel(
            station_code="ALP",
            corridor_code="VKC",
            station_name="Alpha",
            chainage_km=0.0,
            absolute_distance_meters=0,
            total_lines=4,
            has_crossover=True,
        )
        stn2 = StationModel(
            station_code="BRV",
            corridor_code="VKC",
            station_name="Bravo",
            chainage_km=22.5,
            absolute_distance_meters=22500,
            total_lines=3,
            has_crossover=True,
        )
        session.add_all([stn1, stn2])
        session.commit()

        # 3. Insert Track Segment
        seg = TrackSegmentModel(
            segment_id="SEC-01-UP",
            corridor_code="VKC",
            station_from="ALP",
            station_to="BRV",
            direction=TrackDirection.UP,
            chainage_start_km=0.0,
            chainage_end_km=22.5,
            length_meters=22500,
            max_permissible_speed_kmh=130,
            elementary_section_id="ES-ALP-BRV-01",
        )
        session.add(seg)
        session.commit()

        # Query back and verify relations
        queried_corridor = session.scalar(select(CorridorModel).where(CorridorModel.corridor_code == "VKC"))
        assert queried_corridor is not None
        assert len(queried_corridor.stations) == 2
        assert len(queried_corridor.track_segments) == 1
        assert queried_corridor.stations[0].station_code == "ALP"
