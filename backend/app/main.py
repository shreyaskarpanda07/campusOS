"""
CampusOS Backend — FastAPI Application Entry Point

This is the main application factory. It wires together:
- CORS middleware
- Standard API exception handlers
- All module routers
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers import auth, health


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Personalized opportunity intelligence platform for university students",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ─────────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Standard JSON Error Handlers ─────────────────────────────────
    @application.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            error_payload = exc.detail
        else:
            error_payload = {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
            }
        return JSONResponse(
            status_code=exc.status_code,
            content={"data": None, "error": error_payload},
            headers=exc.headers,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = exc.errors()
        messages = [
            f"{e.get('loc', ['field'])[-1]}: {e.get('msg', 'invalid value')}"
            for e in errors
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "; ".join(messages),
                },
            },
        )

    # ── Routers ──────────────────────────────────────────────────────
    application.include_router(health.router, prefix="/api", tags=["health"])
    application.include_router(auth.router, prefix="/api", tags=["auth"])

    return application


app = create_app()
