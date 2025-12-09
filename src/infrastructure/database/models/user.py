"""User database model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base, SoftDeleteMixin, TimestampMixin, VersionMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.download import DownloadModel
    from src.infrastructure.database.models.favorite import FavoriteModel
    from src.infrastructure.database.models.rating import RatingModel
    from src.infrastructure.database.models.request import MovieRequestModel
    from src.infrastructure.database.models.user_series_progress import UserSeriesProgressModel


class UserModel(Base, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """User database model."""

    __tablename__ = "users"

    # Telegram data
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="uz")

    # Status
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    banned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    banned_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    # Activity
    total_downloads: Mapped[int] = mapped_column(default=0)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps (from mixin, but we rename for users)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    downloads: Mapped[list["DownloadModel"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
    requests: Mapped[list["MovieRequestModel"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
    ratings: Mapped[list["RatingModel"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
    favorites: Mapped[list["FavoriteModel"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
    series_progress: Mapped[list["UserSeriesProgressModel"]] = relationship(
        back_populates="user",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} @{self.username}>"
