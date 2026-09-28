"""
Main API Router for SAMARATH.
"""
from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.snapshots import router as snapshots_router
from app.api.v1.rbac_demo import router as rbac_router
from app.api.v1.gateway import router as gateway_router
from app.api.v1.rules import router as rules_router
from app.api.v1.readiness import router as readiness_router
from app.api.v1.packages import router as packages_router
from app.api.v1.planning import router as planning_router
from app.api.v1.checker import router as checker_router
from app.api.v1.diagnostics import router as diagnostics_router
from app.api.v1.disruptions import router as disruptions_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.approval import router as approval_router
from app.api.v1.execution import router as execution_router
from app.api.v1.resilience import router as resilience_router
from app.api.v1.ml_predictions import router as ml_router
from app.api.v1.field import router as field_router
from app.api.v1.weather import router as weather_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(tasks_router)
api_router.include_router(snapshots_router)
api_router.include_router(rbac_router)
api_router.include_router(gateway_router)
api_router.include_router(rules_router)
api_router.include_router(readiness_router)
api_router.include_router(packages_router)
api_router.include_router(planning_router)
api_router.include_router(checker_router)
api_router.include_router(diagnostics_router)
api_router.include_router(disruptions_router)
api_router.include_router(evaluation_router)
api_router.include_router(approval_router)
api_router.include_router(execution_router)
api_router.include_router(resilience_router)
api_router.include_router(ml_router)
api_router.include_router(field_router)
api_router.include_router(weather_router)

