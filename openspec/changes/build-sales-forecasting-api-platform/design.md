## Context

The change introduces a full production-grade backend for sales analytics and forecasting from spreadsheet inputs. The current state has no standardized ingestion-to-insight pipeline, no consistent forecasting API, and no operational baseline (containerization, CI, and testing strategy) for reliable delivery.

Primary constraints:
- Backend stack must use FastAPI and Python 3.11+ with modular clean architecture.
- Data processing and forecasting must use pandas, numpy, scikit-learn, and statsmodels or prophet.
- API contracts must support upload, insights, forecasting, simulation, and health checks with dashboard-ready outputs.
- Forecasting and analytics must support global and per-product views, anomaly detection, and missing data handling.
- PostgreSQL must act as the single source of truth for uploaded and cleaned datasets across all workflows.

Stakeholders:
- Data/BI consumers that need reliable metrics and chart-friendly responses.
- Product teams that need stable endpoints for frontend/dashboard integration.
- Engineering/DevOps teams responsible for operability, repeatability, and test confidence.

## Goals / Non-Goals

**Goals:**
- Provide an end-to-end pipeline from raw CSV/XLSX ingestion to validated analytics and forecasting APIs.
- Establish clean architecture boundaries (`routes` -> `services` -> `models/utils`) to keep business logic testable.
- Support configurable forecast horizons with confidence intervals for global and product-specific time series.
- Deliver operational readiness through caching, health endpoint, Docker, docker-compose, CI, and pytest-based tests.
- Produce natural-language summaries and dashboard-friendly `labels`/`values` payloads for downstream consumers.

**Non-Goals:**
- Building a production frontend in this change (only API-ready contracts and guidance).
- Implementing distributed storage, message queues, or multi-region deployment in v1.
- Guaranteeing model retraining automation and MLOps orchestration beyond basic in-process model execution.

## Decisions

1. **Adopt layered clean architecture under `project/app`**
   - **Decision**: Keep transport logic in `routes`, business logic in `services`, schema contracts in `models`, and reusable helpers in `utils/core`.
   - **Rationale**: Enables isolated unit testing, easier code ownership, and predictable extension points.
   - **Alternatives considered**:
     - Single-file FastAPI app: rejected due to maintainability and testing fragility.
     - Heavy domain framework: rejected for unnecessary complexity at this stage.

2. **Use PostgreSQL-backed canonical dataset model with explicit dataset identity**
   - **Decision**: Convert uploaded files to a canonical dataset, persist clean records in PostgreSQL, and return a `dataset_id` that all downstream routes (`/insights`, `/forecast`, `/simulate`) must consume.
   - **Rationale**: Database-backed state avoids cross-request inconsistency and enables deterministic data boundaries for analytics and forecasting services.
   - **Alternatives considered**:
     - In-memory active dataset: rejected due to concurrency risk and poor multi-instance consistency.
     - Late normalization per endpoint: rejected because duplicated validation logic increases defect risk.

3. **Introduce repository/data-access layer between services and PostgreSQL**
   - **Decision**: Add persistence interfaces for dataset metadata and cleaned sales rows. Services consume repository contracts instead of direct SQL/ORM calls.
   - **Rationale**: Preserves clean architecture by isolating infrastructure concerns and keeping services reusable/testable.
   - **Alternatives considered**:
     - Direct DB calls from routes: rejected because it leaks business logic and weakens testability.
     - Direct DB calls from analytics/forecast services: rejected due to coupling and mocking complexity.

4. **Use statsmodels-first forecasting service with pluggable backend**
   - **Decision**: Implement a forecasting adapter pattern with a baseline model in statsmodels (e.g., ETS/SARIMAX depending on data shape), keeping a pluggable path for prophet.
   - **Rationale**: statsmodels is broadly available, deterministic, and suitable for production service packaging; adapter keeps future flexibility.
   - **Alternatives considered**:
     - Prophet-only: rejected due to packaging/runtime constraints in some deployment environments.
     - Naive moving average only: rejected because confidence intervals and seasonality handling would be insufficient.

5. **Cache expensive analytics and forecast computations**
   - **Decision**: Introduce service-level cache keys based on `dataset_id` (or immutable dataset fingerprint from persistence) + endpoint parameters (horizon, product, aggregation).
   - **Rationale**: Reduces repeated CPU cost and latency for common dashboard polling patterns.
   - **Alternatives considered**:
     - No cache: rejected due to avoidable recomputation.
     - External Redis from day one: deferred to keep initial deployment simpler while preserving extension path.

6. **Expose dashboard-oriented response contracts**
   - **Decision**: Standardize selected response blocks as arrays of `labels` and `values` plus machine-readable summary fields.
   - **Rationale**: Minimizes frontend transformation logic and promotes consistent chart consumption.
   - **Alternatives considered**:
     - Raw table-only outputs: rejected as they shift unnecessary work to clients.

7. **Quality and operability as first-class artifacts**
   - **Decision**: Include pytest endpoint/service coverage, linting in CI, Dockerized runtime, and ADR documentation in the same change.
   - **Rationale**: Prevents architecture drift and ensures the implementation is deployable, not just functional on local machines.
   - **Alternatives considered**:
     - Postpone CI/docs: rejected because it creates rework and lowers confidence for integration.

## Risks / Trade-offs

- **[Risk] Forecast quality varies across sparse products** -> **Mitigation**: enforce minimum-history checks, fallback model strategy, and informative API warnings.
- **[Risk] Concurrent uploads may produce inconsistent processing state** -> **Mitigation**: transaction boundaries, dataset status field (`uploaded`, `validated`, `cleaned`, `failed`), and immutable dataset snapshots once marked `cleaned`.
- **[Risk] Partial processing failures can leave stale rows** -> **Mitigation**: stage rows in transaction and promote dataset status only on commit; capture failure reason in metadata.
- **[Risk] Cache staleness after new uploads** -> **Mitigation**: dataset fingerprinting and cache invalidation on each successful upload.
- **[Risk] Anomaly false positives with simple z-score/IQR** -> **Mitigation**: expose configurable thresholds and include contextual narrative rather than binary alarms only.
- **[Trade-off] Strong validation can reject dirty real-world files** -> **Mitigation**: return explicit validation errors and document acceptable schemas with examples.
- **[Trade-off] Rich API contracts increase payload size** -> **Mitigation**: keep optional sections and enable selective response fields in later iterations.
