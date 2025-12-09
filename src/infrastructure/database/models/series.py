"""Series database model."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base, SoftDeleteMixin, TimestampMixin, VersionMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.movie import MovieModel
    from src.infrastructure.database.models.user_series_progress import UserSeriesProgressModel


class SeriesModel(Base, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """Series database model for multi-part movies."""

    __tablename__ = "series"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_parts: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    movies: Mapped[list["MovieModel"]] = relationship(
        back_populates="series",
        lazy="selectin",
        order_by="MovieModel.part_number",
    )
    user_progress: Mapped[list["UserSeriesProgressModel"]] = relationship(
        back_populates="series",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Series {self.name} ({self.total_parts} parts)>"
