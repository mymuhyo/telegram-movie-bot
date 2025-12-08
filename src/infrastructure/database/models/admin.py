"""Admin database model."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.constants import ROLE_ADMIN, ROLE_SUPER_ADMIN
from src.infrastructure.database.base import Base, SoftDeleteMixin, TimestampMixin, VersionMixin

if TYPE_CHECKING:
    from src.infrastructure.database.models.admin_log import AdminLogModel


class AdminModel(Base, TimestampMixin, SoftDeleteMixin, VersionMixin):
    """Admin database model."""

    __tablename__ = "admins"
    __table_args__ = (
        CheckConstraint(
            f"role IN ('{ROLE_SUPER_ADMIN}', '{ROLE_ADMIN}')",
            name="valid_role",
        ),
    )

    # Telegram data
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Role
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    # Activity
    last_action_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    logs: Mapped[list["AdminLogModel"]] = relationship(
        back_populates="admin",
        lazy="selectin",
    )

    @property
    def is_super_admin(self) -> bool:
        """Check if admin is super admin."""
        return self.role == ROLE_SUPER_ADMIN

    def __repr__(self) -> str:
        return f"<Admin {self.telegram_id} @{self.username} ({self.role})>"
