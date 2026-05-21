"""GET /health — liveness and readiness probe."""
import time

from fastapi import APIRouter

from app.core.config import settings
from app.core.database import check_database_connectivity
from app.models.api_models import HealthResponse
from app.services import cache

router = APIRouter(tags=["Health"])
_START = time.time()


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    Returns service status, version, DB connectivity, and cache stats.
    Use as liveness/readiness probe in Kubernetes or Docker healthcheck.
    """
    db_ok = check_database_connectivity()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        database="connected" if db_ok else "unreachable",
        uptime_seconds=round(time.time() - _START, 1),
    )
