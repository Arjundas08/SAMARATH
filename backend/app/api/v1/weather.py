"""
Weather API for SAMARATH.
Provides Open-Meteo live corridor weather with provenance tags.
All safety thresholds are explicitly identified as DEMONSTRATION_CONFIGURATION.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.engine.weather_engine import weather_engine, CORRIDOR_COORDINATES, DEMO_WEATHER_THRESHOLDS

router = APIRouter(prefix="/weather", tags=["Live Weather & Risk"])


class TaskWeatherEvaluationRequest(BaseModel):
    task_type: str
    corridor_code: str = "VKC"
    custom_wind_gusts_kmh: Optional[float] = None
    custom_precipitation_mm: Optional[float] = None


@router.get("/corridors")
async def list_weather_corridors():
    """Lists supported corridor coordinates for weather tracking."""
    return {
        "corridors": CORRIDOR_COORDINATES,
        "provider": "Open-Meteo REST API",
        "threshold_governance": DEMO_WEATHER_THRESHOLDS["LABEL"],
    }


@router.get("/corridor/{corridor_code}")
async def get_corridor_weather(
    corridor_code: str = "VKC",
    db: AsyncSession = Depends(get_db),
):
    """
    Fetches live weather from Open-Meteo for corridor coordinates.
    Stores and returns observation with full data provenance.
    """
    return await weather_engine.fetch_and_store_corridor_weather(db, corridor_code.upper())


@router.post("/evaluate-task")
async def evaluate_task_weather(
    request: TaskWeatherEvaluationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluates weather risk for a maintenance task against prototype railway limits.
    """
    obs = await weather_engine.fetch_and_store_corridor_weather(db, request.corridor_code.upper())
    gusts = request.custom_wind_gusts_kmh if request.custom_wind_gusts_kmh is not None else obs.get("wind_gusts_kmh")
    rain = request.custom_precipitation_mm if request.custom_precipitation_mm is not None else obs.get("precipitation_mm")

    advisories = weather_engine.evaluate_task_weather_risk(request.task_type, gusts, rain)
    return {
        "corridor_code": request.corridor_code,
        "task_type": request.task_type,
        "evaluated_weather": {
            "wind_gusts_kmh": gusts,
            "precipitation_mm": rain,
            "provenance": obs.get("source"),
        },
        "advisories": advisories,
        "threshold_classification": DEMO_WEATHER_THRESHOLDS["LABEL"],
        "advisory_count": len(advisories),
    }
