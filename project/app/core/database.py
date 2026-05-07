"""Database connectivity helpers for infrastructure layer."""

from psycopg import connect
from psycopg.rows import dict_row

from app.core.config import settings


def check_database_connectivity() -> bool:
    """Return True when a lightweight PostgreSQL probe succeeds."""
    try:
        with connect(settings.psycopg_dsn, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok;")
                result = cur.fetchone()
                return bool(result and result.get("ok") == 1)
    except Exception:
        # Startup should continue while DB container gets ready.
        return False
