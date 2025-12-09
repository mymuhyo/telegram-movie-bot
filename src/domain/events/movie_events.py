"""Movie-related domain events."""

from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from src.domain.events.base import DomainEvent


@dataclass
class MovieDownloaded(DomainEvent):
    """Event raised when a user downloads a movie."""

    event_type: ClassVar[str] = "movie_downloaded"

    movie_id: UUID = field(default_factory=lambda: UUID(int=0))
    movie_code: int = 0
    user_id: UUID = field(default_factory=lambda: UUID(int=0))
    source: str = "code"  # code, search, series, recommendation


@dataclass
class MovieRated(DomainEvent):
    """Event raised when a user rates a movie."""

    event_type: ClassVar[str] = "movie_rated"

    movie_id: UUID = field(default_factory=lambda: UUID(int=0))
    user_id: UUID = field(default_factory=lambda: UUID(int=0))
    score: int = 0
    previous_score: int | None = None


@dataclass
class MovieCreated(DomainEvent):
    """Event raised when a new movie is added."""

    event_type: ClassVar[str] = "movie_created"

    movie_id: UUID = field(default_factory=lambda: UUID(int=0))
    movie_code: int = 0
    added_by: int = 0


@dataclass
class MovieDeleted(DomainEvent):
    """Event raised when a movie is deleted."""

    event_type: ClassVar[str] = "movie_deleted"

    movie_id: UUID = field(default_factory=lambda: UUID(int=0))
    movie_code: int = 0
    deleted_by: int = 0


@dataclass
class FavoriteAdded(DomainEvent):
    """Event raised when user adds movie to favorites."""

    event_type: ClassVar[str] = "favorite_added"

    movie_id: UUID = field(default_factory=lambda: UUID(int=0))
    user_id: UUID = field(default_factory=lambda: UUID(int=0))


@dataclass
class FavoriteRemoved(DomainEvent):
    """Event raised when user removes movie from favorites."""

    event_type: ClassVar[str] = "favorite_removed"

    movie_id: UUID = field(default_factory=lambda: UUID(int=0))
    user_id: UUID = field(default_factory=lambda: UUID(int=0))


@dataclass
class SeriesPartWatched(DomainEvent):
    """Event raised when user watches a series part."""

    event_type: ClassVar[str] = "series_part_watched"

    series_id: UUID = field(default_factory=lambda: UUID(int=0))
    user_id: UUID = field(default_factory=lambda: UUID(int=0))
    part_number: int = 0
    total_parts: int = 0


@dataclass
class SearchPerformed(DomainEvent):
    """Event raised when user performs a search."""

    event_type: ClassVar[str] = "search_performed"

    user_id: UUID = field(default_factory=lambda: UUID(int=0))
    query: str = ""
    results_count: int = 0
    has_filters: bool = False
