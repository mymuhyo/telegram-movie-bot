"""Rating DTOs."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class RatingDTO:
    """Rating data transfer object."""

    id: UUID
    user_id: UUID
    movie_id: UUID
    score: int
    review: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def stars(self) -> str:
        """Get star representation."""
        return "⭐" * self.score + "☆" * (5 - self.score)


@dataclass
class RatingStatsDTO:
    """Rating statistics for a movie."""

    movie_id: UUID
    average: float
    count: int
    distribution: dict[int, int] = field(
        default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    )

    @property
    def average_display(self) -> str:
        """Get formatted average display."""
        if self.count == 0:
            return "Baholanmagan"
        stars = int(round(self.average))
        return f"{'⭐' * stars} {self.average:.1f}"

    def get_percentage(self, score: int) -> float:
        """Get percentage for a score."""
        if self.count == 0:
            return 0.0
        return (self.distribution.get(score, 0) / self.count) * 100
