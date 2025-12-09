"""Rating database model."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.movie import MovieModel
    from src.infrastructure.database.models.user import UserModel


class RatingModel(Base, TimestampMixin):
    """Rating database model for movie ratings."""

    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_rating"),
        CheckConstraint("score >= 1 AND score <= 5", name="valid_score"),
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

    # Rating data
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    review: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["UserModel"] = relationship(
        back_populates="ratings",
        lazy="selectin",
    )
    movie: Mapped["MovieModel"] = relationship(
        back_populates="ratings",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Rating user={self.user_id} movie={self.movie_id} score={self.score}>"
