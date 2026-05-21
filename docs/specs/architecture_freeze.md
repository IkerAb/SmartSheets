# Architecture Freeze

## System Overview
Sales Analytics & Forecasting API built with FastAPI, PostgreSQL, and Docker Compose.

## Core Stack
- Python 3.11+
- FastAPI
- PostgreSQL
- Docker Compose
- pandas
- scikit-learn
- statsmodels/Prophet

## Architectural Principles
- Clean architecture
- Separation of concerns
- Thin routes
- Reusable services
- PostgreSQL as single source of truth

## Project Structure
app/
  routes/
  services/
  repositories/
  models/
  utils/
  core/

## Endpoint Contracts
- POST /upload
- GET /insights
- GET /forecast
- POST /simulate
- GET /health

All non-upload endpoints require dataset_id.

## Dataset Lifecycle
UPLOADED
→ VALIDATED
→ CLEANED
→ ANALYZED
→ FORECAST_READY

## Business Rules
- Routes contain no business logic
- Forecasting only consumes validated datasets
- Services are infrastructure-independent
- DTO contracts isolate repositories from services

## Persistence
- PostgreSQL stores datasets and metadata
- Docker Compose orchestrates API + DB
- Persistent volumes enabled

## Cache Rules
- Cache key includes dataset_id + forecast params
- Cache invalidates on dataset update

## Forecasting Constraints
- Daily aggregated sales
- Minimum historical data required
- Invalid or sparse datasets rejected

## Operational Safeguards
- DB health-gated startup
- Validation before persistence
- Failure-safe dataset transitions

## Forbidden Patterns
- SQL logic inside routes
- Direct ORM leakage into services
- Shared mutable global state