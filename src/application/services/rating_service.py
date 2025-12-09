"""Rating application service."""

from uuid import UUID

from src.application.dto import RatingDTO, RatingStatsDTO
from src.application.interfaces import CacheInterface, EventBus, UnitOfWork
from src.core.exceptions import MovieNotFoundError
from src.domain.events import MovieRated
from src.domain.services import RatingCalculator


class RatingService:
    """Application service for rating operations."""

    CACHE_PREFIX = "rating"

    def __init__(
        self,
        uow: UnitOfWork,
        cache: CacheInterface,
        event_bus: EventBus,
    ) -> None:
        self._uow = uow
        self._cache = cache
        self._event_bus = event_bus
        self._calculator = RatingCalculator()

    async def rate_movie(
        self,
        user_id: UUID,
        movie_id: UUID,
        score: int,
    ) -> RatingDTO:
        """
        Rate a movie.

        Args:
            user_id: User ID
            movie_id: Movie ID
            score: Rating score (1-5)

        Returns:
            Rating DTO

        Raises:
            ValueError: If score is invalid
            MovieNotFoundError: If movie not found
        """
        if not 1 <= score <= 5:
            raise ValueError(f"Score must be between 1 and 5, got {score}")

        async with self._uow:
            # Verify movie exists
            movie = await self._uow.movies.get_by_id(movie_id)
            if not movie:
                raise MovieNotFoundError(movie_id)

            # Create or update rating
            rating, old_score = await self._uow.ratings.upsert(
                user_id=user_id,
                movie_id=movie_id,
                score=score,
            )

            # Update movie average
            new_avg, new_count = self._calculator.calculate_average(
                current_average=movie.average_rating,
                current_count=movie.rating_count,
                new_score=score,
                old_score=old_score,
            )
            await self._uow.movies.update_rating(movie_id, float(new_avg), new_count)

            await self._uow.commit()

            # Invalidate cache
            await self._cache.delete(f"movie:code:{movie.code}")
            await self._cache.delete(f"{self.CACHE_PREFIX}:stats:{movie_id}")

            # Publish event
            await self._event_bus.publish(
                MovieRated(
                    movie_id=movie_id,
                    user_id=user_id,
                    score=score,
                    previous_score=old_score,
                )
            )

            return RatingDTO(
                id=rating.id,
                user_id=rating.user_id,
                movie_id=rating.movie_id,
                score=rating.score,
                review=rating.review,
                created_at=rating.created_at,
            )

    async def get_user_rating(
        self,
        user_id: UUID,
        movie_id: UUID,
    ) -> int | None:
        """Get user's rating for a movie."""
        async with self._uow:
            rating = await self._uow.ratings.get_by_user_and_movie(user_id, movie_id)
            return rating.score if rating else None

    async def get_movie_stats(self, movie_id: UUID) -> RatingStatsDTO:
        """Get rating statistics for a movie."""
        cache_key = f"{self.CACHE_PREFIX}:stats:{movie_id}"
        cached = await self._cache.get(cache_key)
        if cached:
            return cached

        async with self._uow:
            ratings = await self._uow.ratings.get_by_movie(movie_id)
            scores = [r.score for r in ratings]

            average = float(self._calculator.calculate_from_scores(scores))
            distribution = self._calculator.get_distribution(scores)

            stats = RatingStatsDTO(
                movie_id=movie_id,
                average=average,
                count=len(scores),
                distribution=distribution,
            )

            await self._cache.set(cache_key, stats, 1800)
            return stats

    async def get_user_ratings(
        self,
        user_id: UUID,
        limit: int = 50,
    ) -> list[RatingDTO]:
        """Get user's rating history."""
        async with self._uow:
            ratings = await self._uow.ratings.get_by_user(user_id, limit)
            return [
                RatingDTO(
                    id=r.id,
                    user_id=r.user_id,
                    movie_id=r.movie_id,
                    score=r.score,
                    review=r.review,
                    created_at=r.created_at,
                )
                for r in ratings
            ]
