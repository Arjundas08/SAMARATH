"""Initial schema migration with complete relational FK spine.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-26 05:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Corridors
    op.create_table(
        "corridors",
        sa.Column("corridor_code", sa.String(length=10), nullable=False),
        sa.Column("corridor_name", sa.String(length=100), nullable=False),
        sa.Column("total_length_km", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("corridor_code")
    )

    # 2. Stations
    op.create_table(
        "stations",
        sa.Column("station_code", sa.String(length=10), nullable=False),
        sa.Column("corridor_code", sa.String(length=10), nullable=False),
        sa.Column("station_name", sa.String(length=100), nullable=False),
        sa.Column("chainage_km", sa.Float(), nullable=False),
        sa.Column("absolute_distance_meters", sa.Integer(), nullable=False),
        sa.Column("total_lines", sa.Integer(), nullable=False),
        sa.Column("has_crossover", sa.Boolean(), nullable=False),
        sa.Column("signaling_type", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["corridor_code"], ["corridors.corridor_code"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("station_code")
    )

    # 3. Track Segments
    op.create_table(
        "track_segments",
        sa.Column("segment_id", sa.String(length=20), nullable=False),
        sa.Column("corridor_code", sa.String(length=10), nullable=False),
        sa.Column("station_from", sa.String(length=10), nullable=False),
        sa.Column("station_to", sa.String(length=10), nullable=False),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("chainage_start_km", sa.Float(), nullable=False),
        sa.Column("chainage_end_km", sa.Float(), nullable=False),
        sa.Column("length_meters", sa.Integer(), nullable=False),
        sa.Column("max_permissible_speed_kmh", sa.Integer(), nullable=False),
        sa.Column("elementary_section_id", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["corridor_code"], ["corridors.corridor_code"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["station_from"], ["stations.station_code"]),
        sa.ForeignKeyConstraint(["station_to"], ["stations.station_code"]),
        sa.PrimaryKeyConstraint("segment_id")
    )

    # 4. Tasks
    op.create_table(
        "tasks",
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("business_key", sa.String(length=50), nullable=False),
        sa.Column("department", sa.String(length=20), nullable=False),
        sa.Column("sub_department", sa.String(length=50), nullable=False),
        sa.Column("work_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("station_from", sa.String(length=10), nullable=False),
        sa.Column("station_to", sa.String(length=10), nullable=False),
        sa.Column("track_segment_id", sa.String(length=20), nullable=False),
        sa.Column("chainage_start_km", sa.Float(), nullable=False),
        sa.Column("chainage_end_km", sa.Float(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("setup_buffer_minutes", sa.Integer(), nullable=False),
        sa.Column("restoration_buffer_minutes", sa.Integer(), nullable=False),
        sa.Column("total_block_minutes", sa.Integer(), nullable=False),
        sa.Column("criticality", sa.String(length=30), nullable=False),
        sa.Column("deadline_utc", sa.DateTime(), nullable=False),
        sa.Column("preferred_windows", sa.JSON(), nullable=True),
        sa.Column("required_resources", sa.JSON(), nullable=True),
        sa.Column("requires_power_block", sa.Boolean(), nullable=False),
        sa.Column("power_block_elementary_section", sa.String(length=50), nullable=True),
        sa.Column("requires_speed_restriction_after", sa.Boolean(), nullable=False),
        sa.Column("imposed_speed_kmh", sa.Integer(), nullable=True),
        sa.Column("demand_status", sa.String(length=20), nullable=False),
        sa.Column("provenance_mode", sa.String(length=20), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=50), nullable=False),
        sa.CheckConstraint("chainage_end_km >= chainage_start_km", name="check_task_chainage_valid"),
        sa.CheckConstraint("duration_minutes > 0", name="check_task_duration_positive"),
        sa.ForeignKeyConstraint(["station_from"], ["stations.station_code"]),
        sa.ForeignKeyConstraint(["station_to"], ["stations.station_code"]),
        sa.ForeignKeyConstraint(["track_segment_id"], ["track_segments.segment_id"]),
        sa.PrimaryKeyConstraint("task_id"),
        sa.UniqueConstraint("business_key")
    )
    op.create_index("idx_tasks_dept_status", "tasks", ["department", "demand_status"])

    # 5. Snapshots
    op.create_table(
        "snapshots",
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=71), nullable=False),
        sa.Column("corridor_code", sa.String(length=10), nullable=False),
        sa.Column("horizon_start_utc", sa.DateTime(), nullable=False),
        sa.Column("horizon_end_utc", sa.DateTime(), nullable=False),
        sa.Column("provenance_mode", sa.String(length=20), nullable=False),
        sa.Column("is_sealed", sa.Boolean(), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["corridor_code"], ["corridors.corridor_code"]),
        sa.PrimaryKeyConstraint("snapshot_id"),
        sa.UniqueConstraint("snapshot_hash")
    )

    # 6. Snapshot Memberships
    op.create_table(
        "snapshot_task_memberships",
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["snapshots.snapshot_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.task_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("snapshot_id", "task_id")
    )

    # 7. Train Occupations
    op.create_table(
        "train_occupations",
        sa.Column("occupation_id", sa.String(length=36), nullable=False),
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("train_number", sa.String(length=20), nullable=False),
        sa.Column("train_type", sa.String(length=20), nullable=False),
        sa.Column("track_segment_id", sa.String(length=20), nullable=False),
        sa.Column("entry_time_utc", sa.DateTime(), nullable=False),
        sa.Column("exit_time_utc", sa.DateTime(), nullable=False),
        sa.Column("start_minute", sa.Integer(), nullable=False),
        sa.Column("end_minute", sa.Integer(), nullable=False),
        sa.CheckConstraint("exit_time_utc > entry_time_utc", name="check_train_times_valid"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["snapshots.snapshot_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["track_segment_id"], ["track_segments.segment_id"]),
        sa.PrimaryKeyConstraint("occupation_id")
    )
    op.create_index("idx_train_occ_snap_segment", "train_occupations", ["snapshot_id", "track_segment_id"])

    # 8. Resource Calendars
    op.create_table(
        "resource_calendars",
        sa.Column("calendar_id", sa.String(length=36), nullable=False),
        sa.Column("resource_id", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=20), nullable=False),
        sa.Column("corridor_code", sa.String(length=10), nullable=False),
        sa.Column("available_start_utc", sa.DateTime(), nullable=False),
        sa.Column("available_end_utc", sa.DateTime(), nullable=False),
        sa.Column("is_outage", sa.Boolean(), nullable=False),
        sa.Column("outage_reason", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["corridor_code"], ["corridors.corridor_code"]),
        sa.PrimaryKeyConstraint("calendar_id")
    )
    op.create_index("idx_res_cal_id", "resource_calendars", ["resource_id"])

    # 9. Solve Jobs
    op.create_table(
        "solver_jobs",
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("objective_profile", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("progress_percentage", sa.Integer(), nullable=False),
        sa.Column("current_phase", sa.String(length=50), nullable=False),
        sa.Column("lease_owner", sa.String(length=50), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(), nullable=True),
        sa.Column("result_plan_id", sa.String(length=36), nullable=True),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(), nullable=False),
        sa.Column("completed_at_utc", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["snapshot_id"], ["snapshots.snapshot_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("job_id")
    )
    op.create_index("idx_jobs_status", "solver_jobs", ["status"])

    # 10. Plan Versions
    op.create_table(
        "plan_versions",
        sa.Column("plan_id", sa.String(length=36), nullable=False),
        sa.Column("plan_version_number", sa.Integer(), nullable=False),
        sa.Column("snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("parent_plan_id", sa.String(length=36), nullable=True),
        sa.Column("validation_id", sa.String(length=36), nullable=True),
        sa.Column("horizon_type", sa.String(length=20), nullable=False),
        sa.Column("plan_status", sa.String(length=30), nullable=False),
        sa.Column("programme_authority_state", sa.String(length=30), nullable=False),
        sa.Column("field_authority_state", sa.String(length=30), nullable=False),
        sa.Column("approval_eligibility", sa.String(length=30), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(), nullable=False),
        sa.Column("approved_at_utc", sa.DateTime(), nullable=True),
        sa.Column("approved_by_officer", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["parent_plan_id"], ["plan_versions.plan_id"]),
        sa.ForeignKeyConstraint(["snapshot_id"], ["snapshots.snapshot_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("plan_id")
    )

    # 11. Materialized Assignments
    op.create_table(
        "materialized_assignments",
        sa.Column("assignment_id", sa.String(length=36), nullable=False),
        sa.Column("plan_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=36), nullable=False),
        sa.Column("business_key", sa.String(length=50), nullable=False),
        sa.Column("track_segment_id", sa.String(length=20), nullable=False),
        sa.Column("start_utc", sa.DateTime(), nullable=False),
        sa.Column("end_utc", sa.DateTime(), nullable=False),
        sa.Column("start_minute", sa.Integer(), nullable=False),
        sa.Column("end_minute", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("work_phase_schedule", sa.JSON(), nullable=False),
        sa.Column("assigned_resources", sa.JSON(), nullable=False),
        sa.Column("power_block_required", sa.Boolean(), nullable=False),
        sa.Column("power_block_section", sa.String(length=50), nullable=True),
        sa.Column("is_locked", sa.Boolean(), nullable=False),
        sa.Column("is_shadow_block", sa.Boolean(), nullable=False),
        sa.Column("bundled_with_task_ids", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plan_versions.plan_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.task_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["track_segment_id"], ["track_segments.segment_id"]),
        sa.PrimaryKeyConstraint("assignment_id")
    )

    # 12. Audit Events
    op.create_table(
        "audit_events",
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.String(length=50), nullable=False),
        sa.Column("user_role", sa.String(length=50), nullable=False),
        sa.Column("payload_before", sa.JSON(), nullable=True),
        sa.Column("payload_after", sa.JSON(), nullable=True),
        sa.Column("timestamp_utc", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("event_id")
    )
    op.create_index("idx_audit_entity", "audit_events", ["entity_id"])
    op.create_index("idx_audit_time", "audit_events", ["timestamp_utc"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("materialized_assignments")
    op.drop_table("plan_versions")
    op.drop_table("solver_jobs")
    op.drop_table("resource_calendars")
    op.drop_table("train_occupations")
    op.drop_table("snapshot_task_memberships")
    op.drop_table("snapshots")
    op.drop_table("tasks")
    op.drop_table("track_segments")
    op.drop_table("stations")
    op.drop_table("corridors")
