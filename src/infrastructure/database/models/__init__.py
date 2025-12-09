"""Database models package."""

from src.infrastructure.database.models.admin import AdminModel
from src.infrastructure.database.models.admin_log import AdminLogModel
from src.infrastructure.database.models.broadcast import BroadcastModel
from src.infrastructure.database.models.download import DownloadModel
from src.infrastructure.database.models.movie import MovieModel
from src.infrastructure.database.models.request import MovieRequestModel
from src.infrastructure.database.models.series import SeriesModel
from src.infrastructure.database.models.setting import SettingModel
from src.infrastructure.database.models.user import UserModel

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
]
