"""Data Transfer Objects."""

from src.application.dto.movie import (
    MovieCardDTO,
    MovieDTO,
    SearchFilters,
    SearchResult,
)
from src.application.dto.pagination import PaginatedResult
from src.application.dto.rating import RatingDTO, RatingStatsDTO
from src.application.dto.series import SeriesDTO, SeriesWithPartsDTO, UserSeriesProgressDTO
from src.application.dto.user import UserDTO

__all__ = [
    "MovieDTO",
    "MovieCardDTO",
    "SearchFilters",
    "SearchResult",
    "RatingDTO",
    "RatingStatsDTO",
    "SeriesDTO",
    "SeriesWithPartsDTO",
    "UserSeriesProgressDTO",
    "UserDTO",
    "PaginatedResult",
]
