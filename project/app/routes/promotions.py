"""
app/routes/promotions.py
─────────────────────────
POST /promotions/upload  — subir calendario de promociones
GET  /promotions/{promo_id}/week/{semana}  — promos de una semana
GET  /promotions/{promo_id}/calendar  — calendario completo con ventas
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.models.api_models import (
    PromoUploadResponse,
    WeekPromoResponse,
    FiscalCalendarResponse,
    FiscalWeekSales,
    PromoRecord,
)
from app.repositories.promotion_repository import PostgresPromotionRepository
from app.repositories.dataset_repository import PostgresDatasetRepository
from app.services.promotion_loader import PromotionLoaderService, PromoUploadPayload
from app.core.logging import get_logger

router = APIRouter(tags=["Promotions"])
logger = get_logger(__name__)

loader_svc = PromotionLoaderService()


@router.post("/promotions/upload", response_model=PromoUploadResponse, status_code=201)
async def upload_promotions(file: UploadFile = File(...)):
    """
    Sube un calendario de promociones CSV o Excel.

    Columnas requeridas:
    - **semana_fiscal**: número de semana (1-52)
    - **fecha_inicio**: fecha de inicio de la semana
    - **fecha_fin**: fecha de fin de la semana
    - **tipo_promo**: WkndPromo | OtherPromo | DD
    - **categoria**: categoría de producto en promoción
    - **descripcion**: descripción de la promo
    - **md_pct**: porcentaje de markdown (0-100)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo no tiene nombre.")

    content = await file.read()
    payload = PromoUploadPayload(filename=file.filename, content=content)

    try:
        result = loader_svc.ingest_and_persist(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Error cargando calendario de promociones")
        raise HTTPException(status_code=500, detail=str(exc))

    return PromoUploadResponse(
        promo_id=result.promo_id,
        row_count=result.row_count,
        semanas=result.semanas,
        categorias=result.categorias,
    )


@router.get("/promotions/{promo_id}/week/{semana}", response_model=WeekPromoResponse)
async def get_week_promotions(promo_id: str, semana: int):
    """
    Devuelve las promociones de una semana fiscal específica,
    separadas por tipo: WkndPromo, OtherPromo y DD.
    """
    if not 1 <= semana <= 52:
        raise HTTPException(status_code=422, detail="Semana debe estar entre 1 y 52.")

    repo = PostgresPromotionRepository()
    meta = repo.get_metadata(promo_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Calendario '{promo_id}' no encontrado.")

    df = repo.get_week_promotions(promo_id, semana)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No hay promos para la semana {semana}.")

    def to_records(tipo):
        subset = df[df["tipo_promo"] == tipo]
        return [
            PromoRecord(
                semana_fiscal=int(row.semana_fiscal),
                fecha_inicio=str(row.fecha_inicio),
                fecha_fin=str(row.fecha_fin),
                tipo_promo=row.tipo_promo,
                categoria=row.categoria,
                descripcion=row.descripcion,
                md_pct=float(row.md_pct),
            )
            for row in subset.itertuples(index=False)
        ]

    first = df.iloc[0]
    avg_md = round(float(df["md_pct"].mean()), 1)
    cats = sorted(df["categoria"].unique().tolist())

    return WeekPromoResponse(
        promo_id=promo_id,
        semana_fiscal=semana,
        fecha_inicio=str(first["fecha_inicio"]),
        fecha_fin=str(first["fecha_fin"]),
        wknd_promos=to_records("WkndPromo"),
        other_promos=to_records("OtherPromo"),
        daily_deals=to_records("DD"),
        avg_md_pct=avg_md,
        categorias_en_promo=cats,
    )


@router.get("/promotions/{promo_id}/calendar", response_model=FiscalCalendarResponse)
async def get_fiscal_calendar(
    promo_id: str,
    dataset_id: str = Query(..., description="UUID del dataset de ventas"),
):
    """
    Combina ventas por semana fiscal con el calendario de promociones.
    Devuelve cada semana con sus ventas, transacciones y promos activas.
    """
    promo_repo = PostgresPromotionRepository()
    sales_repo = PostgresDatasetRepository()

    if not promo_repo.get_metadata(promo_id):
        raise HTTPException(status_code=404, detail=f"Calendario '{promo_id}' no encontrado.")
    if not sales_repo.get_metadata(dataset_id):
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' no encontrado.")

    promo_df = promo_repo.get_dataframe(promo_id)
    sales_df = sales_repo.get_dataframe(dataset_id)

    if promo_df is None or sales_df is None:
        raise HTTPException(status_code=404, detail="No se encontraron datos.")

    # normalizar fechas
    sales_df["fecha"] = sales_df["fecha"].dt.tz_localize(None)
    promo_df["fecha_inicio"] = promo_df["fecha_inicio"].apply(
        lambda x: x if hasattr(x, 'year') else x
    )

    # agregar ventas por semana fiscal
    weeks = promo_df[["semana_fiscal", "fecha_inicio", "fecha_fin"]].drop_duplicates()
    result = []

    for _, week in weeks.iterrows():
        semana = int(week["semana_fiscal"])
        fi = str(week["fecha_inicio"])
        ff = str(week["fecha_fin"])

        import pandas as pd
        mask = (
            sales_df["fecha"] >= pd.Timestamp(fi)
        ) & (
            sales_df["fecha"] <= pd.Timestamp(ff) + pd.Timedelta(days=1)
        )
        week_sales = sales_df[mask]

        total = round(float(week_sales["ventas"].sum()), 2) if not week_sales.empty else 0.0
        txs = len(week_sales)

        # promos de esa semana
        week_promos_df = promo_df[promo_df["semana_fiscal"] == semana]
        promos = [
            PromoRecord(
                semana_fiscal=semana,
                fecha_inicio=str(r.fecha_inicio),
                fecha_fin=str(r.fecha_fin),
                tipo_promo=r.tipo_promo,
                categoria=r.categoria,
                descripcion=r.descripcion,
                md_pct=float(r.md_pct),
            )
            for r in week_promos_df.itertuples(index=False)
        ]

        avg_md = round(float(week_promos_df["md_pct"].mean()), 1) if not week_promos_df.empty else 0.0

        result.append(FiscalWeekSales(
            semana_fiscal=semana,
            fecha_inicio=fi,
            fecha_fin=ff,
            total_sales=total,
            transactions=txs,
            has_promo=not week_promos_df.empty,
            avg_md_pct=avg_md,
            promos=promos,
        ))

    result.sort(key=lambda x: x.semana_fiscal)

    return FiscalCalendarResponse(
        dataset_id=dataset_id,
        promo_id=promo_id,
        weeks=result,
    )
