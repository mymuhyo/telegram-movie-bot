"""Movie Code value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MovieCode:
    """Value object for validated movie codes."""

    value: int

    def __post_init__(self) -> None:
        """Validate movie code."""
        if self.value < 1:
            raise ValueError(f"Movie code must be positive, got {self.value}")
        if self.value > 999999:
            raise ValueError(f"Movie code too large: {self.value}")

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)

    def __int__(self) -> int:
        """Integer representation."""
        return self.value

    @classmethod
    def from_string(cls, text: str) -> "MovieCode":
        """Create MovieCode from string."""
        try:
            return cls(int(text.strip()))
        except ValueError as e:
            raise ValueError(f"Invalid movie code: {text}") from e

    @classmethod
    def is_valid(cls, text: str) -> bool:
        """Check if text is a valid movie code."""
        try:
            cls.from_string(text)
            return True
        except ValueError:
            return False
