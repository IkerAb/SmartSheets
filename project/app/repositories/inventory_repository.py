"""PostgreSQL repository for inventory and sell-through data."""

from __future__ import annotations

import pandas as pd
from datetime import UTC, datetime
from uuid import uuid4

from psycopg import Connection, connect

from app.core.config import settings
from app.models.inventory_models import (
    InventoryPersistRequest,
    InventoryPersistResult,
)


class PostgresInventoryRepository:

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or settings.psycopg_dsn

    def persist_inventory(self, request: InventoryPersistRequest) -> InventoryPersistResult:
        inventory_id = str(uuid4())
        now = datetime.now(UTC)

        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO inventory_calendars
                            (inventory_id, source_filename, uploaded_at)
                        VALUES (%s, %s, %s)
                        """,
                        (inventory_id, request.source_filename, now),
                    )
                    cur.executemany(
                        """
                        INSERT INTO inventory_records
                            (inventory_id, semana_fiscal, categoria, tienda,
                             inventario_inicial, unidades_vendidas)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [
                            (inventory_id, r.semana_fiscal, r.categoria, r.tienda,
                             r.inventario_inicial, r.unidades_vendidas)
                            for r in request.records
                        ],
                    )

        semanas = len({r.semana_fiscal for r in request.records})
        categorias = sorted({r.categoria for r in request.records})

        return InventoryPersistResult(
            inventory_id=inventory_id,
            row_count=len(request.records),
            semanas=semanas,
            categorias=categorias,
        )

    def get_dataframe(self, inventory_id: str) -> pd.DataFrame | None:
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT semana_fiscal, categoria, tienda,
                           inventario_inicial, unidades_vendidas
                    FROM inventory_records
                    WHERE inventory_id = %s
                    ORDER BY semana_fiscal, categoria, tienda
                    """,
                    (inventory_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    return None
                return pd.DataFrame(rows, columns=[
                    "semana_fiscal", "categoria", "tienda",
                    "inventario_inicial", "unidades_vendidas"
                ])

    def get_week_dataframe(self, inventory_id: str, semana: int) -> pd.DataFrame | None:
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT semana_fiscal, categoria, tienda,
                           inventario_inicial, unidades_vendidas
                    FROM inventory_records
                    WHERE inventory_id = %s AND semana_fiscal = %s
                    ORDER BY categoria, tienda
                    """,
                    (inventory_id, semana),
                )
                rows = cur.fetchall()
                if not rows:
                    return None
                return pd.DataFrame(rows, columns=[
                    "semana_fiscal", "categoria", "tienda",
                    "inventario_inicial", "unidades_vendidas"
                ])

    @staticmethod
    def _ensure_tables(conn: Connection) -> None:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory_calendars (
                    inventory_id    TEXT PRIMARY KEY,
                    source_filename TEXT NOT NULL,
                    uploaded_at     TIMESTAMPTZ NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory_records (
                    id                  BIGSERIAL PRIMARY KEY,
                    inventory_id        TEXT NOT NULL REFERENCES inventory_calendars(inventory_id) ON DELETE CASCADE,
                    semana_fiscal       INTEGER NOT NULL,
                    categoria           TEXT NOT NULL,
                    tienda              TEXT NOT NULL,
                    inventario_inicial  INTEGER NOT NULL,
                    unidades_vendidas   INTEGER NOT NULL
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_inventory_records_id
                ON inventory_records(inventory_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_inventory_records_semana
                ON inventory_records(inventory_id, semana_fiscal)
            """)
