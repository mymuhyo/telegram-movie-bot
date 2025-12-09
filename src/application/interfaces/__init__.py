"""Application Interfaces (Ports)."""

from src.application.interfaces.cache import CacheInterface
from src.application.interfaces.event_bus import EventBus
from src.application.interfaces.repositories import (
    AdminRepository,
    DownloadRepository,
    FavoriteRepository,
    GenreRepository,
    MovieRepository,
    RatingRepository,
    SeriesProgressRepository,
    SeriesRepository,
    SettingRepository,
    UserRepository,
)
from src.application.interfaces.unit_of_work import UnitOfWork

__all__ = [
    "MovieRepository",
    "UserRepository",
    "SeriesRepository",
    "RatingRepository",
    "FavoriteRepository",
    "GenreRepository",
    "SeriesProgressRepository",
    "DownloadRepository",
    "AdminRepository",
    "SettingRepository",
    "UnitOfWork",
    "EventBus",
    "CacheInterface",
]
