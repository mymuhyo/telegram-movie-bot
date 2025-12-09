"""Repository interfaces (Ports)."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from src.domain.entities import (
    Favorite,
    Genre,
    Movie,
    Rating,
    Series,
    User,
    UserSeriesProgress,
)

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository interface."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity."""
        pass


class MovieRepository(BaseRepository[Movie]):
    """Movie repository interface."""

    @abstractmethod
    async def get_by_code(self, code: int) -> Movie | None:
        """Get movie by code."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        year: int | None = None,
        quality: str | None = None,
        genre_id: UUID | None = None,
        limit: int = 10,
    ) -> list[Movie]:
        """Search movies with filters."""
        pass

    @abstractmethod
    async def get_by_series(self, series_id: UUID) -> list[Movie]:
        """Get all movies in a series."""
        pass

    @abstractmethod
    async def get_popular(self, limit: int = 10) -> list[Movie]:
        """Get popular movies."""
        pass

    @abstractmethod
    async def get_recent(self, limit: int = 10) -> list[Movie]:
        """Get recently added movies."""
        pass

    @abstractmethod
    async def get_top_rated(self, limit: int = 10) -> list[Movie]:
        """Get top rated movies."""
        pass

    @abstractmethod
    async def increment_downloads(self, movie_id: UUID) -> None:
        """Increment download count."""
        pass

    @abstractmethod
    async def update_rating(
        self, movie_id: UUID, average: float, count: int
    ) -> None:
        """Update movie rating stats."""
        pass

    @abstractmethod
    async def get_next_code(self) -> int:
        """Get next available movie code."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Get total movie count."""
        pass


class UserRepository(BaseRepository[User]):
    """User repository interface."""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        pass

    @abstractmethod
    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
        full_name: str | None = None,
    ) -> tuple[User, bool]:
        """Get or create user. Returns (user, created)."""
        pass

    @abstractmethod
    async def get_all_ids(self) -> list[int]:
        """Get all user Telegram IDs."""
        pass

    @abstractmethod
    async def get_active_ids(self, days: int = 30) -> list[int]:
        """Get active user IDs."""
        pass

    @abstractmethod
    async def ban(self, user_id: UUID, reason: str | None = None) -> bool:
        """Ban user."""
        pass

    @abstractmethod
    async def unban(self, user_id: UUID) -> bool:
        """Unban user."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Get total user count."""
        pass

    @abstractmethod
    async def count_active(self, days: int = 30) -> int:
        """Get active user count."""
        pass


class SeriesRepository(BaseRepository[Series]):
    """Series repository interface."""

    @abstractmethod
    async def get_by_name(self, name: str) -> Series | None:
        """Get series by name."""
        pass

    @abstractmethod
    async def get_all(self) -> list[Series]:
        """Get all series."""
        pass


class RatingRepository(BaseRepository[Rating]):
    """Rating repository interface."""

    @abstractmethod
    async def get_by_user_and_movie(
        self, user_id: UUID, movie_id: UUID
    ) -> Rating | None:
        """Get user's rating for a movie."""
        pass

    @abstractmethod
    async def get_by_movie(self, movie_id: UUID) -> list[Rating]:
        """Get all ratings for a movie."""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: UUID, limit: int = 50) -> list[Rating]:
        """Get user's ratings."""
        pass

    @abstractmethod
    async def upsert(
        self, user_id: UUID, movie_id: UUID, score: int
    ) -> tuple[Rating, int | None]:
        """Create or update rating. Returns (rating, old_score or None)."""
        pass


class FavoriteRepository(BaseRepository[Favorite]):
    """Favorite repository interface."""

    @abstractmethod
    async def get_by_user_and_movie(
        self, user_id: UUID, movie_id: UUID
    ) -> Favorite | None:
        """Get specific favorite."""
        pass

    @abstractmethod
    async def get_by_user(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Favorite]:
        """Get user's favorites."""
        pass

    @abstractmethod
    async def count_by_user(self, user_id: UUID) -> int:
        """Count user's favorites."""
        pass

    @abstractmethod
    async def exists(self, user_id: UUID, movie_id: UUID) -> bool:
        """Check if favorite exists."""
        pass

    @abstractmethod
    async def remove(self, user_id: UUID, movie_id: UUID) -> bool:
        """Remove favorite."""
        pass


class GenreRepository(BaseRepository[Genre]):
    """Genre repository interface."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Genre | None:
        """Get genre by slug."""
        pass

    @abstractmethod
    async def get_all(self) -> list[Genre]:
        """Get all genres."""
        pass

    @abstractmethod
    async def get_by_movie(self, movie_id: UUID) -> list[Genre]:
        """Get genres for a movie."""
        pass

    @abstractmethod
    async def add_to_movie(self, movie_id: UUID, genre_id: UUID) -> None:
        """Add genre to movie."""
        pass

    @abstractmethod
    async def remove_from_movie(self, movie_id: UUID, genre_id: UUID) -> None:
        """Remove genre from movie."""
        pass


class SeriesProgressRepository(BaseRepository[UserSeriesProgress]):
    """Series progress repository interface."""

    @abstractmethod
    async def get_by_user_and_series(
        self, user_id: UUID, series_id: UUID
    ) -> UserSeriesProgress | None:
        """Get progress for specific user and series."""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[UserSeriesProgress]:
        """Get all progress records for user."""
        pass

    @abstractmethod
    async def upsert(
        self,
        user_id: UUID,
        series_id: UUID,
        part_number: int,
    ) -> UserSeriesProgress:
        """Update or create progress record."""
        pass


class DownloadRepository(ABC):
    """Download tracking repository interface."""

    @abstractmethod
    async def create(
        self,
        user_id: UUID,
        movie_id: UUID,
        movie_code: int,
        source: str = "code",
    ) -> None:
        """Record a download."""
        pass

    @abstractmethod
    async def get_user_history(
        self, user_id: UUID, limit: int = 50
    ) -> list[tuple[UUID, int]]:
        """Get user's download history. Returns list of (movie_id, code)."""
        pass

    @abstractmethod
    async def get_user_movie_ids(self, user_id: UUID) -> set[UUID]:
        """Get set of movie IDs user has downloaded."""
        pass

    @abstractmethod
    async def count_by_movie(self, movie_id: UUID) -> int:
        """Count downloads for a movie."""
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Get total download count."""
        pass


class AdminRepository(ABC):
    """Admin repository interface."""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get admin by Telegram ID."""
        pass

    @abstractmethod
    async def is_admin(self, telegram_id: int) -> bool:
        """Check if user is admin."""
        pass

    @abstractmethod
    async def is_super_admin(self, telegram_id: int) -> bool:
        """Check if user is super admin."""
        pass

    @abstractmethod
    async def get_all(self) -> list[dict]:
        """Get all admins."""
        pass


class SettingRepository(ABC):
    """Settings repository interface."""

    @abstractmethod
    async def get(self, key: str, default: str | None = None) -> str | None:
        """Get setting value."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str) -> None:
        """Set setting value."""
        pass

    @abstractmethod
    async def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean setting."""
        pass

    @abstractmethod
    async def get_int(self, key: str, default: int = 0) -> int:
        """Get integer setting."""
        pass
