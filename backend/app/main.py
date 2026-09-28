"""
SAMARATH - Main FastAPI Application Entrypoint.
SIH26027: AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings
from app.core.logging import logger
from app.schemas.common import ProblemDetails, InvalidParam
from app.api.router import api_router

app = FastAPI(
    title="SAMARATH - Railway Block Planning API",
    description="System for Automated Maintenance Allocation, Rolling Availability, and Track Harmony (SIH26027)",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    RFC 7807 compliant validation error handler.
    """
    invalid_params = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
        invalid_params.append(
            InvalidParam(name=field_path, reason=err.get("msg", "Invalid value"))
        )

    problem = ProblemDetails(
        type="https://samarath.railnet.gov.in/errors/validation-error",
        title="Request Payload Validation Error",
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="One or more fields in the request failed validation checks.",
        instance=str(request.url.path),
        error_code="ERR_VALIDATION_FAILED",
        invalid_params=invalid_params,
        timestamp=datetime.utcnow(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=problem.model_dump(mode="json"),
        headers={"Content-Type": "application/problem+json"},
    )


@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode on port {settings.APP_PORT}")
    try:
        from app.db.session import async_engine, async_session_factory
        from app.db.base import Base
        import app.db.models  # Register all model classes
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema verified / initialized.")

        # Auto-seed if database is empty
        try:
            from sqlalchemy import select
            from app.db.models import Corridor
            from app.gateway.service import seed_vayu_kosh_corridor
            async with async_session_factory() as session:
                res = await session.execute(select(Corridor))
                if not res.scalars().first():
                    logger.info("Empty database detected. Auto-seeding Vadodara-Kazipet corridor...")
                    await seed_vayu_kosh_corridor(session)
                    logger.info("Auto-seeding completed.")
        except Exception as seed_err:
            logger.warning(f"Auto-seed skipped or encountered error: {seed_err}")
    except Exception as e:
        logger.warning(f"Could not auto-initialize DB schema on startup: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info(f"Shutting down {settings.APP_NAME}")


# Include routers
app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "system": "SAMARATH",
        "description": "AI-Powered Automatic Block Planning Engine",
        "status": "OPERATIONAL",
        "provenance_mode": "TEST",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
