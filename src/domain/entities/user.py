"""User domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    """User domain entity representing a bot user."""

    id: UUID
    telegram_id: int
    username: str | None = None
    full_name: str | None = None
    language_code: str = "uz"

    # Status
    is_banned: bool = False
    ban_reason: str | None = None
    banned_at: datetime | None = None

    # Activity
    total_downloads: int = 0
    last_active_at: datetime | None = None

    # Timestamps
    joined_at: datetime = field(default_factory=datetime.now)

    @property
    def display_name(self) -> str:
        """Get user display name."""
        if self.full_name:
            return self.full_name
        if self.username:
            return f"@{self.username}"
        return str(self.telegram_id)

    @property
    def is_active(self) -> bool:
        """Check if user is active (not banned)."""
        return not self.is_banned
