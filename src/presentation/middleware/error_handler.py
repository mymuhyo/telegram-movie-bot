"""Global error handler middleware."""

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from src.core.exceptions import (
    AccessDeniedError,
    BotException,
    EntityNotFoundError,
    MaintenanceModeError,
    RateLimitError,
    SubscriptionRequiredError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Global error handler middleware.

    Catches exceptions and sends user-friendly messages.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Process update with error handling."""
        try:
            return await handler(event, data)
        except BotException as e:
            await self._handle_bot_exception(event, e)
        except Exception as e:
            await self._handle_unknown_exception(event, e)
            raise  # Re-raise for logging

    async def _handle_bot_exception(
        self,
        event: TelegramObject,
        exc: BotException,
    ) -> None:
        """Handle known bot exceptions."""
        logger.warning(f"Bot exception: {exc.message}")

        # Get the message/callback to reply to
        reply_target = self._get_reply_target(event)
        if not reply_target:
            return

        # Send user-friendly message
        try:
            if isinstance(exc, MaintenanceModeError):
                await reply_target.answer(exc.user_message)
            elif isinstance(exc, RateLimitError):
                await reply_target.answer(exc.user_message)
            elif isinstance(exc, SubscriptionRequiredError):
                await reply_target.answer(exc.user_message)
            elif isinstance(exc, AccessDeniedError):
                await reply_target.answer(exc.user_message)
            elif isinstance(exc, EntityNotFoundError):
                await reply_target.answer(exc.user_message)
            elif isinstance(exc, ValidationError):
                await reply_target.answer(exc.user_message)
            else:
                await reply_target.answer(exc.user_message)
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")

    async def _handle_unknown_exception(
        self,
        event: TelegramObject,
        exc: Exception,
    ) -> None:
        """Handle unknown exceptions."""
        logger.error(f"Unexpected error: {exc}", exc_info=True)

        reply_target = self._get_reply_target(event)
        if not reply_target:
            return

        try:
            await reply_target.answer(
                "❌ Xatolik yuz berdi.\n\nIltimos, keyinroq qayta urinib ko'ring."
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")

    def _get_reply_target(self, event: TelegramObject):
        """Get the message or callback to reply to."""
        if isinstance(event, Update):
            if event.message:
                return event.message
            if event.callback_query:
                return event.callback_query.message
        return None


class LoggingMiddleware(BaseMiddleware):
    """
    Logging middleware for all updates.

    Logs incoming updates for debugging and analytics.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Log and process update."""
        if isinstance(event, Update):
            user_id = self._get_user_id(event)
            update_type = self._get_update_type(event)

            logger.info(
                f"Update received: type={update_type}, user_id={user_id}"
            )

        return await handler(event, data)

    def _get_user_id(self, update: Update) -> int | None:
        """Get user ID from update."""
        if update.message and update.message.from_user:
            return update.message.from_user.id
        if update.callback_query and update.callback_query.from_user:
            return update.callback_query.from_user.id
        return None

    def _get_update_type(self, update: Update) -> str:
        """Get update type string."""
        if update.message:
            if update.message.text:
                return f"message:{update.message.text[:20]}"
            return "message:other"
        if update.callback_query:
            return f"callback:{update.callback_query.data}"
        return "unknown"


class ThrottlingMiddleware(BaseMiddleware):
    """
    Throttling middleware to prevent spam.

    Limits the rate of updates per user.
    """

    def __init__(
        self,
        rate_limit: float = 0.5,  # seconds between updates
        max_violations: int = 5,  # violations before temporary ban
    ) -> None:
        self._rate_limit = rate_limit
        self._max_violations = max_violations
        self._last_update: dict[int, float] = {}
        self._violations: dict[int, int] = {}
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Check throttling and process update."""
        import time

        if not isinstance(event, Update):
            return await handler(event, data)

        user_id = self._get_user_id(event)
        if not user_id:
            return await handler(event, data)

        current_time = time.time()
        last_time = self._last_update.get(user_id, 0)

        if current_time - last_time < self._rate_limit:
            self._violations[user_id] = self._violations.get(user_id, 0) + 1

            if self._violations[user_id] >= self._max_violations:
                logger.warning(f"User {user_id} throttled (violations: {self._violations[user_id]})")
                raise RateLimitError(seconds_remaining=int(self._rate_limit * 2))

            # Skip this update
            return None

        # Reset violations on successful request
        self._violations[user_id] = 0
        self._last_update[user_id] = current_time

        return await handler(event, data)

    def _get_user_id(self, update: Update) -> int | None:
        """Get user ID from update."""
        if update.message and update.message.from_user:
            return update.message.from_user.id
        if update.callback_query and update.callback_query.from_user:
            return update.callback_query.from_user.id
        return None
