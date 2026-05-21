# ADR-0002: PostgreSQL as single source of truth

**Status**: Accepted

## Context
In-memory storage loses data on restart and breaks multi-instance deployments.

## Decision
Persist all uploaded and cleaned datasets in PostgreSQL.
All analytics and forecast services read from DB via repository interface.

## Consequences
- Deterministic, cross-request consistent data.
- Repository interface keeps services testable without a real DB (mock in tests).
- Dataset lifecycle tracked via `status` field (uploaded → cleaned | failed).
