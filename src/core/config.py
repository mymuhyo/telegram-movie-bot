"""Core configuration module."""

from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "MovieBot"
    debug: bool = False
    environment: str = "production"

    # Bot
    bot_token: str
    private_channel_id: int
    super_admin_id: int
    admin_username: str = "@AdminUsername"

    # Database
    database_url: PostgresDsn

    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")

    # Backup
    backup_channel_id: int | None = None
    backup_interval_hours: int = 24

    @field_validator("backup_channel_id", mode="before")
    @classmethod
    def parse_backup_channel_id(cls, v: str | int | None) -> int | None:
        if v is None or v == "":
            return None
        return int(v)

    # Broadcasting
    broadcast_batch_size: int = 30
    broadcast_delay_ms: int = 50

    # Rate limiting
    rate_limit_requests: int = 5
    rate_limit_seconds: int = 60

    # Search
    search_min_chars: int = 2
    search_max_results: int = 10
    search_fuzzy_threshold: float = 0.6

    # Pagination
    movies_per_page: int = 10
    logs_per_page: int = 15

    @property
    def database_url_sync(self) -> str:
        """Get sync database URL for Alembic."""
        return str(self.database_url).replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
