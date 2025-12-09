"""Application Services (Use Cases)."""

from src.application.services.favorite_service import FavoriteService
from src.application.services.movie_service import MovieService
from src.application.services.rating_service import RatingService
from src.application.services.recommendation_service import RecommendationService
from src.application.services.series_service import SeriesService
from src.application.services.user_service import UserService

__all__ = [
    "MovieService",
    "UserService",
    "RatingService",
    "SeriesService",
    "FavoriteService",
    "RecommendationService",
]
