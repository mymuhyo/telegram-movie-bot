"""Tests for core configuration and utilities."""
import pytest
from src.core.config import Settings
from src.core.exceptions import MovieNotFoundError, UserBannedError, NotAdminError


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_from_env(self, monkeypatch):
        """Test settings loading from environment."""
        monkeypatch.setenv("BOT_TOKEN", "test:token")
        monkeypatch.setenv("PRIVATE_CHANNEL_ID", "-1001234567890")
        monkeypatch.setenv("SUPER_ADMIN_ID", "123456789")
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
        
        settings = Settings()
        
        assert settings.bot_token == "test:token"
        assert settings.private_channel_id == -1001234567890
        assert settings.super_admin_id == 123456789

    def test_default_values(self, monkeypatch):
        """Test default setting values."""
        monkeypatch.setenv("BOT_TOKEN", "test:token")
        monkeypatch.setenv("PRIVATE_CHANNEL_ID", "-1001234567890")
        monkeypatch.setenv("SUPER_ADMIN_ID", "123456789")
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
        
        settings = Settings()
        
        assert settings.debug is False
        assert settings.environment in ("development", "production")
        assert settings.backup_interval_hours == 24
        assert settings.rate_limit_requests == 5


class TestExceptions:
    """Tests for custom exceptions."""

    def test_movie_not_found_error(self):
        """Test MovieNotFoundError."""
        error = MovieNotFoundError(code=123)
        assert error.code == 123
        assert "123" in error.user_message

    def test_user_banned_error(self):
        """Test UserBannedError."""
        error = UserBannedError(reason="test reason")
        assert error.reason == "test reason"
        assert error.user_message is not None

    def test_not_admin_error(self):
        """Test NotAdminError."""
        error = NotAdminError()
        assert error.user_message is not None
