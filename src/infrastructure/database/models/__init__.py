"""Database models package."""

from src.infrastructure.database.models.admin import AdminModel
from src.infrastructure.database.models.admin_log import AdminLogModel
from src.infrastructure.database.models.broadcast import BroadcastModel
from src.infrastructure.database.models.download import DownloadModel
from src.infrastructure.database.models.favorite import FavoriteModel
from src.infrastructure.database.models.genre import GenreModel
from src.infrastructure.database.models.movie import MovieModel
from src.infrastructure.database.models.movie_genre import MovieGenreModel
from src.infrastructure.database.models.rating import RatingModel
from src.infrastructure.database.models.request import MovieRequestModel
from src.infrastructure.database.models.series import SeriesModel
from src.infrastructure.database.models.setting import SettingModel
from src.infrastructure.database.models.user import UserModel
from src.infrastructure.database.models.user_series_progress import UserSeriesProgressModel

__all__ = [
    "UserModel",
    "MovieModel",
    "AdminModel",
    "SeriesModel",
    "DownloadModel",
    "MovieRequestModel",
    "AdminLogModel",
    "SettingModel",
    "BroadcastModel",
    # New models
    "RatingModel",
    "FavoriteModel",
    "GenreModel",
    "MovieGenreModel",
    "UserSeriesProgressModel",
]
