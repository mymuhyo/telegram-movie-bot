"""Repositories package."""

from src.infrastructure.database.repositories.admin_repo import AdminRepository
from src.infrastructure.database.repositories.base import BaseRepository, SoftDeleteRepository
from src.infrastructure.database.repositories.download_repo import DownloadRepository
from src.infrastructure.database.repositories.favorite_repo import FavoriteRepository
from src.infrastructure.database.repositories.genre_repo import GenreRepository
from src.infrastructure.database.repositories.movie_repo import MovieRepository
from src.infrastructure.database.repositories.rating_repo import RatingRepository
from src.infrastructure.database.repositories.series_progress_repo import SeriesProgressRepository
from src.infrastructure.database.repositories.series_repo import SeriesRepository
from src.infrastructure.database.repositories.setting_repo import SettingRepository
from src.infrastructure.database.repositories.user_repo import UserRepository

__all__ = [
    "BaseRepository",
    "SoftDeleteRepository",
    "MovieRepository",
    "UserRepository",
    "AdminRepository",
    "SettingRepository",
    "DownloadRepository",
    "SeriesRepository",
    # New repositories
    "RatingRepository",
    "FavoriteRepository",
    "GenreRepository",
    "SeriesProgressRepository",
]
