"""Genre database model."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.movie_genre import MovieGenreModel


class GenreModel(Base, TimestampMixin):
    """Genre database model for movie categorization."""

    __tablename__ = "genres"

    # Genre data
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    name_uz: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    # Relationships
    movies: Mapped[list["MovieGenreModel"]] = relationship(
        back_populates="genre",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Genre {self.slug}: {self.name_uz}>"
