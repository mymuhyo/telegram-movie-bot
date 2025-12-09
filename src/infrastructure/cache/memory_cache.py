"""In-memory cache implementation."""

import asyncio
import fnmatch
import time
from typing import Any

from src.application.interfaces import CacheInterface


class MemoryCache(CacheInterface):
    """
    In-memory cache implementation.

    Simple fallback cache when Redis is not available.
    Thread-safe using asyncio locks.
    """

    def __init__(self, default_ttl: int = 3600) -> None:
        self._cache: dict[str, tuple[Any, float | None]] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                return None

            value, expires_at = self._cache[key]

            # Check expiration
            if expires_at and time.time() > expires_at:
                del self._cache[key]
                return None

            return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Set value in cache."""
        async with self._lock:
            expires_at = None
            if ttl is not None:
                expires_at = time.time() + ttl
            elif self._default_ttl:
                expires_at = time.time() + self._default_ttl

            self._cache[key] = (value, expires_at)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self.get(key)  # Handles expiration
        return value is not None

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        async with self._lock:
            keys_to_delete = [
                k for k in self._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        async with self._lock:
            current = 0
            if key in self._cache:
                value, expires_at = self._cache[key]
                if isinstance(value, int):
                    current = value

            new_value = current + amount
            self._cache[key] = (new_value, None)
            return new_value

    async def get_ttl(self, key: str) -> int | None:
        """Get remaining TTL for key."""
        async with self._lock:
            if key not in self._cache:
                return None

            _, expires_at = self._cache[key]
            if expires_at is None:
                return None

            remaining = int(expires_at - time.time())
            return max(0, remaining)

    async def clear_all(self) -> None:
        """Clear all cache."""
        async with self._lock:
            self._cache.clear()

    def _cleanup_expired(self) -> None:
        """Remove expired entries (call periodically)."""
        now = time.time()
        expired = [
            k for k, (_, exp) in self._cache.items()
            if exp and now > exp
        ]
        for key in expired:
            del self._cache[key]
