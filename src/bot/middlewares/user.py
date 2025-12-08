"""User middleware for user context injection."""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from src.infrastructure import UnitOfWork


class UserMiddleware(BaseMiddleware):
    """Middleware for injecting user context into handlers."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        uow: UnitOfWork | None = data.get("uow")
        if not uow:
            return await handler(event, data)

        # Extract user from update
        telegram_user = None
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                telegram_user = event.message.from_user
            elif event.callback_query and event.callback_query.from_user:
                telegram_user = event.callback_query.from_user

        if telegram_user:
            # Get or create user
            user, created = await uow.users.get_or_create(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                full_name=telegram_user.full_name,
            )
            data["user"] = user
            data["user_created"] = created

            # Check if user is admin
            admin = await uow.admins.get_by_telegram_id(telegram_user.id)
            data["admin"] = admin
            data["is_admin"] = admin is not None
            data["is_super_admin"] = admin is not None and admin.is_super_admin

        return await handler(event, data)
