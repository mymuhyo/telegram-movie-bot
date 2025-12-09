"""Favorite database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.movie import MovieModel
    from src.infrastructure.database.models.user import UserModel


class FavoriteModel(Base, TimestampMixin):
    """Favorite database model for user bookmarks."""

    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_favorite"),
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    movie_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        back_populates="favorites",
        lazy="selectin",
    )
    movie: Mapped["MovieModel"] = relationship(
        back_populates="favorites",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Favorite user={self.user_id} movie={self.movie_id}>"
