"""
app/models/api_models.py
─────────────────────────
Pydantic v2 schemas para request params y response bodies de todos los endpoints.
Separados de dataset_models.py que contiene los DTOs de dominio interno.
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
    pct_of_total: float


class MonthlyGrowth(BaseModel):
    month: str
    total: float
    pct_change: float | None


class ChartData(BaseModel):
    labels: list[str]
    values: list[float]


class AnomalySummary(BaseModel):
    date: str
    value: float
    direction: str       # "spike" | "dip"
    severity: str        # "low" | "medium" | "high"
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

class ForecastResponse(BaseModel):
    dataset_id: str
    model: str                   # "ets" | "sarimax" | "naive"
    horizon: int
    aggregation: str             # "day" | "month"
    product: str | None
    confidence: float
    labels: list[str]
    values: list[float]
    lower: list[float]
    upper: list[float]
    mae: float | None = None
    warnings: list[str] = []


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


class SimulateResponse(BaseModel):
    dataset_id: str
    base: ScenarioResult
    simulated: ScenarioResult
    delta_revenue: float
    delta_pct: float
    price_modifier: float
    volume_modifier: float


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str
    database: str          # "connected" | "unreachable"
    uptime_seconds: float
