"""Logging configuration helpers."""

import logging
from logging.config import dictConfig

from app.core.config import settings


def configure_logging() -> None:
    """Configure consistent structured-ish logging for local and container runs."""
    level = "DEBUG" if settings.debug else "INFO"
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": level,
                    "formatter": "standard",
                }
            },
            "root": {"level": level, "handlers": ["console"]},
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger instance."""
    return logging.getLogger(name)
