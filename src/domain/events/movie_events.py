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
