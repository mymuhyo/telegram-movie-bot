"""Movie application service."""

from decimal import Decimal
from uuid import UUID

from src.application.dto import MovieCardDTO, MovieDTO, SearchFilters, SearchResult
from src.application.interfaces import (
    CacheInterface,
    EventBus,
    UnitOfWork,
)
from src.core.exceptions import MovieNotFoundError
from src.domain.entities import Movie
from src.domain.events import MovieDownloaded


class MovieService:
    """Application service for movie operations."""

    CACHE_TTL = 3600  # 1 hour
    CACHE_PREFIX = "movie"

    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheInterface,
        event_bus: EventBus,
    ) -> None:
        self._uow = uow
        self._cache = cache
        self._event_bus = event_bus

    async def get_by_code(self, code: int) -> MovieDTO | None:
        """Get movie by code."""
        # Try cache first
        cache_key = f"{self.CACHE_PREFIX}:code:{code}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        async with self._uow:
            movie = await self._uow.movies.get_by_code(code)
            if not movie:
                return None

            dto = self._to_dto(movie)

            # Cache result
            await self._cache.set(cache_key, dto, self.CACHE_TTL)
            return dto

    async def get_movie_card(
        self,
        code: int,
        user_id: UUID,
        track_download: bool = True,
    ) -> MovieCardDTO:
        """
        Get complete movie card with user-specific data.

        Args:
            code: Movie code
            user_id: User ID
            track_download: Whether to track as download

        Returns:
            Complete movie card data

        Raises:
            MovieNotFoundError: If movie not found
        """
        async with self._uow:
            movie = await self._uow.movies.get_by_code(code)
            if not movie:
                raise MovieNotFoundError(code)

            movie_dto = self._to_dto(movie)

            # Get user-specific data
            user_rating = None
            rating = await self._uow.ratings.get_by_user_and_movie(user_id, movie.id)
            if rating:
                user_rating = rating.score

            is_favorite = await self._uow.favorites.exists(user_id, movie.id)

            watched_ids = await self._uow.downloads.get_user_movie_ids(user_id)
            is_watched = movie.id in watched_ids

            # Series navigation
            has_next = False
            has_prev = False
            next_code = None
            prev_code = None

            if movie.series_id and movie.part_number:
                series_movies = await self._uow.movies.get_by_series(movie.series_id)
                for m in series_movies:
                    if m.part_number == movie.part_number + 1:
                        has_next = True
                        next_code = m.code
                    elif m.part_number == movie.part_number - 1:
                        has_prev = True
                        prev_code = m.code

                # Get series info
                series = await self._uow.series.get_by_id(movie.series_id)
                if series:
                    movie_dto.series_name = series.name
                    movie_dto.total_parts = series.total_parts

            # Track download
            if track_download:
                await self._uow.downloads.create(
                    user_id=user_id,
                    movie_id=movie.id,
                    movie_code=movie.code,
                    source="code",
                )
                await self._uow.movies.increment_downloads(movie.id)
                await self._uow.commit()

                # Publish event
                await self._event_bus.publish(
                    MovieDownloaded(
                        movie_id=movie.id,
                        movie_code=movie.code,
                        user_id=user_id,
                        source="code",
                    )
                )

            return MovieCardDTO(
                movie=movie_dto,
                user_rating=user_rating,
                is_favorite=is_favorite,
                is_watched=is_watched,
                has_next_part=has_next,
                has_prev_part=has_prev,
                next_part_code=next_code,
                prev_part_code=prev_code,
            )

    async def search(
        self,
        filters: SearchFilters,
        page: int = 1,
        per_page: int = 10,
    ) -> SearchResult:
        """Search movies with filters."""
        async with self._uow:
            movies = await self._uow.movies.search(
                query=filters.query,
                year=filters.year,
                quality=filters.quality,
                genre_id=filters.genre_id,
                limit=per_page * 2,  # Get more for pagination estimate
            )

            # Convert to DTOs
            movie_dtos = [self._to_dto(m) for m in movies]

            # Apply pagination
            start = (page - 1) * per_page
            end = start + per_page
            paginated = movie_dtos[start:end]

            return SearchResult(
                movies=paginated,
                total=len(movie_dtos),
                query=filters.query,
                filters=filters,
                page=page,
                per_page=per_page,
            )

    async def get_popular(self, limit: int = 10) -> list[MovieDTO]:
        """Get popular movies."""
        cache_key = f"{self.CACHE_PREFIX}:popular:{limit}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        async with self._uow:
            movies = await self._uow.movies.get_popular(limit)
            dtos = [self._to_dto(m) for m in movies]
            await self._cache.set(cache_key, dtos, 1800)  # 30 min cache
            return dtos

    async def get_recent(self, limit: int = 10) -> list[MovieDTO]:
        """Get recently added movies."""
        async with self._uow:
            movies = await self._uow.movies.get_recent(limit)
            return [self._to_dto(m) for m in movies]

    async def get_top_rated(self, limit: int = 10) -> list[MovieDTO]:
        """Get top rated movies."""
        cache_key = f"{self.CACHE_PREFIX}:top_rated:{limit}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        async with self._uow:
            movies = await self._uow.movies.get_top_rated(limit)
            dtos = [self._to_dto(m) for m in movies]
            await self._cache.set(cache_key, dtos, 1800)
            return dtos

    async def get_count(self) -> int:
        """Get total movie count."""
        async with self._uow:
            return await self._uow.movies.count()

    async def search_advanced(
        self,
        query: str,
        filters: SearchFilters,
        page: int = 1,
        per_page: int = 10,
    ) -> SearchResult:
        """
        Advanced search with multiple filters.

        Args:
            query: Search query
            filters: Search filters
            page: Page number
            per_page: Results per page

        Returns:
            Search result with movies and pagination
        """
        async with self._uow:
            # Get all movies matching query
            movies = await self._uow.movies.search(
                query=query,
                year=filters.year,
                quality=filters.quality,
                genre_id=filters.genre_id,
                limit=100,  # Get more for filtering
            )

            # Apply additional filters
            filtered = []
            for movie in movies:
                # Year range filter
                if filters.year_from and movie.year and movie.year < filters.year_from:
                    continue
                if filters.year_to and movie.year and movie.year > filters.year_to:
                    continue

                # Minimum rating filter
                if filters.min_rating:
                    if float(movie.average_rating) < filters.min_rating:
                        continue

                # Series only filter
                if filters.series_only and not movie.series_id:
                    continue

                filtered.append(movie)

            # Sort results
            if filters.sort_by == "rating":
                filtered.sort(key=lambda m: float(m.average_rating), reverse=True)
            elif filters.sort_by == "downloads":
                filtered.sort(key=lambda m: m.download_count, reverse=True)
            elif filters.sort_by == "newest":
                filtered.sort(key=lambda m: m.year or 0, reverse=True)
            # Default: relevance (original order)

            # Total count before pagination
            total = len(filtered)

            # Apply pagination
            start = (page - 1) * per_page
            end = start + per_page
            paginated = filtered[start:end]

            # Convert to DTOs
            movie_dtos = [self._to_dto(m) for m in paginated]

            return SearchResult(
                movies=movie_dtos,
                total=total,
                query=query,
                filters=filters,
                page=page,
                per_page=per_page,
            )

    def _to_dto(self, movie: Movie) -> MovieDTO:
        """Convert entity to DTO."""
        return MovieDTO(
            id=movie.id,
            code=movie.code,
            title=movie.title,
            file_id=movie.file_id,
            quality=movie.quality,
            year=movie.year,
            duration_minutes=movie.duration_minutes,
            description=movie.description,
            poster_file_id=movie.poster_file_id,
            series_id=movie.series_id,
            part_number=movie.part_number,
            average_rating=movie.average_rating,
            rating_count=movie.rating_count,
            download_count=movie.download_count,
        )
