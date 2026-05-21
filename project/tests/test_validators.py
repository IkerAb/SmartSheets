"""Tests for validation and file parsing utilities."""
import pytest
import pandas as pd
from app.utils.validators import validate_and_normalize_sales_dataframe
from app.utils.file_handler import load_sales_dataframe, validate_supported_extension


def test_valid_dataframe_passes():
    df = pd.DataFrame({"fecha": ["2023-01-01"], "producto": ["P"], "ventas": [100.0]})
    result = validate_and_normalize_sales_dataframe(df)
    assert "fecha" in result.columns
    assert result["ventas"].dtype == float


def test_missing_column_raises():
    df = pd.DataFrame({"fecha": ["2023-01-01"], "producto": ["P"]})
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_and_normalize_sales_dataframe(df)


def test_invalid_date_raises():
    df = pd.DataFrame({"fecha": ["not-a-date"], "producto": ["P"], "ventas": [100.0]})
    with pytest.raises(ValueError, match="fecha"):
        validate_and_normalize_sales_dataframe(df)


def test_invalid_ventas_raises():
    df = pd.DataFrame({"fecha": ["2023-01-01"], "producto": ["P"], "ventas": ["abc"]})
    with pytest.raises(ValueError, match="ventas"):
        validate_and_normalize_sales_dataframe(df)


def test_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported"):
        validate_supported_extension("datos.txt")


def test_csv_parsing(sample_csv_bytes):
    df = load_sales_dataframe(sample_csv_bytes, "test.csv")
    assert len(df) > 0
    assert "fecha" in df.columns
