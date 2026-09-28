"""
Database session management and connectivity verification.
Distinguishes reachable process from usable database.
Supports zero-configuration local SQLite fallback when PostgreSQL daemon is offline.
"""
import time
import socket
from typing import AsyncGenerator, Tuple, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.config import settings
from app.core.logging import logger

db_url = settings.DATABASE_URL
sync_db_url = settings.SYNC_DATABASE_URL


def is_port_reachable(host: str = "localhost", port: int = 5432, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# If configured for postgres, check if port is actually listening
if "postgres" in db_url.lower():
    if not is_port_reachable("localhost", 5432, timeout=0.3):
        logger.warning("PostgreSQL daemon not detected on localhost:5432. Activating local SQLite engine.")
        db_url = "sqlite+aiosqlite:///./samarath.db"

async_engine = create_async_engine(
    db_url,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_health() -> Tuple[bool, str, Optional[float], Optional[str]]:
    """
    Executes a lightweight query (SELECT 1) to verify database responsiveness.
    Returns: (connected: bool, engine_type: str, latency_ms: Optional[float], error: Optional[str])
    """
    engine_type = "postgresql" if "postgres" in db_url else "sqlite"
    start_time = time.perf_counter()
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start_time) * 1000.0
        return True, engine_type, round(latency, 2), None
    except Exception as exc:
        latency = (time.perf_counter() - start_time) * 1000.0
        return False, engine_type, round(latency, 2), str(exc)
