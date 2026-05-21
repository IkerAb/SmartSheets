"""GET /forecast — time-series sales forecast."""
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from app.models.api_models import ForecastResponse, ForecastPoint
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
    Genera un forecast de ventas.
    La respuesta incluye `series` — array combinado histórico + forecast
    listo para el gráfico del frontend (ForecastLineChart).
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

    # ── Construir series combinado histórico + forecast para el gráfico ──────
    series = _build_series(df, result, product, aggregation)

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
        series=series,
    )

    cache.set("forecast", dataset_id, response,
              horizon=horizon, product=product or "",
              confidence=confidence, aggregation=aggregation)
    return response


def _build_series(df: pd.DataFrame, result: dict, product: str | None, aggregation: str) -> list[ForecastPoint]:
    """
    Combina datos históricos reales + predicción futura en un solo array.
    El frontend (ForecastLineChart) usa este array directamente:
    - actual != None, forecast == None → punto histórico (línea cyan)
    - actual == None, forecast != None → punto predicho (línea indigo)
    """
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.tz_localize(None)

    if product:
        subset = df[df["producto"].str.lower() == product.lower()]
    else:
        subset = df

    freq = "D" if aggregation == "day" else "ME"
    fmt = "%Y-%m-%d" if aggregation == "day" else "%Y-%m"

    historical = (
        subset.set_index("fecha")["ventas"]
        .resample(freq)
        .sum()
    )

    # últimos 60 puntos históricos para no saturar el gráfico
    historical = historical.tail(60)

    series: list[ForecastPoint] = []

    # puntos históricos
    for date, val in historical.items():
        series.append(ForecastPoint(
            date=pd.Timestamp(date).strftime(fmt),
            actual=round(float(val), 2),
            forecast=None,
            lower=None,
            upper=None,
        ))

    # puntos de forecast
    for i, label in enumerate(result["labels"]):
        series.append(ForecastPoint(
            date=label,
            actual=None,
            forecast=result["values"][i],
            lower=result["lower"][i],
            upper=result["upper"][i],
        ))

    return series
