"""Domain DTOs for dataset ingestion and persistence boundaries."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class DatasetStatus(StrEnum):
    """Lifecycle states for uploaded datasets."""
    UPLOADED = "uploaded"
    VALIDATED = "validated"
    CLEANED = "cleaned"
    FAILED = "failed"


@dataclass(frozen=True)
class SalesRecordInput:
    """Canonical sales row prepared for persistence."""
    fecha: datetime
    producto: str
    ventas: float


@dataclass(frozen=True)
class DatasetPersistRequest:
    """Repository payload for metadata + records atomic ingestion."""
    source_filename: str
    status: DatasetStatus
    records: list[SalesRecordInput]
    error_reason: str | None = None


@dataclass(frozen=True)
class DatasetPersistResult:
    """Repository response after successful dataset insertion."""
    dataset_id: str
    row_count: int
    status: DatasetStatus


@dataclass(frozen=True)
class DatasetMetadata:
    """Dataset metadata read from persistence."""
    dataset_id: str
    source_filename: str
    status: DatasetStatus
    uploaded_at: datetime
    processed_at: datetime | None
    error_reason: str | None
    row_count: int
