"""
app/routes/traffic.py
──────────────────────
POST /traffic/upload  — subir datos de tráfico
GET  /traffic/{traffic_id}/conversion  — análisis de conversión por tienda
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.models.api_models import (
    TrafficUploadResponse,
    TrafficResponse,
    StoreTrafficRow,
)
from app.repositories.traffic_repository import PostgresTrafficRepository
from app.services.traffic_service import TrafficService, TrafficUploadPayload
from app.core.logging import get_logger

router = APIRouter(tags=["Traffic"])
logger = get_logger(__name__)

traffic_svc = TrafficService()


@router.post("/traffic/upload", response_model=TrafficUploadResponse, status_code=201)
async def upload_traffic(file: UploadFile = File(...)):
    """
    Sube un archivo de tráfico por tienda CSV o Excel.

    Columnas requeridas:
    - **semana_fiscal**: número de semana (1-52)
    - **tienda**: nombre de la tienda
    - **trafico**: visitantes que entraron a la tienda
    - **transacciones**: número de compras realizadas
    - **tasa_conversion_pct**: porcentaje de conversión
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo no tiene nombre.")

    content = await file.read()
    payload = TrafficUploadPayload(filename=file.filename, content=content)

    try:
        result = traffic_svc.ingest_and_persist(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Error cargando tráfico")
        raise HTTPException(status_code=500, detail=str(exc))

    return TrafficUploadResponse(
        traffic_id=result.traffic_id,
        row_count=result.row_count,
        semanas=result.semanas,
        tiendas=result.tiendas,
    )


@router.get("/traffic/{traffic_id}/conversion", response_model=TrafficResponse)
async def get_conversion(
    traffic_id: str,
    semana: int | None = Query(default=None, ge=1, le=52, description="Semana fiscal. None = todas."),
):
    """
    Calcula tráfico y tasa de conversión por tienda.
    Si se pasa semana, filtra solo esa semana.
    """
    repo = PostgresTrafficRepository()
    df = repo.get_dataframe(traffic_id)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Tráfico '{traffic_id}' no encontrado.")

    try:
        points = traffic_svc.compute_traffic_analysis(df, semana=semana)
    except Exception as exc:
        logger.exception("Error calculando conversión")
        raise HTTPException(status_code=500, detail=str(exc))

    rows = [
        StoreTrafficRow(
            tienda=p.tienda,
            trafico_total=p.trafico_total,
            transacciones_total=p.transacciones_total,
            tasa_conversion_pct=p.tasa_conversion_pct,
            vs_promedio_pct=p.vs_promedio_pct,
            nivel_conversion=p.nivel_conversion,
            insight=p.insight,
        )
        for p in points
    ]

    avg_conv = round(sum(r.tasa_conversion_pct for r in rows) / len(rows), 1) if rows else 0.0
    best = max(rows, key=lambda r: r.tasa_conversion_pct).tienda if rows else ""
    worst = min(rows, key=lambda r: r.tasa_conversion_pct).tienda if rows else ""

    return TrafficResponse(
        traffic_id=traffic_id,
        semana_fiscal=semana,
        rows=rows,
        avg_conversion=avg_conv,
        best_store=best,
        worst_store=worst,
    )
