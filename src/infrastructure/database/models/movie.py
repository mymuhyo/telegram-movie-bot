"""Movie database model."""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base, SoftDeleteMixin, TimestampMixin, VersionMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.download import DownloadModel
    from src.infrastructure.database.models.favorite import FavoriteModel
    from src.infrastructure.database.models.movie_genre import MovieGenreModel
    from src.infrastructure.database.models.rating import RatingModel
    from src.infrastructure.database.models.series import SeriesModel


class MovieModel(Base, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """Movie database model."""

    __tablename__ = "movies"
    __table_args__ = (
        CheckConstraint("year IS NULL OR (year >= 1900 AND year <= 2100)", name="valid_year"),
        CheckConstraint("duration_minutes IS NULL OR duration_minutes > 0", name="valid_duration"),
        CheckConstraint("average_rating >= 0 AND average_rating <= 5", name="valid_rating"),
    )

    # Core fields
    code: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Series relation
    series_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("series.id", ondelete="SET NULL"),
        nullable=True,
    )
    part_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Metadata
    quality: Mapped[str] = mapped_column(String(20), default="HD")
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    poster_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="uz")
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Rating fields (NEW)
    average_rating: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Tracking
    added_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    series: Mapped[Optional["SeriesModel"]] = relationship(
        back_populates="movies",
        lazy="selectin",
    )
    downloads: Mapped[list["DownloadModel"]] = relationship(
        back_populates="movie",
        lazy="selectin",
    )
    ratings: Mapped[list["RatingModel"]] = relationship(
        back_populates="movie",
        lazy="selectin",
    )
    favorites: Mapped[list["FavoriteModel"]] = relationship(
        back_populates="movie",
        lazy="selectin",
    )
    genres: Mapped[list["MovieGenreModel"]] = relationship(
        back_populates="movie",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Movie {self.code}: {self.title}>"
