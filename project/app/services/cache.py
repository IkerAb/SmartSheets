"""
app/services/cache.py
──────────────────────
Cache en memoria con TTL y invalidación por dataset_id.
Interfaz abstraída para migrar a Redis sin tocar servicios.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# store global: {cache_key: {"value": ..., "ts": float, "dataset_id": str}}
_store: dict[str, dict] = {}


def _make_key(namespace: str, dataset_id: str, **params) -> str:
    raw = f"{namespace}:{dataset_id}:" + ":".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hashlib.md5(raw.encode()).hexdigest()


def get(namespace: str, dataset_id: str, **params) -> Any | None:
    key = _make_key(namespace, dataset_id, **params)
    entry = _store.get(key)
    if not entry:
        return None
    if time.time() - entry["ts"] > settings.cache_ttl_seconds:
        del _store[key]
        return None
    logger.debug("Cache hit: %s", key[:12])
    return entry["value"]


def set(namespace: str, dataset_id: str, value: Any, **params) -> None:
    key = _make_key(namespace, dataset_id, **params)
    _store[key] = {"value": value, "ts": time.time(), "dataset_id": dataset_id}
    logger.debug("Cache set: %s", key[:12])


def invalidate_dataset(dataset_id: str) -> int:
    """Remove all cached entries for a given dataset_id."""
    keys = [k for k, v in _store.items() if v.get("dataset_id") == dataset_id]
    for k in keys:
        del _store[k]
    if keys:
        logger.info("Cache invalidated %d entries for dataset %s", len(keys), dataset_id[:8])
    return len(keys)


def stats() -> dict:
    return {"entries": len(_store)}
