## ADDED Requirements

### Requirement: Forecast endpoint SHALL provide configurable horizons
The system MUST provide a `GET /forecast` endpoint that accepts a forecast horizon parameter and returns projected sales for the requested number of future periods.

#### Scenario: Default horizon forecast
- **WHEN** a client requests `GET /forecast` without specifying horizon
- **THEN** the system uses the default horizon configuration and returns predicted values

#### Scenario: Custom horizon forecast
- **WHEN** a client requests `GET /forecast` with a valid custom horizon (for example 30 days)
- **THEN** the system returns predictions for exactly the requested horizon length

### Requirement: Forecast service SHALL return confidence intervals
The system MUST include lower and upper confidence bounds for each predicted period in forecast responses.

#### Scenario: Confidence interval in response
- **WHEN** forecast generation succeeds
- **THEN** each forecast point includes prediction value, lower bound, and upper bound fields

### Requirement: Forecasting SHALL support global and per-product modes
The system MUST allow forecasting over the full dataset and for a specific product segment through request parameters.

#### Scenario: Global forecast mode
- **WHEN** a client requests forecast without a product filter
- **THEN** the system computes predictions using aggregated global sales history

#### Scenario: Product forecast mode
- **WHEN** a client requests forecast with a valid product identifier
- **THEN** the system computes predictions only from that product's time-series history

### Requirement: Forecasting service SHALL consume persistence-backed clean datasets only
The system MUST execute forecasting from a cleaned dataset retrieved through a persistence abstraction and MUST NOT depend on route-level or infrastructure-specific objects.

#### Scenario: Forecast service input contract
- **WHEN** forecasting is invoked from the application layer
- **THEN** the service receives a `dataset_id`, forecast parameters, and a clean time-series dataset from repository contracts rather than direct HTTP payloads or ORM session objects

#### Scenario: Dataset not ready for forecasting
- **WHEN** the requested `dataset_id` is not in `cleaned` status
- **THEN** the system rejects forecast execution with a clear domain error

### Requirement: Forecast preprocessing SHALL handle missing data and aggregation
The system MUST preprocess time series by applying configured day/month aggregation and missing-data handling before model fitting.

#### Scenario: Daily aggregation processing
- **WHEN** forecast is requested with daily aggregation mode
- **THEN** the system constructs a complete daily series and applies missing-value strategy before training

#### Scenario: Monthly aggregation processing
- **WHEN** forecast is requested with monthly aggregation mode
- **THEN** the system constructs a monthly series and applies missing-value strategy before training
