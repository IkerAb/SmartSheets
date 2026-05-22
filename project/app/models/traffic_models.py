"""Domain DTOs for store traffic and conversion rate analysis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrafficRecord:
    semana_fiscal: int
    tienda: str
    trafico: int
    transacciones: int
    tasa_conversion_pct: float


@dataclass(frozen=True)
class TrafficPersistRequest:
    source_filename: str
    records: list[TrafficRecord]


@dataclass(frozen=True)
class TrafficPersistResult:
    traffic_id: str
    row_count: int
    semanas: int
    tiendas: list[str]


@dataclass(frozen=True)
class StoreTrafficPoint:
    tienda: str
    semana_fiscal: int | None
    trafico_total: int
    transacciones_total: int
    tasa_conversion_pct: float
    vs_promedio_pct: float      # diferencia vs promedio de todas las tiendas
    nivel_conversion: str       # "alto" | "medio" | "bajo"
    insight: str
