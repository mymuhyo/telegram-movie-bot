"""User keyboards."""

from src.presentation.keyboards.user.favorite import FavoriteKeyboard
from src.presentation.keyboards.user.movie_card import MovieCardKeyboard
from src.presentation.keyboards.user.rating import RatingKeyboard
from src.presentation.keyboards.user.recommendation import RecommendationKeyboard
from src.presentation.keyboards.user.search import SearchKeyboard
from src.presentation.keyboards.user.series import SeriesKeyboard

__all__ = [
    "MovieCardKeyboard",
    "RatingKeyboard",
    "FavoriteKeyboard",
    "SeriesKeyboard",
    "RecommendationKeyboard",
    "SearchKeyboard",
]
