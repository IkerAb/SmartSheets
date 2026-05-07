## 1. Project foundation and scaffolding

- [x] 1.1 Create the complete `project/` directory structure with all required modules, docs, tests, notebook, and sample data folders.
- [x] 1.2 Add baseline backend bootstrap files (`app/main.py`, configuration, logging, package init files) and dependency manifests (`requirements.txt`, `.gitignore`).
- [x] 1.3 Configure Docker runtime (`Dockerfile`, `docker-compose.yml`) for local execution of the FastAPI service.
- [x] 1.5 Add PostgreSQL integration dependencies, DB configuration, and environment-variable settings for app and compose workflows.
- [x] 1.4 Add CI workflow (`.github/workflows/ci.yml`) to run linting and pytest on push and pull request events.

## 2. Data ingestion and validation pipeline

- [x] 2.1 Implement file handling utilities for CSV/XLSX upload parsing and persistence orchestration to PostgreSQL-backed dataset storage.
- [x] 2.2 Implement request validation for required columns (`fecha`, `producto`, `ventas`) and normalized schema conversion.
- [ ] 2.3 Build `POST /upload` route with clear success and validation error responses using Pydantic models.
- [ ] 2.5 Implement dataset metadata schema and lifecycle status tracking (`uploaded`, `validated`, `cleaned`, `failed`) with `dataset_id` response contract.
- [ ] 2.6 Implement atomic ingest transactions for metadata + cleaned rows and explicit failure handling for partial processing errors.
- [ ] 2.4 Add upload-focused tests covering valid CSV, valid XLSX, missing-column failures, and invalid dtype failures.

## 3. Analytics and anomaly detection services

- [ ] 3.1 Implement cleaning and aggregation services for daily/monthly rollups with missing-data handling.
- [ ] 3.2 Implement analysis service for total sales, sales by product, top products, monthly growth, and average ticket metrics.
- [ ] 3.3 Implement anomaly detection service using z-score or IQR with configurable thresholds for spikes and drops.
- [ ] 3.4 Implement natural-language insight generation and dashboard-ready `labels`/`values` output formatting.
- [ ] 3.5 Build `GET /insights` route and response contracts that combine KPI, anomaly, and narrative blocks.
- [ ] 3.6 Add analytics tests for service logic and endpoint behavior, including no-dataset error handling.

## 4. Forecasting and simulation capabilities

- [ ] 4.1 Implement forecasting service with statsmodels-first model pipeline and pluggable adapter for future prophet support.
- [ ] 4.2 Add support for configurable horizons, global forecasting, per-product forecasting, and confidence interval output.
- [ ] 4.3 Implement preprocessing path for aggregation mode selection (day/month) and missing-series completion before fitting.
- [ ] 4.4 Build `GET /forecast` route with typed request parameters and response schemas.
- [ ] 4.5 Implement `POST /simulate` scenario engine for price/volume adjustment inputs and baseline-vs-simulated comparisons.
- [ ] 4.6 Add forecasting and simulation tests for horizon logic, product filtering, confidence intervals, and validation errors.
- [ ] 4.7 Define forecasting feasibility guards (minimum history, sparse-series fallback) and structured warning metadata.

## 5. Operability, caching, and cross-cutting concerns

- [ ] 5.1 Implement cache layer keyed by `dataset_id` (or persisted immutable fingerprint) and request parameters for insights and forecast computations.
- [ ] 5.2 Add cache invalidation hooks triggered by successful dataset uploads.
- [ ] 5.3 Implement `GET /health` route with liveness/readiness response contract.
- [ ] 5.4 Wire shared error handling, structured logging, and service dependency injection across routes.
- [ ] 5.5 Add operability tests for cache hit/miss behavior and health endpoint availability.
- [ ] 5.6 Add explicit repository interfaces and implementations so routes/services never contain raw SQL or direct ORM coupling.

## 6. Documentation and delivery readiness

- [ ] 6.1 Write `README.md` with installation, local run instructions, endpoint descriptions, and curl examples for upload/insights/forecast/simulate/health.
- [ ] 6.2 Create architecture docs (`docs/architecture.md`) and ADRs (`docs/adr/`) for clean architecture and forecasting model decisions.
- [ ] 6.3 Provide example dataset(s) in `data/sample` and notebook starter content in `notebooks/exploration.ipynb`.
- [ ] 6.4 Document production scaling guidance (stateless API + external cache/storage + worker model) and frontend integration path (React/dashboard consumers).
- [ ] 6.5 Run full quality checks (lint/tests) and confirm OpenAPI coverage for all implemented endpoints.
- [ ] 6.6 Add integration tests with PostgreSQL (compose or test container) covering upload -> persisted dataset -> insights/forecast/simulate end-to-end flows.
