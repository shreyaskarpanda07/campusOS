"""
Health check endpoint.

Returns the application status, database connectivity, and version.
This is the first endpoint — used to verify the backend is running
and can reach PostgreSQL.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Check application health and database connectivity.

    Returns:
        200 with status, database connection state, and version.
    """
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "data": {
            "status": "healthy",
            "database": db_status,
            "version": settings.VERSION,
        },
        "error": None,
    }
