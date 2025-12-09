"""Setting repository implementation."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models.setting import SettingModel


class SettingRepository:
    """Repository for settings operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cache: dict[str, Any] = {}

    async def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key."""
        if key in self._cache:
            return self._cache[key]

        query = select(SettingModel).where(SettingModel.key == key)
        result = await self._session.execute(query)
        setting = result.scalar_one_or_none()

        if setting is None:
            return default

        value = setting.get_typed_value()
        self._cache[key] = value
        return value

    async def set(
        self,
        key: str,
        value: Any,
        value_type: str = "string",
        description: str | None = None,
    ) -> None:
        """Set or update a setting."""
        # Convert value to string
        if isinstance(value, bool):
            str_value = "true" if value else "false"
            value_type = "boolean"
        elif isinstance(value, int):
            str_value = str(value)
            value_type = "integer"
        elif isinstance(value, dict):
            import json

            str_value = json.dumps(value)
            value_type = "json"
        else:
            str_value = str(value)

        # Upsert
        stmt = insert(SettingModel).values(
            key=key,
            value=str_value,
            value_type=value_type,
            description=description,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[SettingModel.key],
            set_={
                "value": str_value,
                "value_type": value_type,
            },
        )
        await self._session.execute(stmt)

        # Update cache
        self._cache[key] = value

    async def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean setting."""
        value = await self.get(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")

    async def get_int(self, key: str, default: int = 0) -> int:
        """Get integer setting."""
        value = await self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    async def get_str(self, key: str, default: str = "") -> str:
        """Get string setting."""
        value = await self.get(key)
        if value is None:
            return default
        return str(value)

    def clear_cache(self) -> None:
        """Clear the settings cache."""
        self._cache.clear()

    # Convenience methods for common settings
    async def is_maintenance_mode(self) -> bool:
        """Check if maintenance mode is enabled."""
        return await self.get_bool("maintenance_mode", False)

    async def get_maintenance_message(self) -> str:
        """Get maintenance message."""
        return await self.get_str(
            "maintenance_message",
            "Texnik ishlar olib borilmoqda. Iltimos, keyinroq urinib ko'ring.",
        )

    async def is_channel_check_enabled(self) -> bool:
        """Check if channel subscription check is enabled."""
        return await self.get_bool("channel_check_enabled", False)

    async def get_required_channel(self) -> str:
        """Get required channel username."""
        return await self.get_str("required_channel", "")
