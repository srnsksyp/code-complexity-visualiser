from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Health and database connectivity check")
def health_check(db: Session = Depends(get_db)):
    db_connected = False
    db_type = "unknown"
    error_msg = None

    try:
        db.execute(text("SELECT 1"))
        db_connected = True
        if "postgresql" in settings.DATABASE_URL:
            db_type = "PostgreSQL (Supabase)"
        elif "sqlite" in settings.DATABASE_URL:
            db_type = "SQLite (Local fallback)"
        else:
            db_type = "Relational DB"
    except Exception as e:
        error_msg = str(e)

    return {
        "status": "healthy" if db_connected else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": {
            "connected": db_connected,
            "type": db_type,
            "error": error_msg
        }
    }
