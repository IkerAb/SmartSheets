# Architecture — SmartSheets Forecasting API

## Layers

```
Routes  →  Services  →  Models / Repository  →  PostgreSQL
(HTTP)     (business)   (DTOs / persistence)    (data)
```

- **Routes**: thin HTTP adapters — validate input, call service, map to response.
- **Services**: pure Python business logic, no FastAPI imports.
- **Repository**: all SQL isolated here; services never touch raw DB.
- **Models**: Pydantic API schemas + dataclass domain DTOs.

## Data Flow

1. `POST /upload` → `DataLoaderService` → `PostgresDatasetRepository` → returns `dataset_id`
2. `GET /insights` → `AnalysisService` + `AnomalyDetector` → cached result
3. `GET /forecast` → `ForecastingService` (ETS / naive) → cached result
4. `POST /simulate` → apply modifiers → two `ForecastingService` calls → delta
5. `GET /health` → DB connectivity check + uptime

## Cache

In-memory dict with TTL (default 1h). Invalidated on each successful upload.
Migrating to Redis requires only replacing `app/services/cache.py` implementation.
