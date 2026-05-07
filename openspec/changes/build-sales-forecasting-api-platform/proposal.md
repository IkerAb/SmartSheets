## Why

The team needs a production-ready analytics and forecasting backend that transforms raw sales spreadsheets into trustworthy operational insights and future demand projections. This change is needed now to reduce manual analysis time, standardize forecasting quality, and enable dashboard and product integrations through stable APIs.

## What Changes

- Create a modular FastAPI service (Python 3.11+) with clean architecture boundaries, Pydantic typing, and OpenAPI documentation.
- Add dataset ingestion via `POST /upload` for CSV/XLSX files, schema validation (`fecha`, `producto`, `ventas`), and PostgreSQL persistence as the single source of truth.
- Add `GET /insights` for aggregate business metrics (total sales, sales by product, top products, monthly growth, average ticket), anomaly surfacing (drops/spikes), dashboard-ready series, and natural-language narrative summaries.
- Add `GET /forecast` for global and per-product time-series forecasting with configurable horizon and confidence intervals, including missing-data handling and day/month aggregation support.
- Add `POST /simulate` for scenario simulation (price/volume deltas) based on forecast and baseline metrics.
- Add `GET /health`, explicit dataset state management (`dataset_id`), and caching of expensive analysis/forecast computations to reduce repeated processing latency.
- Establish production engineering baseline: Docker, docker-compose, CI (lint + tests), pytest coverage, architecture docs, ADRs, sample data, and notebook exploration scaffolding.

## Capabilities

### New Capabilities
- `sales-data-ingestion`: Upload, validate, clean, and persist sales datasets from CSV/Excel in PostgreSQL with strict column and format validation.
- `sales-insights-analytics`: Compute descriptive KPIs, anomaly markers, dashboard payloads, and automated narrative insights.
- `sales-forecasting`: Produce configurable global/product forecasts with confidence bands and robust preprocessing for time series.
- `sales-scenario-simulation`: Evaluate what-if scenarios (price/volume changes) and return comparable projected outcomes.
- `analytics-api-operability`: Provide health checks, dataset lifecycle/state consistency rules, caching behavior, API contracts, and operational readiness requirements.
- `postgres-persistence-layer`: Define relational schema, repository boundaries, upload/processing tracking, and transaction-safe dataset workflows.
- `platform-delivery-foundation`: Define repository layout, test strategy, containerization, CI workflow, and documentation baseline.

### Modified Capabilities
None.

## Impact

- Affects application architecture under `project/` with new API routes, domain services, persistence/repository layer, models, utilities, and operational modules.
- Introduces data stack dependencies: pandas, numpy, scikit-learn, statsmodels/prophet, PostgreSQL driver/ORM tooling, and testing/linting tooling.
- Defines external API surface for upload, insights, forecast, simulate, and health endpoints.
- Adds infrastructure artifacts (`Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`) and documentation artifacts (`README.md`, `docs/adr`, `architecture.md`).
- Enables downstream consumption by BI dashboards and future React frontend via stable JSON contracts.
