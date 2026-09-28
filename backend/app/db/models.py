"""
SQLAlchemy relational models implementing the full foreign key spine.
"""
from datetime import datetime
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum,
    JSON,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.schemas.enums import (
    DepartmentType,
    CriticalityTier,
    DemandStatus,
    ProvenanceMode,
    ObjectiveProfile,
    JobState,
    SolverStatus,
    ValidationVerdict,
    PlanStatus,
    ProgrammeAuthorityState,
    FieldAuthorityState,
    ApprovalEligibility,
    TrackDirection,
)


def generate_uuid():
    return str(uuid.uuid4())


class CorridorModel(Base):
    __tablename__ = "corridors"

    corridor_code = Column(String(10), primary_key=True)
    corridor_name = Column(String(100), nullable=False)
    total_length_km = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    stations = relationship("StationModel", back_populates="corridor", cascade="all, delete-orphan")
    track_segments = relationship("TrackSegmentModel", back_populates="corridor", cascade="all, delete-orphan")


class StationModel(Base):
    __tablename__ = "stations"

    station_code = Column(String(10), primary_key=True)
    corridor_code = Column(String(10), ForeignKey("corridors.corridor_code", ondelete="CASCADE"), nullable=False)
    station_name = Column(String(100), nullable=False)
    chainage_km = Column(Float, nullable=False)
    absolute_distance_meters = Column(Integer, nullable=False)
    total_lines = Column(Integer, default=2, nullable=False)
    has_crossover = Column(Boolean, default=False, nullable=False)
    signaling_type = Column(String(50), default="ELECTRONIC_INTERLOCKING", nullable=False)

    corridor = relationship("CorridorModel", back_populates="stations")


class TrackSegmentModel(Base):
    __tablename__ = "track_segments"

    segment_id = Column(String(20), primary_key=True)
    corridor_code = Column(String(10), ForeignKey("corridors.corridor_code", ondelete="CASCADE"), nullable=False)
    station_from = Column(String(10), ForeignKey("stations.station_code"), nullable=False)
    station_to = Column(String(10), ForeignKey("stations.station_code"), nullable=False)
    direction = Column(SQLEnum(TrackDirection), nullable=False)
    chainage_start_km = Column(Float, nullable=False)
    chainage_end_km = Column(Float, nullable=False)
    length_meters = Column(Integer, nullable=False)
    max_permissible_speed_kmh = Column(Integer, default=130, nullable=False)
    elementary_section_id = Column(String(50), nullable=False)

    corridor = relationship("CorridorModel", back_populates="track_segments")


class TaskModel(Base):
    __tablename__ = "tasks"

    task_id = Column(String(36), primary_key=True, default=generate_uuid)
    business_key = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(SQLEnum(DepartmentType), nullable=False)
    sub_department = Column(String(50), nullable=False)
    work_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    station_from = Column(String(10), ForeignKey("stations.station_code"), nullable=False)
    station_to = Column(String(10), ForeignKey("stations.station_code"), nullable=False)
    track_segment_id = Column(String(20), ForeignKey("track_segments.segment_id"), nullable=False)
    chainage_start_km = Column(Float, nullable=False)
    chainage_end_km = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    setup_buffer_minutes = Column(Integer, default=30, nullable=False)
    restoration_buffer_minutes = Column(Integer, default=30, nullable=False)
    total_block_minutes = Column(Integer, nullable=False)
    criticality = Column(SQLEnum(CriticalityTier), nullable=False)
    deadline_utc = Column(DateTime, nullable=False)
    preferred_windows = Column(JSON, default=list)
    required_resources = Column(JSON, default=list)
    requires_power_block = Column(Boolean, default=False, nullable=False)
    power_block_elementary_section = Column(String(50), nullable=True)
    requires_speed_restriction_after = Column(Boolean, default=False, nullable=False)
    imposed_speed_kmh = Column(Integer, nullable=True)
    demand_status = Column(SQLEnum(DemandStatus), default=DemandStatus.VALIDATED, nullable=False)
    provenance_mode = Column(SQLEnum(ProvenanceMode), default=ProvenanceMode.TEST, nullable=False)
    created_at_utc = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(50), default="system", nullable=False)

    __table_args__ = (
        CheckConstraint("chainage_end_km >= chainage_start_km", name="check_task_chainage_valid"),
        CheckConstraint("duration_minutes > 0", name="check_task_duration_positive"),
        Index("idx_tasks_dept_status", "department", "demand_status"),
    )


class SnapshotModel(Base):
    __tablename__ = "snapshots"

    snapshot_id = Column(String(36), primary_key=True, default=generate_uuid)
    snapshot_hash = Column(String(71), unique=True, nullable=False, index=True)
    corridor_code = Column(String(10), ForeignKey("corridors.corridor_code"), nullable=False)
    horizon_start_utc = Column(DateTime, nullable=False)
    horizon_end_utc = Column(DateTime, nullable=False)
    provenance_mode = Column(SQLEnum(ProvenanceMode), default=ProvenanceMode.TEST, nullable=False)
    is_sealed = Column(Boolean, default=True, nullable=False)
    created_at_utc = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(50), default="system", nullable=False)

    memberships = relationship("SnapshotTaskMembership", back_populates="snapshot", cascade="all, delete-orphan")
    plans = relationship("PlanVersionModel", back_populates="snapshot")
    solve_jobs = relationship("SolveJobModel", back_populates="snapshot")


class SnapshotTaskMembership(Base):
    __tablename__ = "snapshot_task_memberships"

    snapshot_id = Column(String(36), ForeignKey("snapshots.snapshot_id", ondelete="CASCADE"), primary_key=True)
    task_id = Column(String(36), ForeignKey("tasks.task_id", ondelete="RESTRICT"), primary_key=True)

    snapshot = relationship("SnapshotModel", back_populates="memberships")
    task = relationship("TaskModel")


class TrainOccupationModel(Base):
    __tablename__ = "train_occupations"

    occupation_id = Column(String(36), primary_key=True, default=generate_uuid)
    snapshot_id = Column(String(36), ForeignKey("snapshots.snapshot_id", ondelete="CASCADE"), nullable=False)
    train_number = Column(String(20), nullable=False)
    train_type = Column(String(20), nullable=False)
    track_segment_id = Column(String(20), ForeignKey("track_segments.segment_id"), nullable=False)
    entry_time_utc = Column(DateTime, nullable=False)
    exit_time_utc = Column(DateTime, nullable=False)
    start_minute = Column(Integer, nullable=False)
    end_minute = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("exit_time_utc > entry_time_utc", name="check_train_times_valid"),
        Index("idx_train_occ_snap_segment", "snapshot_id", "track_segment_id"),
    )


class ResourceCalendarModel(Base):
    __tablename__ = "resource_calendars"

    calendar_id = Column(String(36), primary_key=True, default=generate_uuid)
    resource_id = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(20), nullable=False)
    corridor_code = Column(String(10), ForeignKey("corridors.corridor_code"), nullable=False)
    available_start_utc = Column(DateTime, nullable=False)
    available_end_utc = Column(DateTime, nullable=False)
    is_outage = Column(Boolean, default=False, nullable=False)
    outage_reason = Column(String(100), nullable=True)


class SolveJobModel(Base):
    __tablename__ = "solver_jobs"

    job_id = Column(String(36), primary_key=True, default=generate_uuid)
    corridor_code = Column(String(10), nullable=False, default="VKC", index=True)
    snapshot_id = Column(String(36), ForeignKey("snapshots.snapshot_id", ondelete="CASCADE"), nullable=False)
    objective_profile = Column(SQLEnum(ObjectiveProfile), nullable=False)
    status = Column(SQLEnum(JobState), default=JobState.QUEUED, nullable=False, index=True)
    progress_percentage = Column(Integer, default=0, nullable=False)
    current_phase = Column(String(50), default="QUEUED", nullable=False)
    fencing_token = Column(Integer, default=0, nullable=False)
    attempt_count = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    idempotency_key = Column(String(128), nullable=True, index=True)
    request_fingerprint = Column(String(64), nullable=True)
    created_by_user = Column(String(50), nullable=True, default="planner")
    user_role = Column(String(50), nullable=True, default="PLANNER")
    lease_owner = Column(String(50), nullable=True)
    lease_expires_at = Column(DateTime, nullable=True)
    result_plan_id = Column(String(36), nullable=True)
    error_detail = Column(Text, nullable=True)
    solve_parameters = Column(JSON, default=dict, nullable=False)
    result_summary = Column(JSON, nullable=True)
    is_snapshot_obsolete = Column(Boolean, default=False, nullable=False)
    created_at_utc = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at_utc = Column(DateTime, nullable=True)

    snapshot = relationship("SnapshotModel", back_populates="solve_jobs")


class PlanVersionModel(Base):
    __tablename__ = "plan_versions"

    plan_id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_version_number = Column(Integer, default=1, nullable=False)
    corridor_code = Column(String(10), nullable=False, default="VKC", index=True)
    snapshot_id = Column(String(36), ForeignKey("snapshots.snapshot_id", ondelete="RESTRICT"), nullable=False)
    parent_plan_id = Column(String(36), ForeignKey("plan_versions.plan_id"), nullable=True)
    validation_id = Column(String(36), nullable=True)
    horizon_type = Column(String(20), default="WEEKLY", nullable=False)
    plan_status = Column(SQLEnum(PlanStatus), default=PlanStatus.DRAFT_PROPOSAL, nullable=False)
    solver_status = Column(String(20), nullable=True)
    checker_verdict = Column(String(30), nullable=True)
    programme_authority_state = Column(SQLEnum(ProgrammeAuthorityState), default=ProgrammeAuthorityState.PROPOSED, nullable=False)
    field_authority_state = Column(SQLEnum(FieldAuthorityState), default=FieldAuthorityState.NOT_REQUESTED, nullable=False)
    approval_eligibility = Column(SQLEnum(ApprovalEligibility), default=ApprovalEligibility.ELIGIBLE, nullable=False)
    reconciliation_cases = Column(JSON, default=list, nullable=False)
    metrics = Column(JSON, default=dict, nullable=False)
    created_at_utc = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at_utc = Column(DateTime, nullable=True)
    approved_by_officer = Column(String(100), nullable=True)

    snapshot = relationship("SnapshotModel", back_populates="plans")
    assignments = relationship("MaterializedAssignmentModel", back_populates="plan", cascade="all, delete-orphan")


class MaterializedAssignmentModel(Base):
    __tablename__ = "materialized_assignments"

    assignment_id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_id = Column(String(36), ForeignKey("plan_versions.plan_id", ondelete="CASCADE"), nullable=False)
    task_id = Column(String(36), ForeignKey("tasks.task_id", ondelete="RESTRICT"), nullable=False)
    business_key = Column(String(50), nullable=False)
    track_segment_id = Column(String(20), ForeignKey("track_segments.segment_id"), nullable=False)
    start_utc = Column(DateTime, nullable=False)
    end_utc = Column(DateTime, nullable=False)
    start_minute = Column(Integer, nullable=False)
    end_minute = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    work_phase_schedule = Column(JSON, nullable=False)
    assigned_resources = Column(JSON, default=list, nullable=False)
    power_block_required = Column(Boolean, default=False, nullable=False)
    power_block_section = Column(String(50), nullable=True)
    is_locked = Column(Boolean, default=False, nullable=False)
    is_shadow_block = Column(Boolean, default=False, nullable=False)
    bundled_with_task_ids = Column(JSON, default=list, nullable=False)

    plan = relationship("PlanVersionModel", back_populates="assignments")
    task = relationship("TaskModel")


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    event_id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    user_id = Column(String(50), nullable=False)
    user_role = Column(String(50), nullable=False)
    payload_before = Column(JSON, nullable=True)
    payload_after = Column(JSON, nullable=True)
    timestamp_utc = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class DisruptionEventModel(Base):
    """
    Phase 13: Versioned, idempotent disruption events.
    Source ordering and idempotency keys prevent duplicate processing.
    """
    __tablename__ = "disruption_events"

    event_id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="MEDIUM")
    corridor_code = Column(String(10), nullable=False, default="VKC", index=True)
    source_system = Column(String(50), nullable=False, default="MANUAL")
    source_order = Column(Integer, nullable=False)
    idempotency_key = Column(String(128), unique=True, nullable=False, index=True)
    processing_status = Column(String(30), nullable=False, default="RECEIVED")
    payload = Column(JSON, nullable=False, default=dict)
    description = Column(Text, nullable=True)
    affected_plan_ids = Column(JSON, default=list, nullable=False)
    invalidated_plan_applicability = Column(String(20), nullable=True)
    submitted_by = Column(String(50), nullable=False, default="planner")
    coalesced_into_batch_id = Column(String(36), nullable=True)
    created_at_utc = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at_utc = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_disruption_corridor_status", "corridor_code", "processing_status"),
        Index("idx_disruption_source_order", "source_system", "source_order"),
    )


class PlanDiffModel(Base):
    """
    Phase 13: Persisted PlanDiff between two plan versions.
    """
    __tablename__ = "plan_diffs"

    diff_id = Column(String(36), primary_key=True, default=generate_uuid)
    from_plan_id = Column(String(36), ForeignKey("plan_versions.plan_id"), nullable=False)
    from_plan_version = Column(Integer, nullable=False)
    to_plan_id = Column(String(36), ForeignKey("plan_versions.plan_id"), nullable=False)
    to_plan_version = Column(Integer, nullable=False)
    summary = Column(JSON, nullable=False, default=dict)
    entries = Column(JSON, nullable=False, default=list)
    triggering_event_ids = Column(JSON, default=list, nullable=False)
    created_at_utc = Column(DateTime, default=datetime.utcnow, nullable=False)


class WeatherObservationModel(Base):
    """
    Live / Cached weather observations from Open-Meteo API.
    Maintains data provenance, retrieval timestamp, and forecast parameters.
    """
    __tablename__ = "weather_observations"

    observation_id = Column(String(36), primary_key=True, default=generate_uuid)
    corridor_code = Column(String(10), nullable=False, default="VKC", index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    source = Column(String(50), nullable=False, default="LIVE_EXTERNAL")  # LIVE_EXTERNAL, CACHED, UNAVAILABLE
    retrieval_timestamp_utc = Column(DateTime, default=datetime.utcnow, nullable=False)
    forecast_timestamp_utc = Column(DateTime, nullable=False)
    temperature_c = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    wind_speed_kmh = Column(Float, nullable=True)
    wind_gusts_kmh = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    raw_payload = Column(JSON, nullable=False, default=dict)

    __table_args__ = (
        Index("idx_weather_corridor_time", "corridor_code", "forecast_timestamp_utc"),
    )

