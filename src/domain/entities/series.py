"""Series domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Series:
    """Series domain entity for multi-part movies."""

    id: UUID
    name: str
    description: str | None = None
    total_parts: int = 1

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_complete(self) -> bool:
        """Check if series info is complete."""
        return self.total_parts > 0
