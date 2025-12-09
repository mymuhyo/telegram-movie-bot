"""User handlers."""

from src.presentation.handlers.user.favorite import router as favorite_router
from src.presentation.handlers.user.rating import router as rating_router
from src.presentation.handlers.user.recommendation import router as recommendation_router
from src.presentation.handlers.user.search import router as search_router
from src.presentation.handlers.user.series import router as series_router

__all__ = [
    "rating_router",
    "favorite_router",
    "series_router",
    "recommendation_router",
    "search_router",
]
