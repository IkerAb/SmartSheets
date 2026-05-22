"""PostgreSQL repository for promotion calendars."""

from __future__ import annotations

import pandas as pd
from datetime import UTC, datetime
from uuid import uuid4

from psycopg import Connection, connect

from app.core.config import settings
from app.models.promotion_models import (
    PromotionMetadata,
    PromotionPersistRequest,
    PromotionPersistResult,
)


class PostgresPromotionRepository:

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or settings.psycopg_dsn

    def persist_promotions(self, request: PromotionPersistRequest) -> PromotionPersistResult:
        promo_id = str(uuid4())
        now = datetime.now(UTC)

        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO promotion_calendars
                            (promo_id, source_filename, uploaded_at)
                        VALUES (%s, %s, %s)
                        """,
                        (promo_id, request.source_filename, now),
                    )
                    cur.executemany(
                        """
                        INSERT INTO promotion_records
                            (promo_id, semana_fiscal, fecha_inicio, fecha_fin,
                             tipo_promo, categoria, descripcion, md_pct)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            (promo_id, r.semana_fiscal, r.fecha_inicio, r.fecha_fin,
                             r.tipo_promo, r.categoria, r.descripcion, r.md_pct)
                            for r in request.records
                        ],
                    )

        semanas = len({r.semana_fiscal for r in request.records})
        categorias = sorted({r.categoria for r in request.records})

        return PromotionPersistResult(
            promo_id=promo_id,
            row_count=len(request.records),
            semanas=semanas,
            categorias=categorias,
        )

    def get_metadata(self, promo_id: str) -> PromotionMetadata | None:
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT pc.promo_id, pc.source_filename, pc.uploaded_at,
                           COUNT(pr.id) AS row_count,
                           COUNT(DISTINCT pr.semana_fiscal) AS semanas,
                           ARRAY_AGG(DISTINCT pr.categoria ORDER BY pr.categoria) AS categorias
                    FROM promotion_calendars pc
                    LEFT JOIN promotion_records pr ON pr.promo_id = pc.promo_id
                    WHERE pc.promo_id = %s
                    GROUP BY pc.promo_id
                    """,
                    (promo_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return PromotionMetadata(
                    promo_id=row[0],
                    source_filename=row[1],
                    uploaded_at=str(row[2]),
                    row_count=row[3],
                    semanas=row[4],
                    categorias=row[5] or [],
                )

    def get_dataframe(self, promo_id: str) -> pd.DataFrame | None:
        """Carga el calendario como DataFrame para análisis."""
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT semana_fiscal, fecha_inicio, fecha_fin,
                           tipo_promo, categoria, descripcion, md_pct
                    FROM promotion_records
                    WHERE promo_id = %s
                    ORDER BY semana_fiscal, tipo_promo
                    """,
                    (promo_id,),
                )
                rows = cur.fetchall()
                if not rows:
                    return None
                return pd.DataFrame(rows, columns=[
                    "semana_fiscal", "fecha_inicio", "fecha_fin",
                    "tipo_promo", "categoria", "descripcion", "md_pct"
                ])

    def get_week_promotions(self, promo_id: str, semana: int) -> pd.DataFrame | None:
        """Carga las promos de una semana específica."""
        with connect(self._dsn) as conn:
            self._ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT semana_fiscal, fecha_inicio, fecha_fin,
                           tipo_promo, categoria, descripcion, md_pct
                    FROM promotion_records
                    WHERE promo_id = %s AND semana_fiscal = %s
                    ORDER BY tipo_promo
                    """,
                    (promo_id, semana),
                )
                rows = cur.fetchall()
                if not rows:
                    return None
                return pd.DataFrame(rows, columns=[
                    "semana_fiscal", "fecha_inicio", "fecha_fin",
                    "tipo_promo", "categoria", "descripcion", "md_pct"
                ])

    @staticmethod
    def _ensure_tables(conn: Connection) -> None:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS promotion_calendars (
                    promo_id        TEXT PRIMARY KEY,
                    source_filename TEXT NOT NULL,
                    uploaded_at     TIMESTAMPTZ NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS promotion_records (
                    id              BIGSERIAL PRIMARY KEY,
                    promo_id        TEXT NOT NULL REFERENCES promotion_calendars(promo_id) ON DELETE CASCADE,
                    semana_fiscal   INTEGER NOT NULL,
                    fecha_inicio    DATE NOT NULL,
                    fecha_fin       DATE NOT NULL,
                    tipo_promo      TEXT NOT NULL,
                    categoria       TEXT NOT NULL,
                    descripcion     TEXT NOT NULL,
                    md_pct          DOUBLE PRECISION NOT NULL
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_promo_records_promo_id
                ON promotion_records(promo_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_promo_records_semana
                ON promotion_records(promo_id, semana_fiscal)
            """)
