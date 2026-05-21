"""
app/services/anomaly_detection.py
───────────────────────────────────
Detecta anomalías usando Z-score (distribución normal) o IQR (robusto a outliers).
"""
from __future__ import annotations

import pandas as pd
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnomalyDetector:

    def detect(
        self,
        df: pd.DataFrame,
        method: str = "zscore",
        threshold: float | None = None,
        product: str | None = None,
    ) -> dict:
        threshold = threshold or settings.zscore_threshold
        series = self._build_series(df, product)

        if series.empty:
            return {"method": method, "threshold": threshold, "total_found": 0, "anomalies": []}

        if method == "zscore":
            anomalies, scores = self._zscore(series, threshold)
        elif method == "iqr":
            anomalies, scores = self._iqr(series)
        else:
            raise ValueError(f"Unknown method '{method}'. Use 'zscore' or 'iqr'.")

        mean_val = float(series.mean())
        result = []
        for idx in anomalies.index:
            val = float(anomalies[idx])
            score = float(scores.get(idx, 0.0))
            result.append({
                "date": pd.Timestamp(idx).strftime("%Y-%m-%d"),
                "value": round(val, 2),
                "direction": "spike" if val > mean_val else "dip",
                "severity": self._severity(score, threshold),
                "zscore": round(score, 3),
            })

        logger.info("Anomalies detected: %d (method=%s)", len(result), method)
        return {
            "method": method,
            "threshold": threshold,
            "total_found": len(result),
            "anomalies": sorted(result, key=lambda x: x["date"]),
        }

    def _zscore(self, series: pd.Series, threshold: float):
        scores = (series - series.mean()) / series.std()
        abs_scores = scores.abs()
        mask = abs_scores > threshold
        return series[mask], abs_scores[mask]

    def _iqr(self, series: pd.Series):
        Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        mask = (series < lower) | (series > upper)
        scores = ((series - series.mean()) / series.std()).abs()
        return series[mask], scores[mask]

    def _severity(self, score: float, threshold: float) -> str:
        if score > threshold * 2:
            return "high"
        if score > threshold * 1.5:
            return "medium"
        return "low"

    def _build_series(self, df: pd.DataFrame, product: str | None) -> pd.Series:
        df = df.copy()
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.tz_localize(None)
        subset = df if not product else df[df["producto"].str.lower() == product.lower()]
        if subset.empty:
            return pd.Series(dtype=float)
        return subset.set_index("fecha")["ventas"].resample("D").sum()
