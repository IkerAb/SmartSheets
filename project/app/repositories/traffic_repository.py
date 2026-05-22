"""PostgreSQL repository for store traffic data."""

from __future__ import annotations

import pandas as pd
from datetime import UTC, datetime
from uuid import uuid4

from psycopg import Connection, connect

from app.core.config import settings
from app.models.traffic_models import (
    TrafficPersistRequest,
    TrafficPersistResult,
)


class PostgresTrafficRepository:

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or settings.psycopg_dsn

    def persist_traffic(self, request: TrafficPersistRequest) -> TrafficPersistResult:
        traffic_id = str(uuid4())
        now = datetime.now(UTC)

        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO traffic_calendars
                            (traffic_id, source_filename, uploaded_at)
                        VALUES (%s, %s, %s)
                        """,
                        (traffic_id, request.source_filename, now),
                    )
                    cur.executemany(
                        """
                        INSERT INTO traffic_records
                            (traffic_id, semana_fiscal, tienda,
                             trafico, transacciones, tasa_conversion_pct)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [
                            (traffic_id, r.semana_fiscal, r.tienda,
                             r.trafico, r.transacciones, r.tasa_conversion_pct)
                            for r in request.records
                        ],
                    )

        semanas = len({r.semana_fiscal for r in request.records})
        tiendas = sorted({r.tienda for r in request.records})

        return TrafficPersistResult(
            traffic_id=traffic_id,
            row_count=len(request.records),
            semanas=semanas,
            tiendas=tiendas,
        )

    def get_dataframe(self, traffic_id: str) -> pd.DataFrame | None:
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT semana_fiscal, tienda, trafico,
                           transacciones, tasa_conversion_pct
                    FROM traffic_records
                    WHERE traffic_id = %s
                    ORDER BY semana_fiscal, tienda
                    """,
                    (traffic_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    return None
                return pd.DataFrame(rows, columns=[
                    "semana_fiscal", "tienda", "trafico",
                    "transacciones", "tasa_conversion_pct"
                ])

    def get_week_dataframe(self, traffic_id: str, semana: int) -> pd.DataFrame | None:
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT semana_fiscal, tienda, trafico,
                           transacciones, tasa_conversion_pct
                    FROM traffic_records
                    WHERE traffic_id = %s AND semana_fiscal = %s
                    ORDER BY tienda
                    """,
                    (traffic_id, semana),
                )
                rows = cur.fetchall()
                if not rows:
                    return None
                return pd.DataFrame(rows, columns=[
                    "semana_fiscal", "tienda", "trafico",
                    "transacciones", "tasa_conversion_pct"
                ])

    @staticmethod
    def _ensure_tables(conn: Connection) -> None:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS traffic_calendars (
                    traffic_id      TEXT PRIMARY KEY,
                    source_filename TEXT NOT NULL,
                    uploaded_at     TIMESTAMPTZ NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS traffic_records (
                    id                   BIGSERIAL PRIMARY KEY,
                    traffic_id           TEXT NOT NULL REFERENCES traffic_calendars(traffic_id) ON DELETE CASCADE,
                    semana_fiscal        INTEGER NOT NULL,
                    tienda               TEXT NOT NULL,
                    trafico              INTEGER NOT NULL,
                    transacciones        INTEGER NOT NULL,
                    tasa_conversion_pct  DOUBLE PRECISION NOT NULL
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_traffic_records_id
                ON traffic_records(traffic_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_traffic_records_semana
                ON traffic_records(traffic_id, semana_fiscal)
            """)
