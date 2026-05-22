"""Pydantic v2 schemas alineados con el frontend React."""
from pydantic import BaseModel, Field


# ── Upload ────────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    dataset_id: str
    row_count: int
    columns: list[str]
    date_range: tuple[str, str]
    products: list[str]
    status: str
    message: str = "Dataset uploaded and processed successfully."


# ── Insights ──────────────────────────────────────────────────────────────────

class TopProduct(BaseModel):
    name: str
    total: float
    pct: float


class MonthlyGrowth(BaseModel):
    month: str
    sales: float
    mom_pct: float | None


class ChartData(BaseModel):
    labels: list[str]
    values: list[float]


class AnomalySummary(BaseModel):
    date: str
    value: float
    direction: str
    severity: str
    zscore: float | None = None


class StoreInsight(BaseModel):
    name: str
    total: float
    pct: float


class StoreInsights(BaseModel):
    top_store: StoreInsight | None
    bottom_store: StoreInsight | None
    all_stores: list[StoreInsight]


class InsightsResponse(BaseModel):
    dataset_id: str
    total_sales: float
    avg_ticket: float
    total_transactions: int
    top_products: list[TopProduct]
    monthly_growth: list[MonthlyGrowth]
    anomalies: list[AnomalySummary]
    natural_summary: str
    chart_ready: ChartData
    store_insights: StoreInsights | None = None


# ── Forecast ──────────────────────────────────────────────────────────────────

class ForecastPoint(BaseModel):
    date: str
    actual: float | None
    forecast: float | None
    lower: float | None
    upper: float | None


class ForecastResponse(BaseModel):
    dataset_id: str
    model: str
    horizon: int
    aggregation: str
    product: str | None
    confidence: float
    labels: list[str]
    values: list[float]
    lower: list[float]
    upper: list[float]
    mae: float | None = None
    warnings: list[str] = []
    series: list[ForecastPoint] = []


# ── Simulate ──────────────────────────────────────────────────────────────────

class SimulateRequest(BaseModel):
    dataset_id: str
    horizon: int = Field(default=30, ge=1, le=365)
    price_modifier: float = Field(default=1.0, ge=0.1, le=10.0)
    volume_modifier: float = Field(default=1.0, ge=0.1, le=10.0)
    product: str | None = None


class ScenarioResult(BaseModel):
    labels: list[str]
    values: list[float]
    total_projected: float


class SimulateModifiers(BaseModel):
    price_modifier: float
    volume_modifier: float


class SimulateResponse(BaseModel):
    dataset_id: str
    base: ScenarioResult
    simulated: ScenarioResult
    delta_revenue: float
    delta_pct: float
    modifiers: SimulateModifiers


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    database: str
    uptime_seconds: float


# ── Promotions ────────────────────────────────────────────────────────────────

class PromoUploadResponse(BaseModel):
    promo_id: str
    row_count: int
    semanas: int
    categorias: list[str]
    message: str = "Calendario de promociones cargado correctamente."


class PromoRecord(BaseModel):
    semana_fiscal: int
    fecha_inicio: str
    fecha_fin: str
    tipo_promo: str        # "WkndPromo" | "OtherPromo" | "DD"
    categoria: str
    descripcion: str
    md_pct: float


class WeekPromoResponse(BaseModel):
    promo_id: str
    semana_fiscal: int
    fecha_inicio: str
    fecha_fin: str
    wknd_promos: list[PromoRecord]
    other_promos: list[PromoRecord]
    daily_deals: list[PromoRecord]
    avg_md_pct: float
    categorias_en_promo: list[str]


class FiscalWeekSales(BaseModel):
    semana_fiscal: int
    fecha_inicio: str
    fecha_fin: str
    total_sales: float
    transactions: int
    has_promo: bool
    avg_md_pct: float
    promos: list[PromoRecord]


class FiscalCalendarResponse(BaseModel):
    dataset_id: str
    promo_id: str
    weeks: list[FiscalWeekSales]


# ── Inventory / Sell-Through ──────────────────────────────────────────────────

class InventoryUploadResponse(BaseModel):
    inventory_id: str
    row_count: int
    semanas: int
    categorias: list[str]
    message: str = "Inventario cargado correctamente."


class SellThroughRow(BaseModel):
    categoria: str
    inventario_inicial: int
    unidades_vendidas: int
    sell_through_pct: float
    nivel: str          # "alto" | "medio" | "bajo"
    tiene_promo: bool
    tipo_promos: list[str]
    md_promedio: float
    insight: str


class SellThroughResponse(BaseModel):
    inventory_id: str
    promo_id: str | None
    semana_fiscal: int | None
    rows: list[SellThroughRow]
    resumen: str


# ── Traffic / Conversion Rate ─────────────────────────────────────────────────

class TrafficUploadResponse(BaseModel):
    traffic_id: str
    row_count: int
    semanas: int
    tiendas: list[str]
    message: str = "Tráfico cargado correctamente."


class StoreTrafficRow(BaseModel):
    tienda: str
    trafico_total: int
    transacciones_total: int
    tasa_conversion_pct: float
    vs_promedio_pct: float
    nivel_conversion: str
    insight: str


class TrafficResponse(BaseModel):
    traffic_id: str
    semana_fiscal: int | None
    rows: list[StoreTrafficRow]
    avg_conversion: float
    best_store: str
    worst_store: str
