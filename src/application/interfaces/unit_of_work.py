"""Unit of Work interface."""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator

if TYPE_CHECKING:
    from src.application.interfaces.repositories import (
        AdminRepository,
        DownloadRepository,
        FavoriteRepository,
        GenreRepository,
        MovieRepository,
        RatingRepository,
        SeriesProgressRepository,
        SeriesRepository,
        SettingRepository,
        UserRepository,
    )


class UnitOfWork(ABC):
    """
    Unit of Work pattern interface.

    Provides transactional boundary and access to all repositories.
    """

    movies: "MovieRepository"
    users: "UserRepository"
    series: "SeriesRepository"
    ratings: "RatingRepository"
    favorites: "FavoriteRepository"
    genres: "GenreRepository"
    series_progress: "SeriesProgressRepository"
    downloads: "DownloadRepository"
    admins: "AdminRepository"
    settings: "SettingRepository"

    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction."""
        pass

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        """Enter context."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        pass

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None, None]:
        """
        Explicit transaction context.

        Usage:
            async with uow.transaction():
                await uow.movies.create(movie)
                await uow.commit()
        """
        try:
            yield
            await self.commit()
        except Exception:
            await self.rollback()
            raise
