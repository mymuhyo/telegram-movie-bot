"""Movie repository implementation."""

import json
from collections.abc import Sequence
from uuid import UUID

from rapidfuzz import fuzz
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.core import get_logger
from src.infrastructure.database.models.movie import MovieModel
from src.infrastructure.database.repositories.base import SoftDeleteRepository

logger = get_logger(__name__)


class MovieRepository(SoftDeleteRepository[MovieModel]):
    """Repository for movie operations."""

    model = MovieModel

    def __init__(self, session: AsyncSession, redis: Redis | None = None) -> None:
        super().__init__(session)
        self._redis = redis

    async def get_by_code(self, code: int) -> MovieModel | None:
        """Get movie by code with caching."""
        # Try cache
        if self._redis:
            cache_key = f"movie:code:{code}"
            cached = await self._redis.get(cache_key)
            if cached:
                try:
                    data = json.loads(cached)
                    # Reconstruct model (id is string in JSON)
                    data["id"] = UUID(data["id"])
                    if data.get("series_id"):
                        data["series_id"] = UUID(data["series_id"])
                    return MovieModel(**data)
                except Exception as e:
                    logger.warning("movie_cache_deserialize_failed", code=code, error=str(e))

        # DB fallback
        query = (
            select(MovieModel)
            .where(MovieModel.code == code)
            .where(MovieModel.deleted_at.is_(None))
            .where(MovieModel.is_active.is_(True))
        )
        result = await self._session.execute(query)
        movie = result.scalar_one_or_none()

        # Cache result
        if movie and self._redis:
            try:
                # Serialize
                data = {
                    "id": str(movie.id),
                    "code": movie.code,
                    "title": movie.title,
                    "file_id": movie.file_id,
                    "year": movie.year,
                    "duration_minutes": movie.duration_minutes,
                    "description": movie.description,
                    "download_count": movie.download_count,
                    "part_number": movie.part_number,
                    "series_id": str(movie.series_id) if movie.series_id else None,
                    "is_active": movie.is_active,
                }
                await self._redis.setex(
                    f"movie:code:{movie.code}",
                    3600,  # 1 hour
                    json.dumps(data),
                )
            except Exception as e:
                logger.warning("movie_cache_write_failed", code=movie.code, error=str(e))

        return movie

    async def update(self, instance: MovieModel) -> MovieModel:
        """Update movie and clear cache."""
        # Clear cache before/after update
        if self._redis:
            await self._redis.delete(f"movie:code:{instance.code}")

        await self._session.merge(instance)
        # Flush to ensure DB update
        await self._session.flush()
        return instance

    async def soft_delete(self, id: UUID) -> bool:
        """Soft delete and clear cache."""
        # Need to fetch code to clear cache... optimal?
        # Or just let it expire? Better to fetch.
        movie = await self.get_by_id(id)
        if movie and self._redis:
            await self._redis.delete(f"movie:code:{movie.code}")

        return await super().soft_delete(id)

    async def code_exists(self, code: int, exclude_id: UUID | None = None) -> bool:
        """Check if code already exists."""
        query = (
            select(func.count())
            .select_from(MovieModel)
            .where(MovieModel.code == code)
            .where(MovieModel.deleted_at.is_(None))
        )
        if exclude_id:
            query = query.where(MovieModel.id != exclude_id)
        result = await self._session.execute(query)
        return (result.scalar() or 0) > 0

    async def search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.6,
    ) -> Sequence[MovieModel]:
        """Search movies by title with fuzzy matching."""
        # Get all active movies
        stmt = (
            select(MovieModel)
            .where(MovieModel.deleted_at.is_(None))
            .where(MovieModel.is_active.is_(True))
        )
        result = await self._session.execute(stmt)
        movies = result.scalars().all()

        # Apply fuzzy matching
        matches: list[tuple[MovieModel, float]] = []
        query_lower = query.lower()

        for movie in movies:
            # Calculate similarity ratio
            ratio = fuzz.partial_ratio(query_lower, movie.title.lower()) / 100

            if ratio >= threshold:
                matches.append((movie, ratio))

        # Sort by similarity and return top matches
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches[:limit]]

    async def search_by_year(self, year: int, limit: int = 10) -> Sequence[MovieModel]:
        """Search movies by year."""
        query = (
            select(MovieModel)
            .where(MovieModel.year == year)
            .where(MovieModel.deleted_at.is_(None))
            .where(MovieModel.is_active.is_(True))
            .order_by(MovieModel.download_count.desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_series(self, series_id: UUID) -> Sequence[MovieModel]:
        """Get all movies in a series."""
        query = (
            select(MovieModel)
            .where(MovieModel.series_id == series_id)
            .where(MovieModel.deleted_at.is_(None))
            .order_by(MovieModel.part_number)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_popular(self, limit: int = 5) -> Sequence[MovieModel]:
        """Get most downloaded movies."""
        query = (
            select(MovieModel)
            .where(MovieModel.deleted_at.is_(None))
            .where(MovieModel.is_active.is_(True))
            .order_by(MovieModel.download_count.desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def increment_downloads(self, movie_id: UUID) -> None:
        """Increment download count."""
        stmt = (
            update(MovieModel)
            .where(MovieModel.id == movie_id)
            .values(download_count=MovieModel.download_count + 1)
        )
        await self._session.execute(stmt)

    async def get_total_count(self) -> int:
        """Get total active movies count."""
        query = (
            select(func.count())
            .select_from(MovieModel)
            .where(MovieModel.deleted_at.is_(None))
            .where(MovieModel.is_active.is_(True))
        )
        result = await self._session.execute(query)
        return result.scalar() or 0
