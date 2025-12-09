"""Genre domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Genre:
    """Genre domain entity for movie categorization."""

    id: UUID
    name: str  # English name
    name_uz: str  # Uzbek name
    slug: str  # URL-friendly slug

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def display_name(self) -> str:
        """Get display name (Uzbek preferred)."""
        return self.name_uz or self.name
