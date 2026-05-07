"""Upload ingestion service: parse files and orchestrate persistence."""

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
    """Coordinate upload parsing and PostgreSQL-backed persistence."""

    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def ingest_and_persist(self, payload: FileUploadPayload) -> DatasetPersistResult:
        df = load_sales_dataframe(file_bytes=payload.content, filename=payload.filename)
        df = validate_and_normalize_sales_dataframe(df)
        records = self._to_records(df=df)
        request = DatasetPersistRequest(
            source_filename=payload.filename,
            status=DatasetStatus.VALIDATED,
            records=records,
        )
        return self._repository.persist_dataset(request=request)

    @staticmethod
    def _to_records(df: pd.DataFrame) -> list[SalesRecordInput]:
        """
        Convert parsed dataframe rows into canonical record DTOs.

        Detailed validation rules are implemented in task 2.2.
        """
        result: list[SalesRecordInput] = []
        for row in df.itertuples(index=False):
            row_dict = row._asdict()
            result.append(
                SalesRecordInput(
                    fecha=row_dict["fecha"].to_pydatetime(),
                    producto=row_dict["producto"],
                    ventas=row_dict["ventas"],
                )
            )
        return result
