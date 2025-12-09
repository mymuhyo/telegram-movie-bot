"""Domain Events."""

from src.domain.events.base import DomainEvent
from src.domain.events.movie_events import (
    FavoriteAdded,
    FavoriteRemoved,
    MovieCreated,
    MovieDeleted,
    MovieDownloaded,
    MovieRated,
    SearchPerformed,
    SeriesPartWatched,
)
from src.domain.events.user_events import UserBanned, UserJoined, UserUnbanned

__all__ = [
    "DomainEvent",
    "MovieDownloaded",
    "MovieRated",
    "MovieCreated",
    "MovieDeleted",
    "FavoriteAdded",
    "FavoriteRemoved",
    "SeriesPartWatched",
    "SearchPerformed",
    "UserJoined",
    "UserBanned",
    "UserUnbanned",
]
