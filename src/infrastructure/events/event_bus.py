"""In-memory event bus implementation."""

import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any

from src.application.interfaces import EventBus
from src.domain.events.base import DomainEvent

EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]

logger = logging.getLogger(__name__)


class InMemoryEventBus(EventBus):
    """
    In-memory event bus implementation.

    Simple pub/sub for domain events within a single process.
    For production at scale, consider using Redis Pub/Sub or RabbitMQ.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.

        Executes all handlers concurrently.
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        if not handlers:
            logger.debug(f"No handlers for event: {event_type.__name__}")
            return

        logger.info(
            f"Publishing event {event_type.__name__} to {len(handlers)} handlers"
        )

        # Execute handlers concurrently
        tasks = [self._safe_execute(handler, event) for handler in handlers]
        await asyncio.gather(*tasks)

    def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        """Subscribe to an event type."""
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(
                f"Subscribed handler {handler.__name__} to {event_type.__name__}"
            )

    def unsubscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        """Unsubscribe from an event type."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(
                f"Unsubscribed handler {handler.__name__} from {event_type.__name__}"
            )

    async def _safe_execute(
        self,
        handler: EventHandler,
        event: DomainEvent,
    ) -> None:
        """Execute handler with error handling."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                f"Error in event handler {handler.__name__}: {e}",
                exc_info=True,
            )

    def clear_all(self) -> None:
        """Clear all subscriptions."""
        self._handlers.clear()

    def get_handler_count(self, event_type: type[DomainEvent]) -> int:
        """Get number of handlers for event type."""
        return len(self._handlers.get(event_type, []))
