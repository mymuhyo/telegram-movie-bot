"""Throttling middleware for rate limiting."""

from collections import defaultdict
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from src.core.config import settings
from src.texts import messages


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for rate limiting messages."""

    def __init__(
        self,
        rate_limit: int | None = None,
        rate_window: int | None = None,
    ) -> None:
        self._rate_limit = rate_limit or settings.rate_limit_requests
        self._rate_window = rate_window or settings.rate_limit_seconds
        self._user_requests: dict[int, list[datetime]] = defaultdict(list)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        now = datetime.now(UTC)
        window_start = now - timedelta(seconds=self._rate_window)

        # Clean old requests
        self._user_requests[user_id] = [
            req_time for req_time in self._user_requests[user_id] if req_time > window_start
        ]

        # Check rate limit (skip for admins)
        is_admin = data.get("is_admin", False)
        if not is_admin and len(self._user_requests[user_id]) >= self._rate_limit:
            # Calculate remaining time
            oldest = min(self._user_requests[user_id])
            seconds_remaining = int(
                (oldest + timedelta(seconds=self._rate_window) - now).total_seconds()
            )

            await event.answer(messages.THROTTLED.format(seconds=max(1, seconds_remaining)))
            return None

        # Record this request
        self._user_requests[user_id].append(now)

        return await handler(event, data)
