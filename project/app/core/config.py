"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime configuration for the API service."""

    app_name: str = Field(default="Sales Analytics & Forecasting API")
    app_version: str = Field(default="0.1.0")
    api_prefix: str = Field(default="/api/v1")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # PostgreSQL
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="sales_analytics")
    postgres_user: str = Field(default="sales_user")
    postgres_password: str = Field(default="sales_pass")
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")

    # Cache
    cache_ttl_seconds: int = Field(default=3600)

    # Upload
    max_upload_mb: int = Field(default=50)

    # Forecasting
    min_rows_forecast: int = Field(default=30)
    default_horizon: int = Field(default=30)
    default_confidence: float = Field(default=0.90)

    # Anomaly detection
    zscore_threshold: float = Field(default=2.5)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def psycopg_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
