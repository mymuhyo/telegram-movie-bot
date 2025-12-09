"""Series DTOs."""

from dataclasses import dataclass, field
from uuid import UUID

from src.application.dto.movie import MovieDTO


@dataclass
class SeriesDTO:
    """Series data transfer object."""

    id: UUID
    name: str
    description: str | None = None
    total_parts: int = 1
    available_parts: int = 0  # Actually uploaded parts

    @property
    def is_complete(self) -> bool:
        """Check if all parts are uploaded."""
        return self.available_parts >= self.total_parts


@dataclass
class SeriesWithPartsDTO:
    """Series with all parts data."""

    series: SeriesDTO
    parts: list[MovieDTO] = field(default_factory=list)

    def get_part(self, part_number: int) -> MovieDTO | None:
        """Get specific part."""
        for part in self.parts:
            if part.part_number == part_number:
                return part
        return None

    def get_next_part(self, current_part: int) -> MovieDTO | None:
        """Get next part after current."""
        for part in self.parts:
            if part.part_number and part.part_number == current_part + 1:
                return part
        return None

    def get_prev_part(self, current_part: int) -> MovieDTO | None:
        """Get previous part."""
        for part in self.parts:
            if part.part_number and part.part_number == current_part - 1:
                return part
        return None


@dataclass
class UserSeriesProgressDTO:
    """User's progress in a series."""

    user_id: UUID
    series_id: UUID
    series_name: str
    total_parts: int
    last_watched_part: int = 1
    completed_parts: list[int] = field(default_factory=list)

    @property
    def watched_count(self) -> int:
        """Get number of watched parts."""
        return len(self.completed_parts)

    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage."""
        if self.total_parts == 0:
            return 0.0
        return (self.watched_count / self.total_parts) * 100

    @property
    def progress_display(self) -> str:
        """Get progress display string."""
        return f"{self.watched_count}/{self.total_parts} ({self.progress_percentage:.0f}%)"

    def is_watched(self, part_number: int) -> bool:
        """Check if part is watched."""
        return part_number in self.completed_parts

    @property
    def next_unwatched(self) -> int | None:
        """Get next unwatched part number."""
        for i in range(1, self.total_parts + 1):
            if i not in self.completed_parts:
                return i
        return None
