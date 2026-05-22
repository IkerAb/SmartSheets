"""Domain DTOs for promotion calendar ingestion and persistence."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class PromoType(StrEnum):
    WKND_PROMO  = "WkndPromo"
    OTHER_PROMO = "OtherPromo"
    DD          = "DD"


@dataclass(frozen=True)
class PromotionRecord:
    """Una fila del calendario de promociones."""
    semana_fiscal: int
    fecha_inicio: date
    fecha_fin: date
    tipo_promo: str
    categoria: str
    descripcion: str
    md_pct: float


@dataclass(frozen=True)
class PromotionPersistRequest:
    source_filename: str
    records: list[PromotionRecord]


@dataclass(frozen=True)
class PromotionPersistResult:
    promo_id: str
    row_count: int
    semanas: int              # cuántas semanas fiscales distintas
    categorias: list[str]


@dataclass(frozen=True)
class PromotionMetadata:
    promo_id: str
    source_filename: str
    uploaded_at: str
    row_count: int
    semanas: int
    categorias: list[str]
