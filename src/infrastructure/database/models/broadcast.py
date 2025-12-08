"""Broadcast database model."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.constants import (
    BROADCAST_CANCELLED,
    BROADCAST_COMPLETED,
    BROADCAST_FAILED,
    BROADCAST_PAUSED,
    BROADCAST_PENDING,
    BROADCAST_RUNNING,
)
from src.infrastructure.database.base import Base, VersionMixin


class BroadcastModel(Base, VersionMixin):
    """Broadcast queue model."""

    __tablename__ = "broadcasts"
    __table_args__ = (
        CheckConstraint(
            f"status IN ('{BROADCAST_PENDING}', '{BROADCAST_RUNNING}', '{BROADCAST_PAUSED}', "
            f"'{BROADCAST_COMPLETED}', '{BROADCAST_CANCELLED}', '{BROADCAST_FAILED}')",
            name="valid_status",
        ),
        CheckConstraint(
            "content_type IN ('text', 'photo', 'video')",
            name="valid_content_type",
        ),
    )

    content_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Progress
    total_users: Mapped[int] = mapped_column(Integer, default=0)
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    fail_count: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(20), default=BROADCAST_PENDING)

    # Error tracking
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Ownership
    started_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_users == 0:
            return 0.0
        return (self.sent_count + self.fail_count) / self.total_users * 100

    def __repr__(self) -> str:
        return f"<Broadcast {self.id} ({self.status})>"
