"""Pagination DTOs."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    """Paginated result container."""

    items: list[T]
    total: int
    page: int = 1
    per_page: int = 10

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page * self.per_page < self.total

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1

    @property
    def total_pages(self) -> int:
        """Get total number of pages."""
        if self.per_page == 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def start_index(self) -> int:
        """Get start index (1-based) for display."""
        return (self.page - 1) * self.per_page + 1

    @property
    def end_index(self) -> int:
        """Get end index for display."""
        return min(self.page * self.per_page, self.total)

    @property
    def is_empty(self) -> bool:
        """Check if result is empty."""
        return len(self.items) == 0
