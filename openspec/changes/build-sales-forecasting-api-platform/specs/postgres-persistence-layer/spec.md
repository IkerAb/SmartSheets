## ADDED Requirements

### Requirement: PostgreSQL SHALL be the single source of truth for datasets
The system MUST persist dataset metadata and cleaned sales records in PostgreSQL and MUST use persisted data as the canonical input for analytics, forecasting, anomaly detection, and simulation.

#### Scenario: Dataset retrieved from canonical storage
- **WHEN** downstream workflows execute with a valid `dataset_id`
- **THEN** the system loads data from PostgreSQL through repository interfaces rather than in-memory active state

### Requirement: Dataset metadata SHALL track processing lifecycle
The system MUST store dataset metadata including identifier, upload timestamp, processing timestamps, processing status, and failure reason when applicable.

#### Scenario: Metadata captures successful processing
- **WHEN** upload validation and cleaning succeed
- **THEN** dataset metadata includes `dataset_id`, `uploaded_at`, `processed_at`, and status `cleaned`

#### Scenario: Metadata captures failed processing
- **WHEN** upload processing fails
- **THEN** dataset metadata includes status `failed` and a machine-readable error reason

### Requirement: Persistence layer SHALL isolate infrastructure concerns
The system MUST implement database access through a dedicated data-access/repository layer so application services remain independent from SQL/ORM implementation details.

#### Scenario: Service uses repository contract
- **WHEN** application services request dataset reads or writes
- **THEN** they depend on typed repository interfaces and do not execute raw SQL in service logic

### Requirement: Dataset writes SHALL be transactionally consistent
The system MUST commit metadata and cleaned sales rows atomically so partial processing does not create inconsistent dataset state.

#### Scenario: Atomic ingest commit
- **WHEN** upload processing completes successfully
- **THEN** metadata and cleaned rows are committed in one transaction and dataset status is `cleaned`

#### Scenario: Rollback on failure
- **WHEN** an error occurs before processing completion
- **THEN** partial writes are rolled back or dataset is explicitly marked `failed` with no ambiguous intermediate state
