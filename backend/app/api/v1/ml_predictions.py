"""
ML Prediction and Demand Forecasting API Endpoints.
SIH26027: AI/ML-powered maintenance urgency classification and goods train demand forecasting.
"""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.engine.ml_urgency_classifier import (
    DefectUrgencyClassifier,
    DemandForecaster,
    DefectFeatures,
)

router = APIRouter(prefix="/ml", tags=["AI/ML Predictions"])

# Singleton instances
_classifier = DefectUrgencyClassifier()
_forecaster = DemandForecaster()


class PredictUrgencyRequest(BaseModel):
    """Request body for single defect urgency prediction."""
    defect_age_days: float = Field(default=30.0, ge=0, description="Days since defect first reported")
    defect_severity_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Normalized severity from source system")
    traffic_density_tpd: float = Field(default=40.0, ge=0, description="Trains per day on affected track")
    last_maintenance_days: float = Field(default=30.0, ge=0, description="Days since last maintenance")
    weather_risk_score: float = Field(default=0.3, ge=0.0, le=1.0, description="Monsoon/thermal risk factor")
    speed_restriction_active: bool = Field(default=False, description="Whether TSR is currently active")
    department_code: int = Field(default=0, ge=0, le=2, description="ENG=0, S&T=1, TRD=2")
    work_type: str = Field(default="PREVENTIVE", description="Type of maintenance work")
    has_usfd_flaw: bool = Field(default=False, description="USFD ultrasonic rail flaw detected")
    is_overdue: bool = Field(default=False, description="Flagged as overdue by source system")


class PredictUrgencyResponse(BaseModel):
    predicted_tier: str
    confidence: float
    tier_probabilities: dict
    feature_importance: dict
    explanation: str
    model_version: str
    prediction_hash: str


class BatchPredictRequest(BaseModel):
    defects: List[PredictUrgencyRequest]


class ForecastRequest(BaseModel):
    corridor_code: str = Field(default="VKC", description="Corridor code")
    horizon_days: int = Field(default=7, ge=1, le=30, description="Days to forecast")
    historical_goods_counts: Optional[List[int]] = Field(
        default=None, description="Historical daily goods train counts (last 30+ days)"
    )


@router.post("/predict-urgency", response_model=PredictUrgencyResponse)
async def predict_urgency(request: PredictUrgencyRequest):
    """
    Predicts maintenance criticality tier for a single defect using the
    trained Gradient-Boosted Tree classifier (SAMARATH-GBT-v2.1).

    Returns tier prediction with confidence, probability distribution,
    feature importance (SHAP-approximated), and human-readable explanation.
    """
    features = DefectFeatures(
        defect_age_days=request.defect_age_days,
        defect_severity_score=request.defect_severity_score,
        traffic_density_tpd=request.traffic_density_tpd,
        last_maintenance_days=request.last_maintenance_days,
        weather_risk_score=request.weather_risk_score,
        speed_restriction_active=request.speed_restriction_active,
        department_code=request.department_code,
        work_type=request.work_type,
        has_usfd_flaw=request.has_usfd_flaw,
        is_overdue=request.is_overdue,
    )
    prediction = _classifier.predict(features)
    return PredictUrgencyResponse(
        predicted_tier=prediction.predicted_tier,
        confidence=prediction.confidence,
        tier_probabilities=prediction.tier_probabilities,
        feature_importance=prediction.feature_importance,
        explanation=prediction.explanation,
        model_version=prediction.model_version,
        prediction_hash=prediction.prediction_hash,
    )


@router.post("/predict-urgency/batch")
async def predict_urgency_batch(request: BatchPredictRequest):
    """
    Batch urgency prediction for multiple defects.
    Returns array of predictions matching input order.
    """
    results = []
    for defect in request.defects:
        features = DefectFeatures(
            defect_age_days=defect.defect_age_days,
            defect_severity_score=defect.defect_severity_score,
            traffic_density_tpd=defect.traffic_density_tpd,
            last_maintenance_days=defect.last_maintenance_days,
            weather_risk_score=defect.weather_risk_score,
            speed_restriction_active=defect.speed_restriction_active,
            department_code=defect.department_code,
            work_type=defect.work_type,
            has_usfd_flaw=defect.has_usfd_flaw,
            is_overdue=defect.is_overdue,
        )
        prediction = _classifier.predict(features)
        results.append({
            "predicted_tier": prediction.predicted_tier,
            "confidence": prediction.confidence,
            "tier_probabilities": prediction.tier_probabilities,
            "explanation": prediction.explanation,
            "prediction_hash": prediction.prediction_hash,
        })
    return {"predictions": results, "count": len(results), "model_version": _classifier.MODEL_VERSION}


@router.post("/forecast/goods-trains")
async def forecast_goods_trains(request: ForecastRequest):
    """
    Forecasts daily goods train counts for the specified corridor and horizon.
    Uses EWMA with seasonal decomposition trained on COA historical WTT data.
    """
    forecasts = _forecaster.forecast_goods_trains(
        historical_counts=request.historical_goods_counts or [],
        horizon_days=request.horizon_days,
    )
    return {
        "corridor_code": request.corridor_code,
        "horizon_days": request.horizon_days,
        "forecasts": forecasts,
        "model_info": _forecaster.get_model_info(),
    }


@router.post("/forecast/maintenance-windows")
async def forecast_maintenance_windows(request: ForecastRequest):
    """
    Predicts optimal maintenance corridor windows for each day in the horizon.
    Integrates goods train demand forecast with WTT coaching fixed slots.
    """
    windows = _forecaster.forecast_maintenance_windows(
        corridor_code=request.corridor_code,
        horizon_days=request.horizon_days,
        train_counts=request.historical_goods_counts,
    )
    return {
        "corridor_code": request.corridor_code,
        "horizon_days": request.horizon_days,
        "windows": windows,
        "model_info": _forecaster.get_model_info(),
    }


@router.get("/model-info")
async def get_model_info():
    """Returns metadata about all deployed ML models for audit and governance."""
    return {
        "urgency_classifier": {
            "model_name": "Defect Urgency Classifier",
            "version": _classifier.MODEL_VERSION,
            "algorithm": "Gradient-Boosted Decision Tree (3-tree ensemble)",
            "training_samples": _classifier.TRAINING_SAMPLES,
            "validation_accuracy": _classifier.VALIDATION_ACCURACY,
            "training_date": _classifier.TRAINING_DATE,
            "features": [
                "defect_age_days", "defect_severity_score", "traffic_density_tpd",
                "last_maintenance_days", "weather_risk_score", "speed_restriction_active",
                "department_code", "has_usfd_flaw", "is_overdue",
            ],
            "output_classes": ["TIER_1_MANDATORY", "TIER_2_SPEED_RESTRICTION", "TIER_3_CYCLIC"],
        },
        "demand_forecaster": _forecaster.get_model_info(),
    }
