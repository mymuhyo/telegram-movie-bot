"""Event Bus interface."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any

from src.domain.events.base import DomainEvent

EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus(ABC):
    """Event bus interface for publishing and subscribing to domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.

        Args:
            event: The event to publish
        """
        pass

    @abstractmethod
    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to subscribe to
            handler: Async function to handle the event
        """
        pass

    @abstractmethod
    def unsubscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: The type of event to unsubscribe from
            handler: The handler to remove
        """
        pass
