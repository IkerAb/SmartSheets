# ADR-0001: ETS as primary forecasting model

**Status**: Accepted

## Context
Need to forecast daily/monthly sales with seasonality, missing data, and variable dataset sizes.

## Decision
Use `statsmodels` ExponentialSmoothing (ETS) as primary model.
Fall back to naive mean forecast for series with <30 observations.
Keep an adapter pattern so Prophet can be plugged in later.

## Consequences
- ETS handles trend + seasonality without heavy dependencies.
- Naive fallback prevents errors on sparse product series.
- Adapter pattern: swapping model = changing one method in `forecasting.py`.
