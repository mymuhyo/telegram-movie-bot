"""Base domain event."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    event_type: ClassVar[str] = "domain_event"

    id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.event_type}(id={self.id})"
