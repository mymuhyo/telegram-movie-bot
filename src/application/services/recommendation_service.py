"""Recommendation application service."""

from uuid import UUID

from src.application.dto import MovieDTO
from src.application.interfaces import CacheInterface, UnitOfWork
from src.domain.entities import Movie
from src.domain.services import RecommendationEngine


class RecommendationService:
    """Application service for movie recommendations."""

    CACHE_TTL = 1800  # 30 minutes
    CACHE_PREFIX = "recommendations"

    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheInterface,
    ) -> None:
        self._uow = uow
        self._cache = cache
        self._engine = RecommendationEngine()

    async def get_recommendations(
        self,
        user_id: UUID,
        limit: int = 5,
    ) -> list[MovieDTO]:
        """
        Get personalized recommendations for user.

        Based on:
        - User's download history
        - User's ratings (prefer similar to highly rated)
        - Popular movies user hasn't seen
        - Series continuations

        Args:
            user_id: User ID
            limit: Max recommendations

        Returns:
            List of recommended movies
        """
        cache_key = f"{self.CACHE_PREFIX}:user:{user_id}:{limit}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        async with self._uow:
            # Get user's watch history
            watched_ids = await self._uow.downloads.get_user_movie_ids(user_id)

            # Get user's ratings
            ratings = await self._uow.ratings.get_by_user(user_id)
            rating_map = {r.movie_id: r.score for r in ratings}

            # Get watched movies for preference analysis
            watched_movies: list[Movie] = []
            for movie_id in list(watched_ids)[:50]:  # Limit for performance
                movie = await self._uow.movies.get_by_id(movie_id)
                if movie:
                    watched_movies.append(movie)

            # Calculate preferences
            genre_prefs = self._engine.get_genre_preferences(watched_movies, rating_map)
            favorite_years = self._engine.get_favorite_years(watched_movies)

            # Get candidate movies
            candidates: list[Movie] = []

            # 1. Popular movies
            popular = await self._uow.movies.get_popular(30)
            candidates.extend(popular)

            # 2. Top rated movies
            top_rated = await self._uow.movies.get_top_rated(20)
            candidates.extend(top_rated)

            # 3. Recent movies
            recent = await self._uow.movies.get_recent(20)
            candidates.extend(recent)

            # Remove duplicates
            seen_ids: set[UUID] = set()
            unique_candidates: list[Movie] = []
            for movie in candidates:
                if movie.id not in seen_ids:
                    seen_ids.add(movie.id)
                    unique_candidates.append(movie)

            # Rank recommendations
            recommended = self._engine.rank_movies(
                movies=unique_candidates,
                user_genre_preferences=genre_prefs,
                user_watched_ids=watched_ids,
                favorite_years=favorite_years,
                limit=limit,
            )

            dtos = [self._movie_to_dto(m) for m in recommended]
            await self._cache.set(cache_key, dtos, self.CACHE_TTL)
            return dtos

    async def get_similar_movies(
        self,
        movie_id: UUID,
        limit: int = 5,
    ) -> list[MovieDTO]:
        """
        Get similar movies.

        Based on:
        - Same series
        - Same year range
        - Similar popularity

        Args:
            movie_id: Reference movie ID
            limit: Max similar movies

        Returns:
            List of similar movies
        """
        cache_key = f"{self.CACHE_PREFIX}:similar:{movie_id}:{limit}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        async with self._uow:
            movie = await self._uow.movies.get_by_id(movie_id)
            if not movie:
                return []

            similar: list[Movie] = []

            # Same series
            if movie.series_id:
                series_movies = await self._uow.movies.get_by_series(movie.series_id)
                similar.extend([m for m in series_movies if m.id != movie_id])

            # Same year range
            if movie.year:
                # Get movies within 3 years
                candidates = await self._uow.movies.get_recent(50)
                for m in candidates:
                    if m.id != movie_id and m.year:
                        if abs(m.year - movie.year) <= 3:
                            if m not in similar:
                                similar.append(m)

            # Limit and convert
            similar = similar[:limit]
            dtos = [self._movie_to_dto(m) for m in similar]
            await self._cache.set(cache_key, dtos, self.CACHE_TTL)
            return dtos

    async def get_continue_watching(
        self,
        user_id: UUID,
        limit: int = 3,
    ) -> list[MovieDTO]:
        """
        Get series to continue watching.

        Args:
            user_id: User ID
            limit: Max series to return

        Returns:
            List of next unwatched parts
        """
        async with self._uow:
            progress_list = await self._uow.series_progress.get_by_user(user_id)
            continue_movies: list[Movie] = []

            for progress in progress_list[:limit]:
                series = await self._uow.series.get_by_id(progress.series_id)
                if not series:
                    continue

                # Find next unwatched part
                next_part = progress.last_watched_part + 1
                if next_part <= series.total_parts:
                    movies = await self._uow.movies.get_by_series(series.id)
                    for movie in movies:
                        if movie.part_number == next_part:
                            continue_movies.append(movie)
                            break

            return [self._movie_to_dto(m) for m in continue_movies]

    def _movie_to_dto(self, movie: Movie) -> MovieDTO:
        """Convert movie entity to DTO."""
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
