"""GET /forecast — time-series sales forecast."""
from fastapi import APIRouter, HTTPException, Query

from app.models.api_models import ForecastResponse
from app.models.dataset_models import DatasetStatus
from app.repositories.dataset_repository import PostgresDatasetRepository
from app.services.forecasting import ForecastingService
from app.services import cache
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter(tags=["Forecast"])
logger = get_logger(__name__)

forecast_svc = ForecastingService()


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    dataset_id: str = Query(...),
    horizon: int = Query(default=settings.default_horizon, ge=1, le=365),
    product: str | None = Query(default=None),
    confidence: float = Query(default=settings.default_confidence, ge=0.5, le=0.99),
    aggregation: str = Query(default="day", pattern="^(day|month)$"),
):
    """
    Generate a sales forecast.

    - Uses **ETS** (Exponential Smoothing) when ≥30 observations are available.
    - Falls back to **naive** mean forecast for sparse series.
    - Supports `day` or `month` aggregation.
    - Returns prediction + confidence interval [lower, upper].
    """
    repo = PostgresDatasetRepository()
    meta = repo.get_metadata(dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    if meta.status != DatasetStatus.CLEANED:
        raise HTTPException(status_code=409, detail=f"Dataset not ready (status={meta.status}).")

    cached = cache.get("forecast", dataset_id,
                       horizon=horizon, product=product or "",
                       confidence=confidence, aggregation=aggregation)
    if cached:
        return cached

    df = repo.get_dataframe(dataset_id)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No sales records found.")

    try:
        result = forecast_svc.forecast(
            df, horizon=horizon, product=product,
            confidence=confidence, aggregation=aggregation,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Forecast error")
        raise HTTPException(status_code=500, detail=str(exc))

    response = ForecastResponse(
        dataset_id=dataset_id,
        model=result["model"],
        horizon=horizon,
        aggregation=aggregation,
        product=product,
        confidence=confidence,
        labels=result["labels"],
        values=result["values"],
        lower=result["lower"],
        upper=result["upper"],
        mae=result.get("mae"),
        warnings=result.get("warnings", []),
    )

    cache.set("forecast", dataset_id, response,
              horizon=horizon, product=product or "",
              confidence=confidence, aggregation=aggregation)
    return response
