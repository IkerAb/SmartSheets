"""Persistence contracts and PostgreSQL implementation for datasets."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from psycopg import Connection, connect

from app.core.config import settings
from app.models.dataset_models import DatasetPersistRequest, DatasetPersistResult


class DatasetRepository(Protocol):
    """Abstract repository boundary for dataset writes."""

    def persist_dataset(self, request: DatasetPersistRequest) -> DatasetPersistResult:
        """Persist metadata + records atomically."""


class PostgresDatasetRepository:
    """PostgreSQL-backed implementation of dataset persistence."""

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or settings.psycopg_dsn

    def persist_dataset(self, request: DatasetPersistRequest) -> DatasetPersistResult:
        dataset_id = str(uuid4())
        now = datetime.now(UTC)
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO datasets (
                            dataset_id, source_filename, status, uploaded_at, processed_at, error_reason
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (dataset_id, request.source_filename, request.status.value, now, now, None),
                    )
                    cur.executemany(
                        """
                        INSERT INTO sales_records (dataset_id, fecha, producto, ventas)
                        VALUES (%s, %s, %s, %s)
                        """,
                        [
                            (dataset_id, record.fecha, record.producto, record.ventas)
                            for record in request.records
                        ],
                    )
        return DatasetPersistResult(dataset_id=dataset_id, row_count=len(request.records))

    @staticmethod
    def _ensure_tables(conn: Connection) -> None:
        """Create required tables if they do not exist yet."""
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    source_filename TEXT NOT NULL,
                    status TEXT NOT NULL,
                    uploaded_at TIMESTAMPTZ NOT NULL,
                    processed_at TIMESTAMPTZ,
                    error_reason TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sales_records (
                    id BIGSERIAL PRIMARY KEY,
                    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
                    fecha TIMESTAMPTZ NOT NULL,
                    producto TEXT NOT NULL,
                    ventas DOUBLE PRECISION NOT NULL
                )
                """
            )
