"""Unit of Work pattern implementation."""
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.infrastructure.database.repositories import (
    AdminRepository,
    DownloadRepository,
    MovieRepository,
    SeriesRepository,
    SettingRepository,
    UserRepository,
)


from redis.asyncio import Redis

class UnitOfWork:
    """Unit of Work for managing database transactions."""

    movies: MovieRepository
    users: UserRepository
    admins: AdminRepository
    settings: SettingRepository
    downloads: DownloadRepository
    series: SeriesRepository

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        redis: Redis | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._redis = redis
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.movies = MovieRepository(self._session, self._redis)
        self.users = UserRepository(self._session)
        self.admins = AdminRepository(self._session)
        self.settings = SettingRepository(self._session)
        self.downloads = DownloadRepository(self._session)
        self.series = SeriesRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        if self._session:
            await self._session.close()

    async def commit(self) -> None:
        """Commit the transaction."""
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the transaction."""
        if self._session:
            await self._session.rollback()

    async def flush(self) -> None:
        """Flush pending changes."""
        if self._session:
            await self._session.flush()
