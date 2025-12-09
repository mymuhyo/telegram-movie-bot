"""Bot handlers."""

from src.presentation.handlers.user.favorite import router as favorite_router
from src.presentation.handlers.user.rating import router as rating_router
from src.presentation.handlers.user.series import router as series_router

__all__ = ["rating_router", "favorite_router", "series_router"]
