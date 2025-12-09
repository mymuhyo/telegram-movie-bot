"""Movie DTOs."""

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


@dataclass
class MovieDTO:
    """Movie data transfer object."""

    id: UUID
    code: int
    title: str
    file_id: str

    # Metadata
    quality: str = "HD"
    year: int | None = None
    duration_minutes: int | None = None
    description: str | None = None
    poster_file_id: str | None = None

    # Series
    series_id: UUID | None = None
    series_name: str | None = None
    part_number: int | None = None
    total_parts: int | None = None

    # Ratings
    average_rating: Decimal = field(default_factory=lambda: Decimal("0.00"))
    rating_count: int = 0

    # Stats
    download_count: int = 0

    @property
    def is_series(self) -> bool:
        """Check if movie is part of a series."""
        return self.series_id is not None

    @property
    def rating_display(self) -> str:
        """Get formatted rating display."""
        if self.rating_count == 0:
            return "Baholanmagan"
        stars = int(round(float(self.average_rating)))
        return f"{'⭐' * stars} {self.average_rating:.1f} ({self.rating_count})"


@dataclass
class MovieCardDTO:
    """Complete movie card data for display."""

    movie: MovieDTO

    # User-specific data
    user_rating: int | None = None
    is_favorite: bool = False
    is_watched: bool = False

    # Series navigation
    has_next_part: bool = False
    has_prev_part: bool = False
    next_part_code: int | None = None
    prev_part_code: int | None = None

    # Recommendations
    similar_movies: list[MovieDTO] = field(default_factory=list)


@dataclass
class SearchFilters:
    """Search filter parameters."""

    query: str = ""
    year: int | None = None
    year_from: int | None = None
    year_to: int | None = None
    quality: str | None = None
    genre_id: UUID | None = None
    genre_slug: str | None = None
    min_rating: float | None = None
    series_only: bool = False
    sort_by: str = "relevance"  # relevance, rating, downloads, newest

    @property
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return any([
            self.year,
            self.year_from,
            self.year_to,
            self.quality,
            self.genre_id,
            self.genre_slug,
            self.min_rating,
            self.series_only,
        ])


@dataclass
class SearchResult:
    """Search results container."""

    movies: list[MovieDTO]
    total: int
    query: str
    filters: SearchFilters
    page: int = 1
    per_page: int = 10

    @property
    def has_more(self) -> bool:
        """Check if there are more results."""
        return self.total > self.page * self.per_page

    @property
    def total_pages(self) -> int:
        """Get total number of pages."""
        return (self.total + self.per_page - 1) // self.per_page
