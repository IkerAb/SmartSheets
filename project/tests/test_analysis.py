"""Tests for AnalysisService and AnomalyDetector."""
import pandas as pd
import numpy as np
import pytest
from app.services.analysis import AnalysisService
from app.services.anomaly_detection import AnomalyDetector


def test_compute_insights_returns_all_keys(sample_df):
    svc = AnalysisService()
    result = svc.compute_insights(sample_df)
    for key in ["total_sales", "avg_ticket", "total_transactions",
                "top_products", "monthly_growth", "chart_ready", "natural_summary"]:
        assert key in result


def test_total_sales_positive(sample_df):
    svc = AnalysisService()
    result = svc.compute_insights(sample_df)
    assert result["total_sales"] > 0


def test_top_products_sorted(sample_df):
    svc = AnalysisService()
    top = svc.compute_insights(sample_df)["top_products"]
    totals = [p["total"] for p in top]
    assert totals == sorted(totals, reverse=True)


def test_chart_labels_values_aligned(sample_df):
    svc = AnalysisService()
    chart = svc.compute_insights(sample_df)["chart_ready"]
    assert len(chart["labels"]) == len(chart["values"])


def test_natural_summary_not_empty(sample_df):
    svc = AnalysisService()
    summary = svc.compute_insights(sample_df)["natural_summary"]
    assert isinstance(summary, str) and len(summary) > 20


def test_anomaly_detects_spike():
    detector = AnomalyDetector()
    dates = pd.date_range("2023-01-01", periods=60, freq="D")
    vals = np.random.default_rng(1).normal(5000, 200, 60)
    vals[30] = 25000
    df = pd.DataFrame({"fecha": dates, "producto": "P", "ventas": vals})
    result = detector.detect(df, method="zscore", threshold=2.0)
    assert result["total_found"] >= 1
    assert any(a["direction"] == "spike" for a in result["anomalies"])


def test_anomaly_flat_series_no_results():
    detector = AnomalyDetector()
    dates = pd.date_range("2023-01-01", periods=30, freq="D")
    df = pd.DataFrame({"fecha": dates, "producto": "P", "ventas": [5000.0] * 30})
    result = detector.detect(df, method="zscore")
    assert result["total_found"] == 0


def test_anomaly_iqr_method(sample_df):
    detector = AnomalyDetector()
    result = detector.detect(sample_df, method="iqr")
    assert "anomalies" in result
    assert result["method"] == "iqr"
