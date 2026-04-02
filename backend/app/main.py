"""FastAPI application entry point.

Main application setup including middleware, routes, and health check.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.tracing import TracingMiddleware

# Setup logging
setup_logging(level=settings.log_level)
logger = get_logger(__name__)

# Initialize Sentry if DSN is configured
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastAPIIntegration
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastAPIIntegration()],
        environment=settings.DEPLOYMENT,
    )
    logger.info("Sentry initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Quant backend starting up...")
    yield
    # Shutdown
    logger.info("Quant backend shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Quant Trading System API",
    description="Backend API for quantitative trading system",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tracing middleware
app.add_middleware(TracingMiddleware)

# Include API routes
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "debug": settings.DEBUG,
    }
