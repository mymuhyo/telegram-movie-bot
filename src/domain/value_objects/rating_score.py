"""Rating Score value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RatingScore:
    """Value object for validated rating scores (1-5)."""

    value: int

    MIN_SCORE = 1
    MAX_SCORE = 5

    def __post_init__(self) -> None:
        """Validate rating score."""
        if not self.MIN_SCORE <= self.value <= self.MAX_SCORE:
            raise ValueError(
                f"Rating must be between {self.MIN_SCORE} and {self.MAX_SCORE}, "
                f"got {self.value}"
            )

    def __str__(self) -> str:
        """String representation with stars."""
        return self.stars

    def __int__(self) -> int:
        """Integer representation."""
        return self.value

    @property
    def stars(self) -> str:
        """Get star representation."""
        return "⭐" * self.value + "☆" * (self.MAX_SCORE - self.value)

    @property
    def filled_stars(self) -> str:
        """Get only filled stars."""
        return "⭐" * self.value

    @classmethod
    def from_string(cls, text: str) -> "RatingScore":
        """Create RatingScore from string."""
        try:
            return cls(int(text.strip()))
        except ValueError as e:
            raise ValueError(f"Invalid rating: {text}") from e

    @classmethod
    def is_valid(cls, value: int) -> bool:
        """Check if value is a valid rating."""
        return cls.MIN_SCORE <= value <= cls.MAX_SCORE
