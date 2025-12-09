"""Rating domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Rating:
    """Rating domain entity for movie ratings."""

    id: UUID
    user_id: UUID
    movie_id: UUID
    score: int  # 1-5 stars

    review: str | None = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate score after initialization."""
        if not 1 <= self.score <= 5:
            raise ValueError(f"Score must be between 1 and 5, got {self.score}")

    @property
    def stars(self) -> str:
        """Get star representation."""
        return "⭐" * self.score + "☆" * (5 - self.score)
