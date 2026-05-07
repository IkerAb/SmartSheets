## ADDED Requirements

### Requirement: Upload endpoint SHALL accept sales files
The system MUST provide a `POST /upload` endpoint that accepts sales datasets in CSV and Excel formats, persists dataset metadata and cleaned records in PostgreSQL, and returns a stable `dataset_id` for downstream workflows.

#### Scenario: Successful CSV upload
- **WHEN** a client uploads a valid CSV file through `POST /upload`
- **THEN** the system stores dataset metadata and cleaned rows in PostgreSQL and returns a success response with `dataset_id`, row count, and column metadata

#### Scenario: Successful Excel upload
- **WHEN** a client uploads a valid Excel file through `POST /upload`
- **THEN** the system parses the first configured sheet, stores the normalized dataset in PostgreSQL, and returns a success response with `dataset_id`

### Requirement: Upload validation SHALL enforce required schema
The system MUST validate that uploaded data contains the required columns `fecha`, `producto`, and `ventas`, with parseable date values and numeric sales values.

#### Scenario: Missing required column
- **WHEN** an uploaded file does not contain one or more required columns
- **THEN** the system rejects the request with a validation error that lists missing columns

#### Scenario: Invalid data types
- **WHEN** uploaded rows include unparseable dates or non-numeric `ventas` values
- **THEN** the system rejects the upload and reports field-level validation issues

### Requirement: Ingestion pipeline SHALL normalize time-series input
The system MUST normalize accepted datasets into a canonical internal representation suitable for day and month aggregation with missing-data handling.

#### Scenario: Dataset normalization for downstream services
- **WHEN** a valid dataset is uploaded
- **THEN** the system converts dates to normalized datetime values, standardizes product identifiers, and preserves a canonical schema used by analytics and forecasting services

#### Scenario: Missing dates in time series
- **WHEN** the canonical dataset is prepared for time-series operations
- **THEN** the system fills temporal gaps according to configured missing-data strategy before computing forecast-ready series

### Requirement: Dataset lifecycle state SHALL be tracked durably
The system MUST track upload and processing lifecycle in dataset metadata with statuses that prevent downstream use of incomplete datasets.

#### Scenario: Dataset marked cleaned and ready
- **WHEN** validation and cleaning complete successfully
- **THEN** the dataset status is set to `cleaned` and the returned `dataset_id` is eligible for analytics, forecasting, anomaly detection, and simulation

#### Scenario: Processing failure
- **WHEN** validation or cleaning fails after upload start
- **THEN** the dataset status is set to `failed` with an error reason and downstream routes reject that `dataset_id`
