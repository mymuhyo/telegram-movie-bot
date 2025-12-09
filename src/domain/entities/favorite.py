"""Favorite domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Favorite:
    """Favorite domain entity for user bookmarks."""

    id: UUID
    user_id: UUID
    movie_id: UUID

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
