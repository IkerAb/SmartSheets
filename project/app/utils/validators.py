"""Validation and normalization helpers for uploaded sales datasets."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ("fecha", "producto", "ventas")


def validate_and_normalize_sales_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate required schema and return normalized canonical dataframe.

    Canonical output columns:
    - `fecha`: pandas datetime64[ns, UTC]
    - `producto`: stripped non-empty string
    - `ventas`: float
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    normalized = df.loc[:, REQUIRED_COLUMNS].copy()

    normalized["fecha"] = pd.to_datetime(normalized["fecha"], errors="coerce", utc=True)
    if normalized["fecha"].isna().any():
        raise ValueError("Column 'fecha' contains invalid or malformed dates.")

    normalized["producto"] = normalized["producto"].astype(str).str.strip()
    if (normalized["producto"] == "").any():
        raise ValueError("Column 'producto' contains empty values.")

    normalized["ventas"] = pd.to_numeric(normalized["ventas"], errors="coerce")
    if normalized["ventas"].isna().any():
        raise ValueError("Column 'ventas' must contain numeric values.")

    normalized["ventas"] = normalized["ventas"].astype(float)
    return normalized
