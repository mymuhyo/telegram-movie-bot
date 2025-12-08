"""Download database model."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import SOURCE_CODE, SOURCE_SEARCH, SOURCE_SERIES
from src.infrastructure.database.base import Base
from src.infrastructure.database.models.movie import MovieModel
from src.infrastructure.database.models.user import UserModel


class DownloadModel(Base):
    """Download tracking model."""

    __tablename__ = "downloads"
    __table_args__ = (
        CheckConstraint(
            f"source IN ('{SOURCE_CODE}', '{SOURCE_SEARCH}', '{SOURCE_SERIES}')",
            name="valid_source",
        ),
    )

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

    # Denormalized for faster analytics
    movie_code: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(20), default=SOURCE_CODE)

    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="downloads")
    movie: Mapped["MovieModel"] = relationship(back_populates="downloads")

    def __repr__(self) -> str:
        return f"<Download user={self.user_id} movie={self.movie_code}>"
