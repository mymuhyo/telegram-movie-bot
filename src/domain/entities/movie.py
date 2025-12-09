"""Movie domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Movie:
    """Movie domain entity."""

    id: UUID
    code: int
    title: str
    file_id: str

    # Relations
    series_id: UUID | None = None
    part_number: int | None = None

    # Metadata
    quality: str = "HD"
    year: int | None = None
    duration_minutes: int | None = None
    description: str | None = None
    poster_file_id: str | None = None
    language: str = "uz"
    country: str | None = None

    # Ratings
    average_rating: Decimal = field(default_factory=lambda: Decimal("0.00"))
    rating_count: int = 0

    # Tracking
    added_by: int = 0
    download_count: int = 0
    is_active: bool = True

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_series_part(self) -> bool:
        """Check if movie is part of a series."""
        return self.series_id is not None and self.part_number is not None

    @property
    def formatted_rating(self) -> str:
        """Get formatted rating string."""
        if self.rating_count == 0:
            return "Baholanmagan"
        stars = int(round(float(self.average_rating)))
        return f"{'⭐' * stars} ({self.average_rating:.1f})"

    @property
    def formatted_duration(self) -> str:
        """Get formatted duration string."""
        if not self.duration_minutes:
            return ""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}s {minutes}d"
        return f"{minutes} daqiqa"
