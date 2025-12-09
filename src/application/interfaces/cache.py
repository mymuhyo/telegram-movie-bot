"""Cache interface."""

from abc import ABC, abstractmethod
from typing import Any


class CacheInterface(ABC):
    """Cache interface for caching data."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    async def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for default)
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., "movie:*")

        Returns:
            Number of keys deleted
        """
        pass

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment counter.

        Args:
            key: Cache key
            amount: Amount to increment

        Returns:
            New value
        """
        pass

    @abstractmethod
    async def get_ttl(self, key: str) -> int | None:
        """
        Get remaining TTL for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, None if no TTL or key doesn't exist
        """
        pass
