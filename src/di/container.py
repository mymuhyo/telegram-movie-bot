"""Dependency Injection Container Setup."""

from aiogram import Dispatcher
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import setup_dishka as dishka_aiogram_setup
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.di.providers import (
    CacheProvider,
    DatabaseProvider,
    EventBusProvider,
    ServiceProvider,
)

_container: AsyncContainer | None = None


def create_container(
    session_factory: async_sessionmaker[AsyncSession],
    redis_url: str | None = None,
) -> AsyncContainer:
    """
    Create and configure the DI container.

    Args:
        session_factory: SQLAlchemy async session factory
        redis_url: Optional Redis URL for caching

    Returns:
        Configured AsyncContainer
    """
    global _container

    _container = make_async_container(
        DatabaseProvider(session_factory),
        CacheProvider(redis_url),
        EventBusProvider(),
        ServiceProvider(),
    )

    return _container


def get_container() -> AsyncContainer:
    """Get the global DI container."""
    if _container is None:
        raise RuntimeError(
            "DI container not initialized. Call create_container() first."
        )
    return _container


def setup_dishka(dp: Dispatcher, container: AsyncContainer) -> None:
    """
    Setup dishka integration with aiogram.

    Args:
        dp: Aiogram Dispatcher
        container: DI container
    """
    dishka_aiogram_setup(container, dp)
