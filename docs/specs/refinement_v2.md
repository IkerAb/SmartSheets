# Refinement V2 — PostgreSQL Integration & Architecture Stabilization

## Objective

Refine and stabilize the Sales Analytics & Forecasting API architecture after the initial explore phase by introducing PostgreSQL persistence and formalizing operational boundaries.

The refinement focuses on:
- state management consistency
- persistence architecture
- service contracts
- forecasting constraints
- Docker orchestration
- operational stability

---

# Architectural Evolution

## Previous Limitation

The original proposal relied on temporary or in-memory dataset handling, creating ambiguity around:
- dataset persistence
- multi-request consistency
- forecasting reproducibility
- cache invalidation
- concurrent workflows

---

# PostgreSQL as Source of Truth

## Architectural Decision

PostgreSQL is now the official single source of truth for:
- uploaded datasets
- cleaned datasets
- dataset metadata
- processing status

The persistence layer is managed through Docker Compose.

---

# Persistence Strategy

## Core Principle

All analytics and forecasting workflows consume persisted, validated datasets from PostgreSQL instead of transient in-memory data.

---

# Database Responsibilities

## PostgreSQL Stores

### Sales Records
- date
- product
- sales
- dataset_id
- ingestion metadata

### Dataset Metadata
- dataset_id
- upload status
- uploaded_at
- processed_at
- error_reason

---

# State Management Refinement

## Mandatory dataset_id Contract

All business endpoints now require explicit `dataset_id`.

Applies to:
- insights
- forecast
- simulation
- anomaly workflows

---

# Benefits

- deterministic workflows
- dataset traceability
- forecasting reproducibility
- cache consistency
- concurrent upload safety

---

# Service Boundary Refinement

## Clean Architecture Enforcement

### Routes
Responsible only for:
- request validation
- response serialization
- service invocation

### Services
Responsible for:
- business workflows
- forecasting
- analytics
- anomaly detection
- simulations

### Repositories
Responsible for:
- PostgreSQL interaction
- persistence abstraction
- DTO mapping

### Utilities
Restricted to:
- generic helpers
- file handling
- validators

---

# Repository Pattern Introduction

## Goal

Prevent ORM/database leakage into business services.

### Rule
Services never interact directly with ORM models or raw SQL.

Repositories expose DTO-based contracts only.

---

# Forecasting Constraints

## Formalized Rules

### Forecast Eligibility
Forecasting requires:
- minimum historical observations
- valid temporal continuity
- supported aggregation frequency

### Fallback Hierarchy
If forecasting conditions fail:
1. fallback forecasting strategy
2. warning metadata returned
3. forecast rejection for invalid datasets

---

# Date Parsing Policy

## Accepted Formats

The system formalizes:
- accepted date formats
- timezone handling
- normalization rules

Invalid temporal formats trigger validation errors before persistence.

---

# Docker Compose Orchestration

## Infrastructure Components

### fastapi-app
Application container.

### postgres-db
Persistent PostgreSQL container.

---

# Operational Requirements

## Compose Rules

- persistent database volumes
- environment-based configuration
- startup dependency ordering
- DB health-gated startup

---

# Cache & Consistency Refinement

## Cache Rules

Cache keys include:
- dataset_id
- forecast parameters
- aggregation scope

Cache invalidates when:
- dataset updates occur
- processing lifecycle changes

---

# Operational Risk Analysis

## Identified Risks

- concurrent uploads
- stale cached forecasts
- partial ingestion failures
- malformed datasets
- forecasting over sparse data

---

# Mitigation Strategy

- lifecycle status tracking
- validation before persistence
- dataset-level isolation
- explicit failure metadata
- repository boundaries

---

# Testing Refinement

## Required Coverage Areas

- repository integration tests
- upload validation tests
- forecasting workflows
- anomaly detection
- API contract tests
- Docker orchestration validation

---

# Scalability & Extensibility

The architecture now supports future extension for:
- dashboards
- authentication
- multi-user workflows
- frontend integration
- analytics expansion

without major architectural rewrites.

---

# ADR Addition

A new ADR is required documenting:
- PostgreSQL as source of truth
- repository pattern adoption
- persistence rationale
- operational trade-offs

---

# Final Assessment

The architecture is now operationally stable, modular, persistence-aware, and implementation-ready.

Core concerns resolved:
- state management
- persistence consistency
- service boundaries
- forecasting constraints
- orchestration stability

The project is now suitable for:
- task generation
- incremental implementation
- production-oriented development workflows

---