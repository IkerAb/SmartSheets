"""Tests for DataLoaderService using mock repository."""
import pytest
from app.services.data_loader import DataLoaderService, FileUploadPayload


def test_ingest_valid_csv(mock_repo, sample_csv_bytes):
    svc = DataLoaderService(repository=mock_repo)
    result = svc.ingest_and_persist(
        FileUploadPayload(filename="ventas.csv", content=sample_csv_bytes)
    )
    assert result.dataset_id == "test-uuid"
    assert result.row_count > 0


def test_ingest_invalid_extension_raises(mock_repo):
    svc = DataLoaderService(repository=mock_repo)
    with pytest.raises(ValueError, match="Unsupported"):
        svc.ingest_and_persist(FileUploadPayload(filename="file.txt", content=b"a,b\n1,2"))


def test_ingest_missing_columns_raises(mock_repo):
    svc = DataLoaderService(repository=mock_repo)
    bad_csv = b"nombre,precio\nProd,100\n"
    with pytest.raises(ValueError, match="Missing required columns"):
        svc.ingest_and_persist(FileUploadPayload(filename="bad.csv", content=bad_csv))
