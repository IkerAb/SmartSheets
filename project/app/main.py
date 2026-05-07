"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import check_database_connectivity
from app.core.logging import configure_logging, get_logger
from app.routes import api_router

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event() -> None:
    """Log startup metadata for traceability."""
    logger.info(
        "Application startup complete",
        extra={"app": settings.app_name, "version": settings.app_version},
    )
    if check_database_connectivity():
        logger.info("PostgreSQL connectivity check succeeded")
    else:
        logger.warning("PostgreSQL connectivity check failed during startup")
