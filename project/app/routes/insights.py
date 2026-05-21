"""GET /insights — KPIs, anomalies, and narrative summary."""
from fastapi import APIRouter, HTTPException, Query

from app.models.api_models import (
    InsightsResponse, AnomalySummary, TopProduct,
    MonthlyGrowth, ChartData
)
from app.models.dataset_models import DatasetStatus
from app.repositories.dataset_repository import PostgresDatasetRepository
from app.services.analysis import AnalysisService
from app.services.anomaly_detection import AnomalyDetector
from app.services import cache
from app.core.logging import get_logger

router = APIRouter(tags=["Insights"])
logger = get_logger(__name__)

analysis_svc = AnalysisService()
anomaly_svc = AnomalyDetector()


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(
    dataset_id: str = Query(...),
    anomaly_method: str = Query(default="zscore", pattern="^(zscore|iqr)$"),
    anomaly_threshold: float = Query(default=2.5, ge=1.0, le=5.0),
):
    repo = PostgresDatasetRepository()
    meta = repo.get_metadata(dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found.")
    if meta.status != DatasetStatus.CLEANED:
        raise HTTPException(status_code=409, detail=f"Dataset status is '{meta.status}'.")

    cached = cache.get("insights", dataset_id, method=anomaly_method, threshold=anomaly_threshold)
    if cached:
        return cached

    df = repo.get_dataframe(dataset_id)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No sales records found.")

    try:
        data = analysis_svc.compute_insights(df)
        anomaly_data = anomaly_svc.detect(df, method=anomaly_method, threshold=anomaly_threshold)
    except Exception as exc:
        logger.exception("Error computing insights")
        raise HTTPException(status_code=500, detail=str(exc))

    response = InsightsResponse(
        dataset_id=dataset_id,
        total_sales=data["total_sales"],
        avg_ticket=data["avg_ticket"],
        total_transactions=data["total_transactions"],
        top_products=[
            TopProduct(
                name=p["name"],
                total=p["total"],
                pct=p["pct"],           # ← campo correcto para el frontend
            )
            for p in data["top_products"]
        ],
        monthly_growth=[
            MonthlyGrowth(
                month=m["month"],
                sales=m["sales"],       # ← campo correcto para el frontend
                mom_pct=m["mom_pct"],   # ← campo correcto para el frontend
            )
            for m in data["monthly_growth"]
        ],
        anomalies=[AnomalySummary(**a) for a in anomaly_data["anomalies"]],
        natural_summary=data["natural_summary"],
        chart_ready=ChartData(**data["chart_ready"]),
    )

    cache.set("insights", dataset_id, response, method=anomaly_method, threshold=anomaly_threshold)
    return response
