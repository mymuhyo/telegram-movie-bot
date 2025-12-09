"""Redis cache implementation."""

import json
from typing import Any
from uuid import UUID

import redis.asyncio as redis

from src.application.interfaces import CacheInterface


class UUIDEncoder(json.JSONEncoder):
    """JSON encoder that handles UUIDs."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class RedisCache(CacheInterface):
    """
    Redis cache implementation.

    Uses Redis for distributed caching with JSON serialization.
    """

    def __init__(
        self,
        url: str,
        default_ttl: int = 3600,
        key_prefix: str = "moviebot:",
    ) -> None:
        self._url = url
        self._default_ttl = default_ttl
        self._key_prefix = key_prefix
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self._client = redis.from_url(self._url, decode_responses=True)
        # Test connection
        await self._client.ping()

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None

    def _key(self, key: str) -> str:
        """Get prefixed key."""
        return f"{self._key_prefix}{key}"

    def _serialize(self, value: Any) -> str:
        """Serialize value to JSON."""
        return json.dumps(value, cls=UUIDEncoder)

    def _deserialize(self, data: str | None) -> Any:
        """Deserialize value from JSON."""
        if data is None:
            return None
        return json.loads(data)

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self._client:
            return None

        data = await self._client.get(self._key(key))
        return self._deserialize(data)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Set value in cache."""
        if not self._client:
            return

        ttl = ttl or self._default_ttl
        data = self._serialize(value)
        await self._client.set(self._key(key), data, ex=ttl)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self._client:
            return False

        result = await self._client.delete(self._key(key))
        return result > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._client:
            return False

        return await self._client.exists(self._key(key)) > 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self._client:
            return 0

        full_pattern = self._key(pattern)
        cursor = 0
        deleted = 0

        while True:
            cursor, keys = await self._client.scan(
                cursor, match=full_pattern, count=100
            )
            if keys:
                deleted += await self._client.delete(*keys)
            if cursor == 0:
                break

        return deleted

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        if not self._client:
            return amount

        return await self._client.incrby(self._key(key), amount)

    async def get_ttl(self, key: str) -> int | None:
        """Get remaining TTL for key."""
        if not self._client:
            return None

        ttl = await self._client.ttl(self._key(key))
        if ttl < 0:
            return None
        return ttl

    async def set_with_lock(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """Set value only if key doesn't exist (NX)."""
        if not self._client:
            return False

        ttl = ttl or self._default_ttl
        data = self._serialize(value)
        result = await self._client.set(self._key(key), data, ex=ttl, nx=True)
        return result is not None
