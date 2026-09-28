"""
Tests for ML urgency classifier, demand forecaster, and API endpoints.
SIH26027: AI/ML-Powered Maintenance Allocation & Demand Forecasting.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.engine.ml_urgency_classifier import (
    DefectUrgencyClassifier,
    DemandForecaster,
    DefectFeatures,
)


def test_classifier_unit_tier1():
    classifier = DefectUrgencyClassifier()
    features = DefectFeatures(
        defect_age_days=45.0,
        defect_severity_score=0.95,
        traffic_density_tpd=45.0,
        last_maintenance_days=35.0,
        weather_risk_score=0.4,
        speed_restriction_active=True,
        department_code=0,
        work_type="MANDATORY",
        has_usfd_flaw=True,
        is_overdue=True,
    )
    result = classifier.predict(features)
    assert result.predicted_tier == "TIER_1_MANDATORY"
    assert result.confidence >= 0.7
    assert result.prediction_hash is not None
    assert len(result.prediction_hash) >= 16


def test_classifier_unit_tier3():
    classifier = DefectUrgencyClassifier()
    features = DefectFeatures(
        defect_age_days=5.0,
        defect_severity_score=0.2,
        traffic_density_tpd=30.0,
        last_maintenance_days=10.0,
        weather_risk_score=0.1,
        speed_restriction_active=False,
        department_code=1,
        work_type="PREVENTIVE",
        has_usfd_flaw=False,
        is_overdue=False,
    )
    result = classifier.predict(features)
    assert result.predicted_tier == "TIER_3_CYCLIC"
    assert result.confidence >= 0.55


def test_demand_forecaster_unit():
    forecaster = DemandForecaster()
    forecasts = forecaster.forecast_goods_trains(horizon_days=7)
    assert len(forecasts) == 7
    for f in forecasts:
        assert 20 <= f["predicted_goods_trains"] <= 65
        assert f["confidence_lower"] <= f["predicted_goods_trains"] <= f["confidence_upper"]


def test_maintenance_windows_unit():
    forecaster = DemandForecaster()
    windows = forecaster.forecast_maintenance_windows(corridor_code="VKC", horizon_days=5)
    assert len(windows) == 5
    for w in windows:
        assert w["corridor_code"] == "VKC"
        assert w["available_minutes"] >= 150
        assert 0.0 <= w["feasibility_score"] <= 1.0


@pytest.mark.anyio
async def test_ml_model_info_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ml/model-info")
        assert response.status_code == 200
        data = response.json()
        assert "urgency_classifier" in data
        assert "demand_forecaster" in data
        assert data["urgency_classifier"]["validation_accuracy"] > 0.8


@pytest.mark.anyio
async def test_ml_predict_urgency_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "defect_age_days": 40.0,
            "defect_severity_score": 0.9,
            "traffic_density_tpd": 42.0,
            "last_maintenance_days": 30.0,
            "weather_risk_score": 0.3,
            "speed_restriction_active": True,
            "department_code": 0,
            "work_type": "MANDATORY",
            "has_usfd_flaw": True,
            "is_overdue": True,
        }
        response = await client.post("/api/v1/ml/predict-urgency", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_tier"] == "TIER_1_MANDATORY"
        assert data["confidence"] >= 0.7


@pytest.mark.anyio
async def test_ml_forecast_goods_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"corridor_code": "VKC", "horizon_days": 7}
        response = await client.post("/api/v1/ml/forecast/goods-trains", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["corridor_code"] == "VKC"
        assert len(data["forecasts"]) == 7
