"""Pytest configuration and fixtures."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.database.base import Base
from src.infrastructure.unit_of_work import UnitOfWork


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def engine():  # type: ignore
    """Create test database engine."""
    # Use SQLite for tests
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True,
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(engine: Any) -> AsyncGenerator[AsyncSession, None]:
    """Create test session."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def uow(session: AsyncSession) -> AsyncGenerator[UnitOfWork, None]:
    """Create test unit of work."""

    class TestUoW(UnitOfWork):
        def __init__(self, session: AsyncSession) -> None:
            self._session = session
            # Import here to avoid circular imports
            from src.infrastructure.database.repositories import (
                AdminRepository,
                DownloadRepository,
                MovieRepository,
                SettingRepository,
                UserRepository,
            )

            self.movies = MovieRepository(session)
            self.users = UserRepository(session)
            self.admins = AdminRepository(session)
            self.settings = SettingRepository(session)
            self.downloads = DownloadRepository(session)

        async def __aenter__(self):  # type: ignore
            return self

        async def __aexit__(self, *args: Any) -> None:
            pass

        async def commit(self) -> None:
            await self._session.commit()

        async def rollback(self) -> None:
            await self._session.rollback()

    yield TestUoW(session)
