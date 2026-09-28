"""
Database schema upgrade script for Phase 10: Durable Solve Jobs.
Safely adds missing columns to solver_jobs and plan_versions tables for both SQLite and PostgreSQL.
"""
import asyncio
from sqlalchemy import text
from app.db.session import async_engine
from app.core.logging import logger


async def migrate_phase10():
    async with async_engine.begin() as conn:
        dialect = conn.dialect.name
        logger.info(f"Running Phase 10 schema check on dialect '{dialect}'")

        # 1. solver_jobs table
        existing_cols = []
        if dialect == "sqlite":
            res = await conn.execute(text("PRAGMA table_info(solver_jobs);"))
            existing_cols = [r[1] for r in res.fetchall()]
        else:
            res = await conn.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'solver_jobs';")
            )
            existing_cols = [r[0] for r in res.fetchall()]

        cols_to_add = [
            ("corridor_code", "VARCHAR(10) DEFAULT 'VKC' NOT NULL"),
            ("fencing_token", "INTEGER DEFAULT 0 NOT NULL"),
            ("attempt_count", "INTEGER DEFAULT 0 NOT NULL"),
            ("max_attempts", "INTEGER DEFAULT 3 NOT NULL"),
            ("version", "INTEGER DEFAULT 1 NOT NULL"),
            ("idempotency_key", "VARCHAR(128)"),
            ("request_fingerprint", "VARCHAR(64)"),
            ("created_by_user", "VARCHAR(50) DEFAULT 'planner'"),
            ("user_role", "VARCHAR(50) DEFAULT 'PLANNER'"),
            ("solve_parameters", "JSON DEFAULT '{}' NOT NULL"),
            ("result_summary", "JSON"),
            ("is_snapshot_obsolete", "BOOLEAN DEFAULT FALSE NOT NULL"),
        ]

        for col_name, col_def in cols_to_add:
            if col_name not in existing_cols:
                logger.info(f"Adding column '{col_name}' to solver_jobs")
                await conn.execute(text(f"ALTER TABLE solver_jobs ADD COLUMN {col_name} {col_def};"))

        # 2. plan_versions table
        existing_plan_cols = []
        if dialect == "sqlite":
            res = await conn.execute(text("PRAGMA table_info(plan_versions);"))
            existing_plan_cols = [r[1] for r in res.fetchall()]
        else:
            res = await conn.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'plan_versions';")
            )
            existing_plan_cols = [r[0] for r in res.fetchall()]

        plan_cols_to_add = [
            ("corridor_code", "VARCHAR(10) DEFAULT 'VKC' NOT NULL"),
            ("solver_status", "VARCHAR(20)"),
            ("checker_verdict", "VARCHAR(30)"),
            ("reconciliation_cases", "JSON DEFAULT '[]' NOT NULL"),
        ]

        for col_name, col_def in plan_cols_to_add:
            if col_name not in existing_plan_cols:
                logger.info(f"Adding column '{col_name}' to plan_versions")
                await conn.execute(text(f"ALTER TABLE plan_versions ADD COLUMN {col_name} {col_def};"))

    print("Phase 10 migration complete.")


if __name__ == "__main__":
    asyncio.run(migrate_phase10())
