"""Persistence contracts and PostgreSQL implementation for datasets."""

from __future__ import annotations

import pandas as pd
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from psycopg import Connection, connect

from app.core.config import settings
from app.models.dataset_models import (
    DatasetMetadata,
    DatasetPersistRequest,
    DatasetPersistResult,
    DatasetStatus,
)


class DatasetRepository(Protocol):
    """Abstract repository boundary — services depend on this, not on Postgres."""

    def persist_dataset(self, request: DatasetPersistRequest) -> DatasetPersistResult: ...
    def get_metadata(self, dataset_id: str) -> DatasetMetadata | None: ...
    def get_dataframe(self, dataset_id: str) -> pd.DataFrame | None: ...
    def mark_failed(self, dataset_id: str, reason: str) -> None: ...


class PostgresDatasetRepository:
    """PostgreSQL-backed implementation of DatasetRepository."""

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or settings.psycopg_dsn

    # ── writes ────────────────────────────────────────────────────────────────

    def persist_dataset(self, request: DatasetPersistRequest) -> DatasetPersistResult:
        """Insert metadata + records atomically; status becomes CLEANED on success."""
        dataset_id = str(uuid4())
        now = datetime.now(UTC)

        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            try:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO datasets
                                (dataset_id, source_filename, status, uploaded_at, processed_at, error_reason)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (dataset_id, request.source_filename,
                             DatasetStatus.CLEANED.value, now, now, None),
                        )
                        cur.executemany(
                            """
                            INSERT INTO sales_records (dataset_id, fecha, producto, ventas)
                            VALUES (%s, %s, %s, %s)
                            """,
                            [
                                (dataset_id, r.fecha, r.producto, r.ventas)
                                for r in request.records
                            ],
                        )
            except Exception as exc:
                # Mark as failed if any mid-transaction error
                self._insert_failed(conn, dataset_id, request.source_filename, now, str(exc))
                raise

        return DatasetPersistResult(
            dataset_id=dataset_id,
            row_count=len(request.records),
            status=DatasetStatus.CLEANED,
        )

    def mark_failed(self, dataset_id: str, reason: str) -> None:
        with connect(self._dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE datasets SET status=%s, error_reason=%s WHERE dataset_id=%s",
                    (DatasetStatus.FAILED.value, reason, dataset_id),
                )

    # ── reads ─────────────────────────────────────────────────────────────────

    def get_metadata(self, dataset_id: str) -> DatasetMetadata | None:
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT d.dataset_id, d.source_filename, d.status,
                           d.uploaded_at, d.processed_at, d.error_reason,
                           COUNT(s.id) AS row_count
                    FROM datasets d
                    LEFT JOIN sales_records s ON s.dataset_id = d.dataset_id
                    WHERE d.dataset_id = %s
                    GROUP BY d.dataset_id
                    """,
                    (dataset_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return DatasetMetadata(
                    dataset_id=row[0],
                    source_filename=row[1],
                    status=DatasetStatus(row[2]),
                    uploaded_at=row[3],
                    processed_at=row[4],
                    error_reason=row[5],
                    row_count=row[6],
                )

    def get_dataframe(self, dataset_id: str) -> pd.DataFrame | None:
        """Load cleaned sales records as a DataFrame for analytics/forecast services."""
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT fecha, producto, ventas
                    FROM sales_records
                    WHERE dataset_id = %s
                    ORDER BY fecha
                    """,
                    (dataset_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    return None
                df = pd.DataFrame(rows, columns=["fecha", "producto", "ventas"])
                df["fecha"] = pd.to_datetime(df["fecha"], utc=True)
                df["ventas"] = df["ventas"].astype(float)
                return df

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _insert_failed(conn, dataset_id, filename, now, reason):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO datasets
                        (dataset_id, source_filename, status, uploaded_at, error_reason)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (dataset_id) DO UPDATE SET status=%s, error_reason=%s
                    """,
                    (dataset_id, filename, DatasetStatus.FAILED.value, now, reason,
                     DatasetStatus.FAILED.value, reason),
                )
        except Exception:
            pass

    @staticmethod
    def _ensure_tables(conn: Connection) -> None:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id     TEXT PRIMARY KEY,
                    source_filename TEXT NOT NULL,
                    status          TEXT NOT NULL,
                    uploaded_at     TIMESTAMPTZ NOT NULL,
                    processed_at    TIMESTAMPTZ,
                    error_reason    TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sales_records (
                    id          BIGSERIAL PRIMARY KEY,
                    dataset_id  TEXT NOT NULL REFERENCES datasets(dataset_id) ON DELETE CASCADE,
                    fecha       TIMESTAMPTZ NOT NULL,
                    producto    TEXT NOT NULL,
                    ventas      DOUBLE PRECISION NOT NULL
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_sales_dataset
                ON sales_records(dataset_id)
            """)
