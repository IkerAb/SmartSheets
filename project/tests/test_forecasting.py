"""Tests for ForecastingService."""
import pytest
import pandas as pd
import numpy as np
from app.services.forecasting import ForecastingService


def test_forecast_returns_correct_horizon(sample_df):
    svc = ForecastingService()
    result = svc.forecast(sample_df, horizon=14)
    assert len(result["labels"]) == 14
    assert len(result["values"]) == 14
    assert len(result["lower"]) == 14
    assert len(result["upper"]) == 14


def test_confidence_interval_ordering(sample_df):
    svc = ForecastingService()
    result = svc.forecast(sample_df, horizon=10)
    for lo, mid, hi in zip(result["lower"], result["values"], result["upper"]):
        assert lo <= hi, f"lower={lo} > upper={hi}"


def test_forecast_by_product(sample_df):
    svc = ForecastingService()
    result = svc.forecast(sample_df, horizon=7, product="ProductoA")
    assert len(result["labels"]) == 7


def test_forecast_unknown_product_raises(sample_df):
    svc = ForecastingService()
    with pytest.raises(ValueError, match="No data found"):
        svc.forecast(sample_df, product="NoExiste")


def test_naive_fallback_for_short_series():
    svc = ForecastingService()
    dates = pd.date_range("2023-01-01", periods=10, freq="D")
    df = pd.DataFrame({"fecha": dates, "producto": "P",
                       "ventas": np.random.default_rng(0).normal(3000, 200, 10)})
    result = svc.forecast(df, horizon=5)
    assert result["model"] == "naive"
    assert len(result["warnings"]) > 0


def test_monthly_aggregation(sample_df):
    svc = ForecastingService()
    result = svc.forecast(sample_df, horizon=3, aggregation="month")
    assert len(result["labels"]) == 3
