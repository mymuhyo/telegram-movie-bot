"""Domain Entities."""

from src.domain.entities.favorite import Favorite
from src.domain.entities.genre import Genre
from src.domain.entities.movie import Movie
from src.domain.entities.rating import Rating
from src.domain.entities.series import Series
from src.domain.entities.user import User
from src.domain.entities.user_series_progress import UserSeriesProgress

__all__ = [
    "User",
    "Movie",
    "Series",
    "Rating",
    "Favorite",
    "Genre",
    "UserSeriesProgress",
]
