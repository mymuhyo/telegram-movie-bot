"""User DTOs."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class UserDTO:
    """User data transfer object."""

    id: UUID
    telegram_id: int
    username: str | None = None
    full_name: str | None = None

    # Status
    is_banned: bool = False
    ban_reason: str | None = None

    # Stats
    total_downloads: int = 0
    total_ratings: int = 0
    total_favorites: int = 0

    # Timestamps
    joined_at: datetime = field(default_factory=datetime.now)
    last_active_at: datetime | None = None

    @property
    def display_name(self) -> str:
        """Get display name."""
        if self.full_name:
            return self.full_name
        if self.username:
            return f"@{self.username}"
        return str(self.telegram_id)

    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return not self.is_banned
