"""
GripWise Backend — FastAPI application entry point.
"""
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import engine, Base
from backend.middleware.logging import LoggingMiddleware
from backend.api import auth, vehicles, inspections, health

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("gripwise.startup", env=settings.ENVIRONMENT)
    yield
    log.info("gripwise.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="GripWise API",
        description="AI-assisted tyre-safety and rider-trust platform",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    from backend.api import auth, vehicles, inspections, health, mechanic, consent

    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
    app.include_router(inspections.router, prefix="/api/inspections", tags=["inspections"])
    app.include_router(mechanic.router, prefix="/api/mechanic", tags=["mechanic"])
    app.include_router(consent.router, prefix="/api/consent", tags=["consent"])

    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc):
        log.error("unhandled_exception", exc=str(exc), path=str(request.url))
        return JSONResponse(
            status_code=500,
            content={"success": False, "data": None, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
        )

    return app


app = create_app()
