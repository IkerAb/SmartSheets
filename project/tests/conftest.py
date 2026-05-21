"""Global pytest fixtures. Uses mock repo — no DB required for unit tests."""
import io, csv
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock

import pandas as pd
import numpy as np

from app.models.dataset_models import DatasetStatus, DatasetPersistResult, DatasetMetadata


def _make_df(n_days=90):
    rows = []
    rng = np.random.default_rng(42)
    for i in range(n_days):
        d = date(2023, 1, 1) + timedelta(days=i)
        for p in ["ProductoA", "ProductoB"]:
            rows.append({"fecha": pd.Timestamp(d), "producto": p,
                         "ventas": float(abs(rng.normal(5000, 400)))})
    return pd.DataFrame(rows)


@pytest.fixture(scope="session")
def sample_df():
    return _make_df()


@pytest.fixture(scope="session")
def mock_repo():
    df = _make_df()
    repo = MagicMock()
    repo.get_metadata.return_value = DatasetMetadata(
        dataset_id="test-uuid",
        source_filename="test.csv",
        status=DatasetStatus.CLEANED,
        uploaded_at=pd.Timestamp("2024-01-01"),
        processed_at=pd.Timestamp("2024-01-01"),
        error_reason=None,
        row_count=len(df),
    )
    repo.get_dataframe.return_value = df
    repo.persist_dataset.return_value = DatasetPersistResult(
        dataset_id="test-uuid", row_count=len(df), status=DatasetStatus.CLEANED,
    )
    return repo


@pytest.fixture
def sample_csv_bytes() -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["fecha", "producto", "ventas"])
    for i in range(60):
        d = date(2023, 1, 1) + timedelta(days=i)
        w.writerow([d.isoformat(), "ProductoX", round(3000 + i * 10, 2)])
        w.writerow([d.isoformat(), "ProductoY", round(2000 + i * 8, 2)])
    return buf.getvalue().encode("utf-8")
