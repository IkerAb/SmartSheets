"""POST /upload — file ingestion endpoint."""
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.models.api_models import UploadResponse
from app.models.dataset_models import DatasetStatus
from app.repositories.dataset_repository import PostgresDatasetRepository
from app.services.data_loader import DataLoaderService, FileUploadPayload
from app.services import cache
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter(tags=["Upload"])
logger = get_logger(__name__)


def get_loader() -> DataLoaderService:
    return DataLoaderService(repository=PostgresDatasetRepository())


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    loader: DataLoaderService = Depends(get_loader),
):
    """
    Upload a CSV or Excel sales file.

    Required columns: **fecha**, **producto**, **ventas**.
    Returns a `dataset_id` to use in all subsequent endpoints.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name.")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(content)/1e6:.1f} MB). Max: {settings.max_upload_mb} MB.",
        )

    payload = FileUploadPayload(filename=file.filename, content=content)

    try:
        result = loader.ingest_and_persist(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error during ingestion")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")

    # invalidate any stale cache for this dataset (shouldn't exist but be safe)
    cache.invalidate_dataset(result.dataset_id)

    # load metadata for response
    repo = PostgresDatasetRepository()
    meta = repo.get_metadata(result.dataset_id)
    df = repo.get_dataframe(result.dataset_id)

    products = sorted(df["producto"].unique().tolist()) if df is not None else []
    date_range = ("", "")
    columns: list[str] = []
    if df is not None:
        date_range = (
            df["fecha"].min().strftime("%Y-%m-%d"),
            df["fecha"].max().strftime("%Y-%m-%d"),
        )
        columns = list(df.columns)

    return UploadResponse(
        dataset_id=result.dataset_id,
        row_count=result.row_count,
        columns=columns,
        date_range=date_range,
        products=products,
        status=DatasetStatus.CLEANED.value,
    )
