## ADDED Requirements

### Requirement: Insights endpoint SHALL provide core sales KPIs
The system MUST provide a `GET /insights` endpoint that returns total sales, sales by product, top products, monthly growth, and average ticket from the active dataset.

#### Scenario: Compute KPI summary
- **WHEN** a client requests `GET /insights` with a valid active dataset
- **THEN** the system returns all mandatory KPI fields in a single response payload

#### Scenario: No active dataset
- **WHEN** a client requests `GET /insights` before any successful upload
- **THEN** the system responds with an error indicating that dataset upload is required

### Requirement: Insights endpoint SHALL include anomaly signals
The system MUST detect strong drops and abnormal peaks using z-score or IQR methods and include anomaly markers in the insights output.

#### Scenario: Detect high-spike anomaly
- **WHEN** sales values exceed configured anomaly threshold
- **THEN** the system marks the affected periods as anomalies and includes reason metadata in the response

#### Scenario: Detect strong-drop anomaly
- **WHEN** sales values fall below configured anomaly threshold
- **THEN** the system identifies affected periods as drops and returns them in anomaly sections

### Requirement: Insights output SHALL be dashboard-ready and narrative-ready
The system MUST return chart-friendly arrays (`labels`, `values`) and generated natural-language insights that summarize key patterns and risks.

#### Scenario: Dashboard payload formatting
- **WHEN** insights are generated
- **THEN** each chartable metric includes aligned `labels` and `values` arrays for direct dashboard ingestion

#### Scenario: Natural-language summary generation
- **WHEN** KPI and anomaly computations are complete
- **THEN** the response includes a concise narrative summary describing trend direction, best-performing products, and anomaly highlights
