"""POST /simulate — what-if scenario engine."""
from fastapi import APIRouter, HTTPException

from app.models.api_models import SimulateRequest, SimulateResponse, ScenarioResult, SimulateModifiers
from app.models.dataset_models import DatasetStatus
from app.repositories.dataset_repository import PostgresDatasetRepository
from app.services.forecasting import ForecastingService
from app.core.logging import get_logger

router = APIRouter(tags=["Simulate"])
logger = get_logger(__name__)

forecast_svc = ForecastingService()


@router.post("/simulate", response_model=SimulateResponse)
async def simulate_scenario(body: SimulateRequest):
    """
    Simula el impacto de cambios de precio/volumen sobre las ventas futuras.
    La respuesta incluye `modifiers` como objeto anidado (alineado con frontend).
    """
    if body.price_modifier == 1.0 and body.volume_modifier == 1.0:
        raise HTTPException(
            status_code=422,
            detail="At least one modifier must differ from 1.0.",
        )

    repo = PostgresDatasetRepository()
    meta = repo.get_metadata(body.dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Dataset '{body.dataset_id}' not found.")
    if meta.status != DatasetStatus.CLEANED:
        raise HTTPException(status_code=409, detail=f"Dataset not ready (status={meta.status}).")

    df = repo.get_dataframe(body.dataset_id)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No sales records found.")

    try:
        base = forecast_svc.forecast(df, horizon=body.horizon, product=body.product)

        df_sim = df.copy()
        df_sim["ventas"] = df_sim["ventas"] * body.price_modifier * body.volume_modifier
        simulated = forecast_svc.forecast(df_sim, horizon=body.horizon, product=body.product)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Simulation error")
        raise HTTPException(status_code=500, detail=str(exc))

    base_total = round(sum(base["values"]), 2)
    sim_total = round(sum(simulated["values"]), 2)
    delta = round(sim_total - base_total, 2)
    delta_pct = round((delta / base_total * 100) if base_total else 0.0, 2)

    return SimulateResponse(
        dataset_id=body.dataset_id,
        base=ScenarioResult(
            labels=base["labels"],
            values=base["values"],
            total_projected=base_total,
        ),
        simulated=ScenarioResult(
            labels=simulated["labels"],
            values=simulated["values"],
            total_projected=sim_total,
        ),
        delta_revenue=delta,
        delta_pct=delta_pct,
        modifiers=SimulateModifiers(         # ← objeto anidado que espera el frontend
            price_modifier=body.price_modifier,
            volume_modifier=body.volume_modifier,
        ),
    )
