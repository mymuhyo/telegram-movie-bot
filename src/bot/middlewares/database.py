"""Database middleware for session injection."""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.infrastructure import UnitOfWork


class DatabaseMiddleware(BaseMiddleware):
    """Middleware for injecting database unit of work."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self._uow_factory() as uow:
            data["uow"] = uow
            result = await handler(event, data)
            await uow.commit()
            return result
