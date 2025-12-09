"""User middleware for injecting user data into handlers."""

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from dishka import AsyncContainer

from src.application.services import UserService
from src.core.exceptions import MaintenanceModeError, SubscriptionRequiredError, UserBannedError

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    """
    User middleware for:
    - Getting or creating user in database
    - Checking if user is banned
    - Injecting user data into handler data
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Get/create user and inject into data."""
        if not isinstance(event, Update):
            return await handler(event, data)

        # Get telegram user info
        tg_user = self._get_telegram_user(event)
        if not tg_user:
            return await handler(event, data)

        # Get user service from DI container
        container: AsyncContainer | None = data.get("dishka_container")
        if not container:
            logger.warning("No DI container in middleware data")
            return await handler(event, data)

        try:
            user_service = await container.get(UserService)

            # Get or create user
            user, created = await user_service.get_or_create(
                telegram_id=tg_user.id,
                username=tg_user.username,
                full_name=tg_user.full_name,
            )

            if created:
                logger.info(f"New user registered: {tg_user.id} (@{tg_user.username})")

            # Check if user is banned
            if user.is_banned:
                raise UserBannedError(user.ban_reason)

            # Inject user data into handler data
            data["user"] = user
            data["user_id"] = user.id
            data["telegram_id"] = tg_user.id

            # Update last activity
            await user_service.update_last_activity(user.id)

        except UserBannedError:
            raise
        except Exception as e:
            logger.error(f"Error in user middleware: {e}")
            # Continue without user data
            data["user"] = None
            data["user_id"] = None

        return await handler(event, data)

    def _get_telegram_user(self, update: Update):
        """Get telegram user from update."""
        if update.message and update.message.from_user:
            return update.message.from_user
        if update.callback_query and update.callback_query.from_user:
            return update.callback_query.from_user
        return None


class SubscriptionMiddleware(BaseMiddleware):
    """
    Middleware to check if user is subscribed to required channels.
    """

    def __init__(
        self,
        required_channels: list[str] | None = None,
        skip_commands: list[str] | None = None,
    ) -> None:
        self._required_channels = required_channels or []
        self._skip_commands = skip_commands or ["/start", "/help"]
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Check subscription and process update."""
        if not isinstance(event, Update):
            return await handler(event, data)

        # Skip if no required channels
        if not self._required_channels:
            return await handler(event, data)

        # Skip certain commands
        if event.message and event.message.text:
            for cmd in self._skip_commands:
                if event.message.text.startswith(cmd):
                    return await handler(event, data)

        # Check subscription
        tg_user = self._get_telegram_user(event)
        if tg_user:
            bot = data.get("bot")
            if bot:
                for channel in self._required_channels:
                    try:
                        member = await bot.get_chat_member(channel, tg_user.id)
                        if member.status in ["left", "kicked"]:
                            raise SubscriptionRequiredError(channel)
                    except SubscriptionRequiredError:
                        raise
                    except Exception as e:
                        logger.error(f"Error checking subscription: {e}")
                        # Continue if check fails

        return await handler(event, data)

    def _get_telegram_user(self, update: Update):
        """Get telegram user from update."""
        if update.message and update.message.from_user:
            return update.message.from_user
        if update.callback_query and update.callback_query.from_user:
            return update.callback_query.from_user
        return None


class MaintenanceMiddleware(BaseMiddleware):
    """
    Middleware to check if bot is in maintenance mode.
    """

    def __init__(
        self,
        is_enabled: Callable[[], Awaitable[bool]] | None = None,
        message: str = "Bot vaqtincha ishlamayapti",
        admin_ids: list[int] | None = None,
    ) -> None:
        self._is_enabled = is_enabled
        self._message = message
        self._admin_ids = admin_ids or []
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Check maintenance mode and process update."""
        if not self._is_enabled:
            return await handler(event, data)

        if not isinstance(event, Update):
            return await handler(event, data)

        # Check if maintenance mode is enabled
        try:
            is_maintenance = await self._is_enabled()
        except Exception:
            is_maintenance = False

        if not is_maintenance:
            return await handler(event, data)

        # Allow admins to bypass
        tg_user = self._get_telegram_user(event)
        if tg_user and tg_user.id in self._admin_ids:
            return await handler(event, data)

        raise MaintenanceModeError(self._message)

    def _get_telegram_user(self, update: Update):
        """Get telegram user from update."""
        if update.message and update.message.from_user:
            return update.message.from_user
        if update.callback_query and update.callback_query.from_user:
            return update.callback_query.from_user
        return None
