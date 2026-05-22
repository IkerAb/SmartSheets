"""
app/routes/inventory.py
────────────────────────
POST /inventory/upload  — subir inventario semanal
GET  /inventory/{inventory_id}/sellthrough  — sell-through por semana
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.models.api_models import (
    InventoryUploadResponse,
    SellThroughResponse,
    SellThroughRow,
)
from app.repositories.inventory_repository import PostgresInventoryRepository
from app.repositories.promotion_repository import PostgresPromotionRepository
from app.services.inventory_service import InventoryService, InventoryUploadPayload
from app.core.logging import get_logger

router = APIRouter(tags=["Inventory"])
logger = get_logger(__name__)

inventory_svc = InventoryService()


@router.post("/inventory/upload", response_model=InventoryUploadResponse, status_code=201)
async def upload_inventory(file: UploadFile = File(...)):
    """
    Sube un archivo de inventario semanal CSV o Excel.

    Columnas requeridas:
    - **semana_fiscal**: número de semana (1-52)
    - **categoria**: categoría de producto
    - **tienda**: nombre de la tienda
    - **inventario_inicial**: unidades al inicio de la semana
    - **unidades_vendidas**: unidades vendidas en la semana
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo no tiene nombre.")

    content = await file.read()
    payload = InventoryUploadPayload(filename=file.filename, content=content)

    try:
        result = inventory_svc.ingest_and_persist(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Error cargando inventario")
        raise HTTPException(status_code=500, detail=str(exc))

    return InventoryUploadResponse(
        inventory_id=result.inventory_id,
        row_count=result.row_count,
        semanas=result.semanas,
        categorias=result.categorias,
    )


@router.get("/inventory/{inventory_id}/sellthrough", response_model=SellThroughResponse)
async def get_sell_through(
    inventory_id: str,
    semana: int | None = Query(default=None, ge=1, le=52, description="Semana fiscal (1-52). None = todas."),
    promo_id: str | None = Query(default=None, description="UUID del calendario de promociones para cruzar datos."),
):
    """
    Calcula el Sell-Through por categoría.

    - Si se pasa **semana**, filtra solo esa semana.
    - Si se pasa **promo_id**, cruza con las promos activas para generar insights automáticos.
    - Devuelve inventario inicial, unidades vendidas, ST% y un insight en lenguaje natural.
    """
    inv_repo = PostgresInventoryRepository()
    inv_df = inv_repo.get_dataframe(inventory_id)
    if inv_df is None:
        raise HTTPException(status_code=404, detail=f"Inventario '{inventory_id}' no encontrado.")

    promo_df = None
    if promo_id:
        promo_repo = PostgresPromotionRepository()
        promo_df = promo_repo.get_dataframe(promo_id)

    try:
        points = inventory_svc.compute_sell_through(
            inventory_df=inv_df,
            promo_df=promo_df,
            semana=semana,
        )
    except Exception as exc:
        logger.exception("Error calculando sell-through")
        raise HTTPException(status_code=500, detail=str(exc))

    rows = [
        SellThroughRow(
            categoria=p.categoria,
            inventario_inicial=p.inventario_inicial,
            unidades_vendidas=p.unidades_vendidas,
            sell_through_pct=p.sell_through_pct,
            nivel=p.nivel,
            tiene_promo=p.tiene_promo,
            tipo_promos=p.tipo_promos,
            md_promedio=p.md_promedio,
            insight=p.insight,
        )
        for p in points
    ]

    # resumen general
    altos = [r for r in rows if r.nivel == "alto"]
    bajos = [r for r in rows if r.nivel == "bajo" and r.tiene_promo]
    resumen_parts = []
    if altos:
        cats = ", ".join(r.categoria for r in altos)
        resumen_parts.append(f"ST alto en: {cats}.")
    if bajos:
        cats = ", ".join(r.categoria for r in bajos)
        resumen_parts.append(f"⚠️ ST bajo con promo activa en: {cats} — revisar inventario o efectividad de la promo.")
    resumen = " ".join(resumen_parts) if resumen_parts else "ST dentro de rangos esperados."

    return SellThroughResponse(
        inventory_id=inventory_id,
        promo_id=promo_id,
        semana_fiscal=semana,
        rows=rows,
        resumen=resumen,
    )
