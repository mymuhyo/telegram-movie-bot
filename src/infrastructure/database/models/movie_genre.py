"""Movie-Genre junction table model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base

if TYPE_CHECKING:
    from src.infrastructure.database.models.genre import GenreModel
    from src.infrastructure.database.models.movie import MovieModel


class MovieGenreModel(Base):
    """Junction table for movie-genre many-to-many relationship."""

    __tablename__ = "movie_genres"
    __table_args__ = (
        PrimaryKeyConstraint("movie_id", "genre_id"),
    )

    # Override id from Base - we use composite primary key
    id = None  # type: ignore

    # Foreign keys (composite primary key)
    movie_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    genre_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("genres.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    # Relationships
    movie: Mapped["MovieModel"] = relationship(
        back_populates="genres",
        lazy="selectin",
    )
    genre: Mapped["GenreModel"] = relationship(
        back_populates="movies",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<MovieGenre movie={self.movie_id} genre={self.genre_id}>"
