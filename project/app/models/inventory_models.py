"""Domain DTOs for inventory and sell-through analysis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryRecord:
    semana_fiscal: int
    categoria: str
    tienda: str
    inventario_inicial: int
    unidades_vendidas: int


@dataclass(frozen=True)
class InventoryPersistRequest:
    source_filename: str
    records: list[InventoryRecord]


@dataclass(frozen=True)
class InventoryPersistResult:
    inventory_id: str
    row_count: int
    semanas: int
    categorias: list[str]


@dataclass(frozen=True)
class SellThroughPoint:
    semana_fiscal: int
    categoria: str
    tienda: str | None
    inventario_inicial: int
    unidades_vendidas: int
    sell_through_pct: float
    nivel: str   # "alto" | "medio" | "bajo"
    tiene_promo: bool
    tipo_promos: list[str]
    md_promedio: float
    insight: str
