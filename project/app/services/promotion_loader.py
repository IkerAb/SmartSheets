"""Promotion calendar ingestion service."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import pandas as pd

from app.models.promotion_models import (
    PromotionPersistRequest,
    PromotionPersistResult,
    PromotionRecord,
)
from app.repositories.promotion_repository import PostgresPromotionRepository


@dataclass(frozen=True)
class PromoUploadPayload:
    filename: str
    content: bytes


VALID_TIPOS = {"WkndPromo", "OtherPromo", "DD"}
REQUIRED_COLS = {"semana_fiscal", "fecha_inicio", "fecha_fin", "tipo_promo", "categoria", "descripcion", "md_pct"}


class PromotionLoaderService:

    def __init__(self, repository: PostgresPromotionRepository | None = None) -> None:
        self._repository = repository or PostgresPromotionRepository()

    def ingest_and_persist(self, payload: PromoUploadPayload) -> PromotionPersistResult:
        df = self._parse(payload)
        df = self._validate(df)
        records = self._to_records(df)
        request = PromotionPersistRequest(
            source_filename=payload.filename,
            records=records,
        )
        return self._repository.persist_promotions(request)

    def _parse(self, payload: PromoUploadPayload) -> pd.DataFrame:
        import io
        ext = payload.filename.rsplit(".", 1)[-1].lower()
        buf = io.BytesIO(payload.content)
        if ext == "csv":
            try:
                df = pd.read_csv(buf, encoding="utf-8")
            except UnicodeDecodeError:
                buf.seek(0)
                df = pd.read_csv(buf, encoding="latin-1")
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(buf, engine="openpyxl")
        else:
            raise ValueError(f"Extensión no soportada: .{ext}. Usa CSV o XLSX.")
        df.columns = [c.lower().strip() for c in df.columns]
        return df

    def _validate(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            raise ValueError(f"Columnas faltantes: {missing}")

        df["semana_fiscal"] = pd.to_numeric(df["semana_fiscal"], errors="coerce")
        df = df.dropna(subset=["semana_fiscal"])
        df["semana_fiscal"] = df["semana_fiscal"].astype(int)

        invalid_weeks = df[~df["semana_fiscal"].between(1, 52)]
        if len(invalid_weeks):
            raise ValueError(f"Semanas fiscales inválidas: {invalid_weeks['semana_fiscal'].unique().tolist()}")

        df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce").dt.date
        df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce").dt.date
        df = df.dropna(subset=["fecha_inicio", "fecha_fin"])

        invalid_tipos = set(df["tipo_promo"].unique()) - VALID_TIPOS
        if invalid_tipos:
            raise ValueError(f"Tipos de promo inválidos: {invalid_tipos}. Usa: {VALID_TIPOS}")

        df["md_pct"] = pd.to_numeric(df["md_pct"], errors="coerce").fillna(0)
        df["descripcion"] = df["descripcion"].astype(str).str.strip()
        df["categoria"] = df["categoria"].astype(str).str.strip()

        return df

    def _to_records(self, df: pd.DataFrame) -> list[PromotionRecord]:
        return [
            PromotionRecord(
                semana_fiscal=int(row.semana_fiscal),
                fecha_inicio=row.fecha_inicio,
                fecha_fin=row.fecha_fin,
                tipo_promo=str(row.tipo_promo),
                categoria=str(row.categoria),
                descripcion=str(row.descripcion),
                md_pct=float(row.md_pct),
            )
            for row in df.itertuples(index=False)
        ]
