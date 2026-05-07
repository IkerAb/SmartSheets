## ADDED Requirements

### Requirement: Simulation endpoint SHALL support what-if scenarios
The system MUST provide a `POST /simulate` endpoint that evaluates scenario adjustments such as price and volume changes against baseline sales projections.

#### Scenario: Simulate volume increase
- **WHEN** a client submits a simulation request with positive volume delta
- **THEN** the system returns adjusted projected sales and impact versus baseline

#### Scenario: Simulate price decrease
- **WHEN** a client submits a simulation request with negative price delta
- **THEN** the system returns scenario projections and quantified variance compared with baseline

### Requirement: Simulation responses SHALL include comparative outputs
The system MUST return baseline and simulated results in a comparable structure suitable for dashboard consumption.

#### Scenario: Comparative response formatting
- **WHEN** simulation completes successfully
- **THEN** the response includes side-by-side baseline and scenario `labels` and `values` series plus total impact metrics

### Requirement: Simulation SHALL validate scenario parameters
The system MUST validate scenario request parameters, including allowed ranges and required fields, before running simulation logic.

#### Scenario: Invalid simulation parameter range
- **WHEN** scenario inputs exceed supported percentage or absolute ranges
- **THEN** the system rejects the request with clear validation error details
