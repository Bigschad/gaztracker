"""
Main Application Module

FastAPI application entry point for GazTracker.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time

from app.config import settings
from app.database import init_databases, close_databases
from app.utils.exceptions import GazTrackerException, to_http_exception


# Configure logging
logger = logging.getLogger(__name__)


# =============================================================================
# Application Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENVIRONMENT}")

    # Initialize databases
    await init_databases()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Close database connections
    await close_databases()

    logger.info("Application shutdown complete")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Système de gestion et suivi des palettes de bouteilles de gaz",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False,
)


# =============================================================================
# Middleware
# =============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(GazTrackerException)
async def gaztracker_exception_handler(request: Request, exc: GazTrackerException):
    """Handle custom GazTracker exceptions."""
    logger.error(f"GazTracker exception: {exc.message}", extra={"details": exc.details})
    http_exc = to_http_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    # Convert any bytes to strings for JSON serialization
    for error in errors:
        if 'ctx' in error:
            for key, value in error['ctx'].items():
                if isinstance(value, bytes):
                    error['ctx'][key] = value.decode('utf-8', errors='replace')
        if 'input' in error and isinstance(error['input'], bytes):
            error['input'] = error['input'].decode('utf-8', errors='replace')

    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
            "details": {"error": str(exc)} if settings.DEBUG else {}
        }
    )


# =============================================================================
# Root Endpoints
# =============================================================================

@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    response_description="API information"
)
async def root():
    """
    Get API root information.

    Returns basic information about the API.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENVIRONMENT,
        "docs": "/docs",
        "status": "healthy"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    response_description="Health status"
)
async def health_check():
    """
    Health check endpoint.

    Returns the health status of the application and its dependencies.
    """
    # TODO: In future phases, add checks for database and Redis connectivity
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENVIRONMENT,
        "services": {
            "api": "healthy",
            # "database": "healthy",  # To be implemented in Phase 2
            # "redis": "healthy",      # To be implemented in Phase 2
        }
    }


# =============================================================================
# API Router Includes
# =============================================================================

# Phase 2: Authentication routes
from app.routes import auth
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

# Phase 2: User management routes
from app.routes import users
app.include_router(users.router, prefix=settings.API_V1_PREFIX)

# Phase 3: RFID Tag routes
from app.routes import rfid_tags
app.include_router(rfid_tags.router, prefix=f"{settings.API_V1_PREFIX}/rfid-tags", tags=["RFID Tags"])

# Phase 3: Palette routes
from app.routes import palettes
app.include_router(palettes.router, prefix=f"{settings.API_V1_PREFIX}/palettes", tags=["Palettes"])

# Phase 4: Expedition routes
from app.routes import expeditions
app.include_router(expeditions.router, prefix=f"{settings.API_V1_PREFIX}/expeditions", tags=["Expeditions"])

# Phase 5: Notification routes
from app.routes import notifications
app.include_router(notifications.router, prefix=f"{settings.API_V1_PREFIX}/notifications", tags=["Notifications"])

# Phase 6: Reports and Statistics routes
from app.routes import reports
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
