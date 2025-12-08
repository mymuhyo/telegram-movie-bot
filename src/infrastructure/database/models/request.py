"""Movie request database model."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import STATUS_ADDED, STATUS_APPROVED, STATUS_PENDING, STATUS_REJECTED
from src.infrastructure.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.admin import AdminModel
    from src.infrastructure.database.models.movie import MovieModel
    from src.infrastructure.database.models.user import UserModel


class MovieRequestModel(Base, TimestampMixin):
    """User movie request model."""

    __tablename__ = "movie_requests"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{STATUS_PENDING}', '{STATUS_APPROVED}', '{STATUS_REJECTED}', '{STATUS_ADDED}')",
            name="valid_status",
        ),
    )

    # User relation
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Request content
    movie_title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default=STATUS_PENDING, index=True)
    admin_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Processing
    processed_by: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Fulfilled movie
    fulfilled_movie_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("movies.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="requests")
    processed_by_admin: Mapped[Optional["AdminModel"]] = relationship()
    fulfilled_movie: Mapped[Optional["MovieModel"]] = relationship()

    def __repr__(self) -> str:
        return f"<MovieRequest '{self.movie_title}' ({self.status})>"
