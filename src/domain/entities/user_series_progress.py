"""User Series Progress domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class UserSeriesProgress:
    """Tracks user's progress in watching a series."""

    id: UUID
    user_id: UUID
    series_id: UUID

    last_watched_part: int = 1
    completed_parts: list[int] = field(default_factory=list)

    # Timestamps
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def watched_count(self) -> int:
        """Get number of watched parts."""
        return len(self.completed_parts)

    def is_part_watched(self, part_number: int) -> bool:
        """Check if a specific part is watched."""
        return part_number in self.completed_parts

    def mark_watched(self, part_number: int) -> None:
        """Mark a part as watched."""
        if part_number not in self.completed_parts:
            self.completed_parts.append(part_number)
            self.completed_parts.sort()
        if part_number > self.last_watched_part:
            self.last_watched_part = part_number
        self.updated_at = datetime.now()
