"""
Health check endpoints distinguishing process reachability from database usability.
"""
from fastapi import APIRouter
from datetime import datetime

from app.schemas.common import HealthResponse, DatabaseHealth
from app.db.session import check_db_health

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def get_system_health():
    """
    Health check endpoint.
    Distinguishes a reachable FastAPI process from a functioning database connection.
    """
    connected, engine_name, latency_ms, error = await check_db_health()

    status = "healthy" if connected else "degraded"

    return HealthResponse(
        status=status,
        app_name="SAMARATH",
        version="0.1.0",
        process="reachable",
        database=DatabaseHealth(
            connected=connected,
            engine=engine_name,
            latency_ms=latency_ms,
            error=error,
        ),
        timestamp_utc=datetime.utcnow(),
    )
