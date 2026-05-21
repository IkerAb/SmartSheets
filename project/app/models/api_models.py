"""
app/models/api_models.py
─────────────────────────
Pydantic v2 schemas para request params y response bodies.
Campos alineados con el frontend React (charts-dashboard branch).
"""
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
    pct: float              # era pct_of_total — frontend usa pct


class MonthlyGrowth(BaseModel):
    month: str
    sales: float            # era total — frontend usa sales
    mom_pct: float | None   # era pct_change — frontend usa mom_pct


class ChartData(BaseModel):
    labels: list[str]
    values: list[float]


class AnomalySummary(BaseModel):
    date: str
    value: float
    direction: str          # "spike" | "dip"
    severity: str           # "low" | "medium" | "high"
    zscore: float | None = None


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


# ── Forecast ──────────────────────────────────────────────────────────────────

class ForecastPoint(BaseModel):
    """Un punto de la serie combinada histórico + forecast para el gráfico."""
    date: str
    actual: float | None    # valor real (histórico), None en periodo futuro
    forecast: float | None  # valor predicho, None en periodo histórico
    lower: float | None
    upper: float | None


class ForecastResponse(BaseModel):
    dataset_id: str
    model: str              # "ets" | "naive"
    horizon: int
    aggregation: str        # "day" | "month"
    product: str | None
    confidence: float
    labels: list[str]       # fechas futuras
    values: list[float]     # predicción
    lower: list[float]      # intervalo inferior
    upper: list[float]      # intervalo superior
    mae: float | None = None
    warnings: list[str] = []
    series: list[ForecastPoint] = []   # combinado histórico+forecast para el chart


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
    """Objeto modifiers que espera el frontend en la respuesta."""
    price_modifier: float
    volume_modifier: float


class SimulateResponse(BaseModel):
    dataset_id: str
    base: ScenarioResult
    simulated: ScenarioResult
    delta_revenue: float
    delta_pct: float
    modifiers: SimulateModifiers    # era price_modifier/volume_modifier sueltos


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    database: str           # "connected" | "unreachable"
    uptime_seconds: float
