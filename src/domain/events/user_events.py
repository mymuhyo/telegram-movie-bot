"""User-related domain events."""

from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from src.domain.events.base import DomainEvent


@dataclass
class UserJoined(DomainEvent):
    """Event raised when a new user joins."""

    event_type: ClassVar[str] = "user_joined"

    user_id: UUID = field(default_factory=lambda: UUID(int=0))
    telegram_id: int = 0


@dataclass
class UserBanned(DomainEvent):
    """Event raised when a user is banned."""

    event_type: ClassVar[str] = "user_banned"

    user_id: UUID = field(default_factory=lambda: UUID(int=0))
    telegram_id: int = 0
    reason: str | None = None
    banned_by: int = 0


@dataclass
class UserUnbanned(DomainEvent):
    """Event raised when a user is unbanned."""

    event_type: ClassVar[str] = "user_unbanned"

    user_id: UUID = field(default_factory=lambda: UUID(int=0))
    telegram_id: int = 0
    unbanned_by: int = 0
