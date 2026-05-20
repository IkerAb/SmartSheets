"""Upload ingestion service: parse, validate, clean, and persist."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.models.dataset_models import (
    DatasetPersistRequest,
    DatasetPersistResult,
    DatasetStatus,
    SalesRecordInput,
)
from app.repositories.dataset_repository import DatasetRepository
from app.utils.file_handler import load_sales_dataframe
from app.utils.validators import validate_and_normalize_sales_dataframe


@dataclass(frozen=True)
class FileUploadPayload:
    """Service input payload for uploaded file content."""
    filename: str
    content: bytes


class DataLoaderService:
    """Coordinate upload parsing, validation, cleaning, and PostgreSQL persistence."""

    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def ingest_and_persist(self, payload: FileUploadPayload) -> DatasetPersistResult:
        """
        Full ingestion pipeline:
        1. Parse CSV/XLSX → raw DataFrame
        2. Validate schema and normalize types
        3. Convert to domain records
        4. Persist atomically → status CLEANED
        Raises ValueError on validation failures (caller marks dataset FAILED).
        """
        df = load_sales_dataframe(file_bytes=payload.content, filename=payload.filename)
        df = validate_and_normalize_sales_dataframe(df)
        records = self._to_records(df=df)
        request = DatasetPersistRequest(
            source_filename=payload.filename,
            status=DatasetStatus.CLEANED,
            records=records,
        )
        return self._repository.persist_dataset(request=request)

    @staticmethod
    def _to_records(df: pd.DataFrame) -> list[SalesRecordInput]:
        result: list[SalesRecordInput] = []
        for row in df.itertuples(index=False):
            d = row._asdict()
            result.append(
                SalesRecordInput(
                    fecha=d["fecha"].to_pydatetime(),
                    producto=str(d["producto"]),
                    ventas=float(d["ventas"]),
                )
            )
        return result
