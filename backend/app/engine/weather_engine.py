"""
Weather Engine for SAMARATH.
Integrates live forecasts from Open-Meteo API.
All prototype thresholds are explicitly tagged as DEMONSTRATION_CONFIGURATION.
Weather provides risk advisories for human review—it never automatically certifies work as safe.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.logging import logger
from app.db.models import WeatherObservationModel

CORRIDOR_COORDINATES = {
    "VKC": {"name": "Vadodara-Kazipet Trunk", "lat": 22.3072, "lon": 73.1812},
    "DLI": {"name": "Delhi Division", "lat": 28.6139, "lon": 77.2090},
    "PRYJ": {"name": "Prayagraj Division", "lat": 25.4358, "lon": 81.8463},
    "HWH": {"name": "Howrah Division", "lat": 22.5850, "lon": 88.3426},
}

# DEMONSTRATION ONLY: Prototype advisories subject to railway specialist verification
DEMO_WEATHER_THRESHOLDS = {
    "OHE_WIND_GUST_LIMIT_KMH": 45.0,
    "TRACK_BALLAST_RAIN_LIMIT_MM": 15.0,
    "LABEL": "DEMONSTRATION_CONFIGURATION",
}


class WeatherEngine:
    def __init__(self, timeout_seconds: float = 6.0):
        self.timeout_seconds = timeout_seconds

    async def fetch_and_store_corridor_weather(
        self,
        db: AsyncSession,
        corridor_code: str = "VKC",
    ) -> Dict[str, Any]:
        """
        Fetches live hourly forecast from Open-Meteo for corridor coordinates.
        Stores the observation with provenance metadata.
        Falls back to cached observations if external call fails.
        """
        coord = CORRIDOR_COORDINATES.get(corridor_code, CORRIDOR_COORDINATES["VKC"])
        now_utc = datetime.now(timezone.utc)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coord["lat"],
            "longitude": coord["lon"],
            "hourly": "temperature_2m,precipitation,wind_speed_10m,wind_gusts_10m",
            "timezone": "UTC",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    hourly = data.get("hourly", {})
                    times = hourly.get("time", [])
                    temps = hourly.get("temperature_2m", [])
                    precips = hourly.get("precipitation", [])
                    winds = hourly.get("wind_speed_10m", [])
                    gusts = hourly.get("wind_gusts_10m", [])

                    # Find current hour index
                    current_idx = 0
                    if times:
                        current_iso = now_utc.strftime("%Y-%m-%dT%H:00")
                        for idx, t_str in enumerate(times):
                            if t_str >= current_iso:
                                current_idx = idx
                                break

                    temp_c = temps[current_idx] if current_idx < len(temps) else None
                    precip_mm = precips[current_idx] if current_idx < len(precips) else 0.0
                    wind_kmh = winds[current_idx] if current_idx < len(winds) else 0.0
                    gust_kmh = gusts[current_idx] if current_idx < len(gusts) else 0.0

                    obs = WeatherObservationModel(
                        corridor_code=corridor_code,
                        latitude=coord["lat"],
                        longitude=coord["lon"],
                        source="LIVE_EXTERNAL",
                        retrieval_timestamp_utc=now_utc,
                        forecast_timestamp_utc=now_utc,
                        temperature_c=temp_c,
                        precipitation_mm=precip_mm,
                        wind_speed_kmh=wind_kmh,
                        wind_gusts_kmh=gust_kmh,
                        status="ACTIVE",
                        raw_payload={
                            "hourly_sample": {
                                "times": times[:24],
                                "precip": precips[:24],
                                "wind_gusts": gusts[:24],
                            },
                            "provider": "Open-Meteo",
                            "license": "Non-commercial free tier",
                        },
                    )
                    db.add(obs)
                    await db.commit()
                    await db.refresh(obs)

                    logger.info(
                        f"Stored LIVE_EXTERNAL weather for {corridor_code}: "
                        f"{temp_c}°C, rain {precip_mm}mm, wind {wind_kmh}km/h (gusts {gust_kmh}km/h)"
                    )
                    return self._format_observation(obs, is_live=True)

        except Exception as e:
            logger.warning(f"Live Open-Meteo request failed for {corridor_code}: {e}. Checking cache.")

        # Fallback to latest stored observation
        return await self._get_cached_or_fallback(db, corridor_code, coord, now_utc)

    async def _get_cached_or_fallback(
        self,
        db: AsyncSession,
        corridor_code: str,
        coord: Dict[str, Any],
        now_utc: datetime,
    ) -> Dict[str, Any]:
        stmt = (
            select(WeatherObservationModel)
            .where(WeatherObservationModel.corridor_code == corridor_code)
            .order_by(desc(WeatherObservationModel.retrieval_timestamp_utc))
            .limit(1)
        )
        res = await db.execute(stmt)
        cached = res.scalar_one_or_none()

        if cached:
            return self._format_observation(cached, is_live=False)

        # Baseline fallback with UNAVAILABLE provenance
        return {
            "observation_id": "fallback-none",
            "corridor_code": corridor_code,
            "corridor_name": coord["name"],
            "coordinates": {"lat": coord["lat"], "lon": coord["lon"]},
            "source": "UNAVAILABLE",
            "status": "UNAVAILABLE",
            "retrieval_timestamp_utc": now_utc.isoformat(),
            "forecast_timestamp_utc": now_utc.isoformat(),
            "temperature_c": 28.0,
            "precipitation_mm": 0.0,
            "wind_speed_kmh": 12.0,
            "wind_gusts_kmh": 18.0,
            "advisories": [],
            "provenance_note": "External API unreachable and no cache found. Synthetic demonstration fallback.",
        }

    def evaluate_task_weather_risk(
        self,
        task_type: str,
        wind_gusts_kmh: Optional[float],
        precipitation_mm: Optional[float],
    ) -> List[Dict[str, Any]]:
        """
        Evaluates task-specific weather advisory against prototype railway limits.
        Explicitly marked as DEMONSTRATION_CONFIGURATION.
        """
        advisories = []
        gusts = wind_gusts_kmh or 0.0
        rain = precipitation_mm or 0.0

        if "OHE" in task_type.upper() or "TRACTION" in task_type.upper():
            if gusts > DEMO_WEATHER_THRESHOLDS["OHE_WIND_GUST_LIMIT_KMH"]:
                advisories.append({
                    "advisory_type": "HIGH_WIND_GUST_RISK",
                    "severity": "WARNING",
                    "threshold_rule": f"Wind gusts > {DEMO_WEATHER_THRESHOLDS['OHE_WIND_GUST_LIMIT_KMH']} km/h",
                    "measured_value": f"{gusts:.1f} km/h",
                    "provenance": DEMO_WEATHER_THRESHOLDS["LABEL"],
                    "message": "Strong wind gusts forecast. Ladder/tower wagon work requires SSE(TRD) clearance.",
                    "action_required": "HUMAN_SUPERVISOR_REVIEW",
                })

        if "BALLAST" in task_type.upper() or "TAMPING" in task_type.upper() or "TRACK" in task_type.upper():
            if rain > DEMO_WEATHER_THRESHOLDS["TRACK_BALLAST_RAIN_LIMIT_MM"]:
                advisories.append({
                    "advisory_type": "HEAVY_PRECIPITATION_RISK",
                    "severity": "WARNING",
                    "threshold_rule": f"Rainfall > {DEMO_WEATHER_THRESHOLDS['TRACK_BALLAST_RAIN_LIMIT_MM']} mm/h",
                    "measured_value": f"{rain:.1f} mm/h",
                    "provenance": DEMO_WEATHER_THRESHOLDS["LABEL"],
                    "message": "Heavy precipitation forecast. Mechanized deep screening risk (ballast slurry).",
                    "action_required": "HUMAN_SUPERVISOR_REVIEW",
                })

        return advisories

    def _format_observation(self, obs: WeatherObservationModel, is_live: bool) -> Dict[str, Any]:
        coord = CORRIDOR_COORDINATES.get(obs.corridor_code, CORRIDOR_COORDINATES["VKC"])
        ohe_advisories = self.evaluate_task_weather_risk("OHE", obs.wind_gusts_kmh, obs.precipitation_mm)
        track_advisories = self.evaluate_task_weather_risk("TRACK", obs.wind_gusts_kmh, obs.precipitation_mm)
        all_advisories = ohe_advisories + track_advisories

        return {
            "observation_id": obs.observation_id,
            "corridor_code": obs.corridor_code,
            "corridor_name": coord["name"],
            "coordinates": {"lat": obs.latitude, "lon": obs.longitude},
            "source": obs.source if is_live else "CACHED",
            "status": obs.status,
            "retrieval_timestamp_utc": obs.retrieval_timestamp_utc.isoformat(),
            "forecast_timestamp_utc": obs.forecast_timestamp_utc.isoformat(),
            "temperature_c": obs.temperature_c,
            "precipitation_mm": obs.precipitation_mm,
            "wind_speed_kmh": obs.wind_speed_kmh,
            "wind_gusts_kmh": obs.wind_gusts_kmh,
            "advisories": all_advisories,
            "provenance_note": "LIVE_EXTERNAL from Open-Meteo" if is_live else "CACHED from earlier Open-Meteo retrieval",
            "threshold_classification": DEMO_WEATHER_THRESHOLDS["LABEL"],
        }


weather_engine = WeatherEngine()
