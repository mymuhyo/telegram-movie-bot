"""User Series Progress database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.series import SeriesModel
    from src.infrastructure.database.models.user import UserModel


class UserSeriesProgressModel(Base, TimestampMixin):
    """Tracks user's progress in watching a series."""

    __tablename__ = "user_series_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "series_id", name="uq_user_series_progress"),
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    series_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("series.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Progress data
    last_watched_part: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    completed_parts: Mapped[list[int]] = mapped_column(
        ARRAY(Integer),
        default=[],
        nullable=False,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        back_populates="series_progress",
        lazy="selectin",
    )
    series: Mapped["SeriesModel"] = relationship(
        back_populates="user_progress",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<UserSeriesProgress user={self.user_id} series={self.series_id} part={self.last_watched_part}>"
