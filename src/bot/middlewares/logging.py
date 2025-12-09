"""Logging middleware for request tracking."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from src.core import get_logger, log_context

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging all incoming updates."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Update):
            # Extract user info
            user = None
            if event.message:
                user = event.message.from_user
            elif event.callback_query:
                user = event.callback_query.from_user

            if user:
                log_context(
                    user_id=user.id,
                    username=user.username,
                )
                logger.debug(
                    "incoming_update",
                    update_id=event.update_id,
                    update_type=event.event_type,
                )

        return await handler(event, data)
