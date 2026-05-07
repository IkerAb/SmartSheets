## ADDED Requirements

### Requirement: Service SHALL expose health status endpoint
The system MUST provide a `GET /health` endpoint that reports application liveness and readiness for API consumers and platform probes.

#### Scenario: Healthy application status
- **WHEN** the application is running and dependencies are available
- **THEN** `GET /health` returns a healthy status response with service metadata

### Requirement: Expensive computations SHALL be cached
The system MUST cache insights and forecast results using keys derived from `dataset_id` (or immutable persisted fingerprint) and request parameters to avoid redundant recomputation.

#### Scenario: Cache hit for repeated forecast
- **WHEN** a forecast request repeats the same dataset fingerprint and parameters
- **THEN** the system returns cached results instead of recomputing the model output

#### Scenario: Cache invalidation on new upload
- **WHEN** a new dataset upload becomes active
- **THEN** cached analytics and forecast entries tied to previous dataset fingerprints are not reused

### Requirement: Routes SHALL remain transport-only adapters
The system MUST keep route handlers thin and free of business logic, delegating analytics, forecasting, anomaly detection, simulation, and persistence workflows to services.

#### Scenario: Route delegates to service contracts
- **WHEN** a request reaches `upload`, `insights`, `forecast`, or `simulate` routes
- **THEN** the route performs request validation and response mapping only, and all business rules execute in services

### Requirement: API contracts SHALL remain OpenAPI-documented
The system MUST expose endpoint contracts, request models, and response schemas through FastAPI-generated OpenAPI documentation.

#### Scenario: Schema visibility in OpenAPI
- **WHEN** a client accesses the OpenAPI document
- **THEN** upload, insights, forecast, simulate, and health endpoints include typed request/response schemas
