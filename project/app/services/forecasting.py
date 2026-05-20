"""
app/services/forecasting.py
────────────────────────────
Motor de forecasting con modelo ETS (statsmodels) como primario
y fallback a media móvil para series muy cortas.
Patrón adaptador: pluggable para agregar Prophet en el futuro.
"""
from __future__ import annotations

import pandas as pd
import numpy as np

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ForecastingService:

    def forecast(
        self,
        df: pd.DataFrame,
        horizon: int = settings.default_horizon,
        product: str | None = None,
        confidence: float = settings.default_confidence,
        aggregation: str = "day",
    ) -> dict:
        """
        Genera forecast para el horizonte dado.
        aggregation: "day" | "month"
        """
        series = self._build_series(df, product, aggregation)

        if series.empty:
            raise ValueError(
                f"No data found for product '{product}'. "
                f"Available: {df['producto'].unique().tolist()}"
            )

        warnings: list[str] = []
        model_name: str
        labels: list[str]
        values: list[float]
        lower: list[float]
        upper: list[float]
        mae: float | None = None

        if len(series) >= settings.min_rows_forecast:
            try:
                result = self._ets_forecast(series, horizon, confidence, aggregation)
                model_name = result["model"]
                labels, values, lower, upper = (
                    result["labels"], result["values"],
                    result["lower"], result["upper"],
                )
                mae = result.get("mae")
            except Exception as exc:
                logger.warning("ETS failed (%s), using naive fallback", exc)
                warnings.append(f"ETS model failed; using naive fallback. Reason: {exc}")
                result = self._naive_forecast(series, horizon, confidence, aggregation)
                model_name = result["model"]
                labels, values, lower, upper = (
                    result["labels"], result["values"],
                    result["lower"], result["upper"],
                )
        else:
            warnings.append(
                f"Series has only {len(series)} observations (min={settings.min_rows_forecast}). "
                "Using naive forecast; results may be unreliable."
            )
            result = self._naive_forecast(series, horizon, confidence, aggregation)
            model_name = result["model"]
            labels, values, lower, upper = (
                result["labels"], result["values"],
                result["lower"], result["upper"],
            )

        return {
            "model": model_name,
            "labels": labels,
            "values": values,
            "lower": lower,
            "upper": upper,
            "mae": mae,
            "warnings": warnings,
        }

    # ── ETS (statsmodels) ────────────────────────────────────────────────────

    def _ets_forecast(self, series: pd.Series, horizon: int, confidence: float, aggregation: str) -> dict:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        freq = "D" if aggregation == "day" else "ME"
        model = ExponentialSmoothing(
            series,
            trend="add",
            seasonal="add" if len(series) >= 24 else None,
            seasonal_periods=7 if aggregation == "day" else 12,
            initialization_method="estimated",
        )
        fit = model.fit(optimized=True)

        forecast_vals = fit.forecast(horizon)
        # intervalo de confianza via simulación bootstrap
        alpha = 1 - confidence
        residuals = fit.resid
        std_resid = float(residuals.std())
        z = float(np.abs(np.percentile(np.random.standard_normal(10000), (alpha / 2) * 100)))

        # fechas futuras
        last_date = series.index[-1]
        if aggregation == "day":
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D")
        else:
            future_dates = pd.date_range(start=last_date + pd.offsets.MonthEnd(1), periods=horizon, freq="ME")

        fv = forecast_vals.values
        lo = (fv - z * std_resid).tolist()
        hi = (fv + z * std_resid).tolist()

        fmt = "%Y-%m-%d" if aggregation == "day" else "%Y-%m"
        mae = float(np.abs(fit.fittedvalues - series).mean())

        return {
            "model": "ets",
            "labels": [d.strftime(fmt) for d in future_dates],
            "values": [round(float(v), 2) for v in fv],
            "lower": [round(v, 2) for v in lo],
            "upper": [round(v, 2) for v in hi],
            "mae": round(mae, 2),
        }

    # ── Naive fallback ───────────────────────────────────────────────────────

    def _naive_forecast(self, series: pd.Series, horizon: int, confidence: float, aggregation: str) -> dict:
        mean_val = float(series.mean())
        std_val = float(series.std()) if len(series) > 1 else mean_val * 0.1
        alpha = 1 - confidence
        z = float(np.abs(np.percentile(np.random.standard_normal(10000), (alpha / 2) * 100)))

        last_date = series.index[-1]
        if aggregation == "day":
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D")
            fmt = "%Y-%m-%d"
        else:
            future_dates = pd.date_range(start=last_date + pd.offsets.MonthEnd(1), periods=horizon, freq="ME")
            fmt = "%Y-%m"

        return {
            "model": "naive",
            "labels": [d.strftime(fmt) for d in future_dates],
            "values": [round(mean_val, 2)] * horizon,
            "lower": [round(mean_val - z * std_val, 2)] * horizon,
            "upper": [round(mean_val + z * std_val, 2)] * horizon,
            "mae": None,
        }

    # ── helpers ──────────────────────────────────────────────────────────────

    def _build_series(self, df: pd.DataFrame, product: str | None, aggregation: str) -> pd.Series:
        df = df.copy()
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.tz_localize(None)
        subset = df if not product else df[df["producto"].str.lower() == product.lower()]
        if subset.empty:
            return pd.Series(dtype=float)
        freq = "D" if aggregation == "day" else "ME"
        series = subset.set_index("fecha")["ventas"].resample(freq).sum()
        # completar huecos
        series = series.asfreq(freq, fill_value=0)
        return series
