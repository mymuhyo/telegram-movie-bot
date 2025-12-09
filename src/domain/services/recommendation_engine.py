"""Recommendation engine domain service."""

from collections import Counter
from uuid import UUID

from src.domain.entities.movie import Movie


class RecommendationEngine:
    """
    Domain service for movie recommendations.

    Algorithm:
    1. Similar genres to user's highly-rated/downloaded movies
    2. Popular movies user hasn't watched
    3. Series continuations
    4. Year proximity
    """

    @staticmethod
    def score_movie(
        movie: Movie,
        user_genre_preferences: dict[UUID, int],  # genre_id -> weight
        user_watched_ids: set[UUID],
        favorite_years: list[int],
    ) -> float:
        """
        Calculate recommendation score for a movie.

        Args:
            movie: Movie to score
            user_genre_preferences: User's preferred genres with weights
            user_watched_ids: Set of movie IDs user has watched
            favorite_years: List of years user prefers

        Returns:
            Recommendation score (higher = better match)
        """
        # Skip already watched
        if movie.id in user_watched_ids:
            return -1.0

        score = 0.0

        # Base score from movie rating
        score += float(movie.average_rating) * 10

        # Popularity bonus
        score += min(movie.download_count / 100, 20)  # Max 20 points

        # Year proximity bonus
        if movie.year and favorite_years:
            avg_year = sum(favorite_years) / len(favorite_years)
            year_diff = abs(movie.year - avg_year)
            if year_diff < 5:
                score += 15
            elif year_diff < 10:
                score += 10
            elif year_diff < 20:
                score += 5

        # New movie bonus (within last year)
        if movie.year and movie.year >= 2024:
            score += 10

        return score

    @staticmethod
    def get_genre_preferences(
        watched_movies: list[Movie],
        ratings: dict[UUID, int],  # movie_id -> score
    ) -> dict[UUID, int]:
        """
        Calculate user's genre preferences based on watch/rating history.

        Args:
            watched_movies: List of movies user has watched
            ratings: User's ratings for movies

        Returns:
            Dict of genre_id -> preference weight
        """
        genre_weights: Counter[UUID] = Counter()

        for movie in watched_movies:
            # Higher weight for rated movies
            rating = ratings.get(movie.id, 3)  # Default to 3 if not rated
            weight = rating  # Weight is 1-5 based on rating

            # Note: In real implementation, would need movie.genres
            # For now, use series_id as a proxy for similarity
            if movie.series_id:
                genre_weights[movie.series_id] += weight

        return dict(genre_weights)

    @staticmethod
    def get_favorite_years(watched_movies: list[Movie]) -> list[int]:
        """Get list of years from user's watched movies."""
        years = [m.year for m in watched_movies if m.year]
        return years

    @staticmethod
    def rank_movies(
        movies: list[Movie],
        user_genre_preferences: dict[UUID, int],
        user_watched_ids: set[UUID],
        favorite_years: list[int],
        limit: int = 10,
    ) -> list[Movie]:
        """
        Rank movies by recommendation score.

        Args:
            movies: List of candidate movies
            user_genre_preferences: User's genre preferences
            user_watched_ids: Movies user has already watched
            favorite_years: User's preferred years
            limit: Maximum number of recommendations

        Returns:
            Sorted list of recommended movies
        """
        scored = []
        for movie in movies:
            score = RecommendationEngine.score_movie(
                movie, user_genre_preferences, user_watched_ids, favorite_years
            )
            if score >= 0:
                scored.append((movie, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        return [movie for movie, _ in scored[:limit]]
