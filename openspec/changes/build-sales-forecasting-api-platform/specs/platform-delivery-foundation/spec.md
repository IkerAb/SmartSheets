## ADDED Requirements

### Requirement: Project SHALL include defined production-oriented repository structure
The system MUST provide the required modular project layout under `project/`, including application modules, tests, data samples, notebooks, architecture docs, ADRs, and delivery artifacts.

#### Scenario: Required structure is present
- **WHEN** repository structure is inspected
- **THEN** all mandated paths and baseline files are present for implementation and delivery workflows

### Requirement: Service SHALL be containerizable for local and CI usage
The system MUST include a functional `Dockerfile` and `docker-compose.yml` to build and run the API with reproducible dependencies.

#### Scenario: Container build succeeds
- **WHEN** the Docker image is built using the provided Dockerfile
- **THEN** the build completes successfully and the API application can start in the container

#### Scenario: Compose orchestrates API and PostgreSQL
- **WHEN** the local stack starts with docker compose
- **THEN** FastAPI and PostgreSQL containers run with configured environment variables, persistent database volume, and startup dependency wiring

### Requirement: CI pipeline SHALL enforce baseline quality gates
The system MUST include a GitHub Actions workflow that executes linting and tests on pull requests and relevant branch pushes.

#### Scenario: CI runs lint and tests
- **WHEN** code is pushed or a pull request is opened
- **THEN** the workflow runs lint and pytest jobs and reports pass/fail status

### Requirement: Documentation SHALL support implementation and operations
The system MUST include a comprehensive README with setup and curl usage examples, plus ADR documents that justify architecture and forecasting model choices.

#### Scenario: README provides executable usage
- **WHEN** a developer follows README instructions
- **THEN** they can install dependencies, run the API, and call key endpoints with provided curl examples

#### Scenario: ADRs capture core decisions
- **WHEN** architecture documentation is reviewed
- **THEN** decision records explain rationale, alternatives, and implications for architecture and model selection
