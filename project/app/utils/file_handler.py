"""File parsing helpers for CSV/XLSX uploads."""

from io import BytesIO
from pathlib import Path

import pandas as pd


SUPPORTED_UPLOAD_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def validate_supported_extension(filename: str) -> None:
    """Raise ValueError when uploaded extension is unsupported."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_UPLOAD_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_UPLOAD_EXTENSIONS))
        raise ValueError(f"Unsupported file extension '{suffix}'. Supported: {supported}")


def load_sales_dataframe(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """
    Parse CSV/XLSX payload into a dataframe.

    Column names are normalized (trimmed/lowercase) to simplify downstream logic.
    """
    validate_supported_extension(filename)
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(BytesIO(file_bytes))
    else:
        df = pd.read_excel(BytesIO(file_bytes))

    df.columns = [str(col).strip().lower() for col in df.columns]
    return df
