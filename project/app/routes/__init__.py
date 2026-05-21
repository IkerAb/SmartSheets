"""Route registration for API endpoints."""

from fastapi import APIRouter

from app.routes.upload import router as upload_router
from app.routes.insights import router as insights_router
from app.routes.forecast import router as forecast_router
from app.routes.simulate import router as simulate_router
from app.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(upload_router)
api_router.include_router(insights_router)
api_router.include_router(forecast_router)
api_router.include_router(simulate_router)
api_router.include_router(health_router)
