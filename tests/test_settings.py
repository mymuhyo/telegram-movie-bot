"""Tests for settings repository and caching."""

import pytest


class TestSettingRepository:
    """Tests for SettingRepository."""

    @pytest.mark.asyncio
    async def test_set_and_get(self, uow):
        """Test setting and getting a value."""
        await uow.settings.set("test_key", "test_value")
        await uow.commit()

        value = await uow.settings.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_get_default(self, uow):
        """Test getting non-existent key with default."""
        value = await uow.settings.get("nonexistent", default="default_val")
        assert value == "default_val"

    @pytest.mark.asyncio
    async def test_maintenance_mode(self, uow):
        """Test maintenance mode toggle."""
        # Default is False
        is_maint = await uow.settings.is_maintenance_mode()
        assert is_maint is False

        # Enable
        await uow.settings.set("maintenance_mode", True)
        await uow.commit()

        is_maint = await uow.settings.is_maintenance_mode()
        assert is_maint is True

    @pytest.mark.asyncio
    async def test_channel_check(self, uow):
        """Test channel check toggle."""
        is_enabled = await uow.settings.is_channel_check_enabled()
        assert is_enabled is False

        await uow.settings.set("channel_check_enabled", True)
        await uow.commit()

        is_enabled = await uow.settings.is_channel_check_enabled()
        assert is_enabled is True

    @pytest.mark.asyncio
    async def test_required_channel(self, uow):
        """Test setting required channel."""
        # Set channel
        await uow.settings.set("required_channel", "@TestChannel")
        await uow.commit()

        channel = await uow.settings.get_required_channel()
        assert channel == "@TestChannel"


class TestDownloadRepository:
    """Tests for DownloadRepository."""

    @pytest.mark.asyncio
    async def test_get_top_movies(self, uow):
        """Test getting top downloaded movies."""
        top = await uow.downloads.get_top_movies(limit=5)
        assert isinstance(top, list)
