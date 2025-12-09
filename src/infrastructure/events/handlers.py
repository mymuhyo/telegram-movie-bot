"""Event handlers for domain events."""

import logging
from typing import TYPE_CHECKING

from src.application.interfaces import CacheInterface
from src.domain.events import (
    DomainEvent,
    FavoriteAdded,
    FavoriteRemoved,
    MovieCreated,
    MovieDeleted,
    MovieDownloaded,
    MovieRated,
    SearchPerformed,
    SeriesPartWatched,
    UserBanned,
    UserJoined,
)

if TYPE_CHECKING:
    from src.application.interfaces import UnitOfWork

logger = logging.getLogger(__name__)


class EventHandlers:
    """
    Domain event handlers.

    Handles side effects of domain events like:
    - Cache invalidation
    - Statistics updates
    - Notifications
    - Analytics
    """

    def __init__(
        self,
        cache: CacheInterface,
    ) -> None:
        self._cache = cache

    async def handle_movie_downloaded(self, event: MovieDownloaded) -> None:
        """
        Handle movie downloaded event.

        Side effects:
        - Invalidate popular movies cache
        - Log for analytics
        """
        logger.info(
            f"Movie downloaded: code={event.movie_code}, "
            f"user={event.user_id}, source={event.source}"
        )

        # Invalidate popular movies cache (download count changed)
        await self._cache.delete("movie:popular:*")

        # Could also:
        # - Send notification to admins for milestones
        # - Update real-time analytics
        # - Trigger recommendation recalculation

    async def handle_movie_rated(self, event: MovieRated) -> None:
        """
        Handle movie rated event.

        Side effects:
        - Invalidate movie cache
        - Invalidate top rated cache
        - Update recommendation cache for user
        """
        logger.info(
            f"Movie rated: movie={event.movie_id}, "
            f"user={event.user_id}, score={event.score}"
        )

        # Invalidate movie-specific cache
        await self._cache.delete(f"movie:id:{event.movie_id}")

        # Invalidate top rated cache
        await self._cache.delete("movie:top_rated:*")

        # Invalidate user's recommendations (preferences changed)
        await self._cache.delete(f"recommendations:user:{event.user_id}:*")

    async def handle_movie_created(self, event: MovieCreated) -> None:
        """
        Handle movie created event.

        Side effects:
        - Invalidate recent movies cache
        - Log for analytics
        """
        logger.info(f"Movie created: id={event.movie_id}, code={event.movie_code}")

        # Invalidate recent movies cache
        await self._cache.delete("movie:recent:*")

        # Could also:
        # - Send notification to subscribed users
        # - Update search index

    async def handle_movie_deleted(self, event: MovieDeleted) -> None:
        """
        Handle movie deleted event.

        Side effects:
        - Invalidate all movie caches
        """
        logger.info(f"Movie deleted: id={event.movie_id}")

        # Invalidate all caches related to this movie
        await self._cache.delete(f"movie:id:{event.movie_id}")
        await self._cache.delete(f"movie:code:*")
        await self._cache.delete("movie:popular:*")
        await self._cache.delete("movie:top_rated:*")
        await self._cache.delete("movie:recent:*")

    async def handle_user_joined(self, event: UserJoined) -> None:
        """
        Handle user joined event.

        Side effects:
        - Log for analytics
        - Could send welcome message
        """
        logger.info(
            f"User joined: telegram_id={event.telegram_id}, "
            f"username={event.username}"
        )

        # Could also:
        # - Send welcome message via bot
        # - Notify admins about milestone (every 100 users)
        # - Add to mailing list

    async def handle_user_banned(self, event: UserBanned) -> None:
        """
        Handle user banned event.

        Side effects:
        - Invalidate user cache
        - Log for audit
        """
        logger.info(
            f"User banned: user_id={event.user_id}, "
            f"reason={event.reason}, by={event.banned_by}"
        )

        # Invalidate user cache
        await self._cache.delete(f"user:{event.user_id}:*")

    async def handle_favorite_added(self, event: FavoriteAdded) -> None:
        """
        Handle favorite added event.

        Side effects:
        - Invalidate user favorites cache
        """
        logger.info(
            f"Favorite added: movie={event.movie_id}, user={event.user_id}"
        )

        # Invalidate user's favorites cache
        await self._cache.delete(f"favorites:user:{event.user_id}:*")

    async def handle_favorite_removed(self, event: FavoriteRemoved) -> None:
        """
        Handle favorite removed event.

        Side effects:
        - Invalidate user favorites cache
        """
        logger.info(
            f"Favorite removed: movie={event.movie_id}, user={event.user_id}"
        )

        await self._cache.delete(f"favorites:user:{event.user_id}:*")

    async def handle_series_part_watched(self, event: SeriesPartWatched) -> None:
        """
        Handle series part watched event.

        Side effects:
        - Invalidate progress cache
        - Log progress
        """
        progress_percent = (event.part_number / event.total_parts) * 100
        logger.info(
            f"Series part watched: series={event.series_id}, "
            f"user={event.user_id}, part={event.part_number}/{event.total_parts} "
            f"({progress_percent:.0f}%)"
        )

        # Invalidate user's series progress cache
        await self._cache.delete(f"series:progress:{event.user_id}:*")

    async def handle_search_performed(self, event: SearchPerformed) -> None:
        """
        Handle search performed event.

        Side effects:
        - Log search for analytics
        """
        logger.info(
            f"Search performed: user={event.user_id}, "
            f"query='{event.query}', results={event.results_count}, "
            f"filters={event.has_filters}"
        )


class AnalyticsHandler:
    """
    Analytics event handler.

    Collects statistics and metrics from domain events.
    """

    def __init__(self, cache: CacheInterface) -> None:
        self._cache = cache

    async def track_download(self, event: MovieDownloaded) -> None:
        """Track download for analytics."""
        # Increment daily downloads counter
        today_key = "analytics:downloads:today"
        await self._cache.increment(today_key)

        # Track by source
        source_key = f"analytics:downloads:source:{event.source}"
        await self._cache.increment(source_key)

    async def track_rating(self, event: MovieRated) -> None:
        """Track rating for analytics."""
        # Increment daily ratings counter
        today_key = "analytics:ratings:today"
        await self._cache.increment(today_key)

        # Track rating distribution
        score_key = f"analytics:ratings:score:{event.score}"
        await self._cache.increment(score_key)

    async def track_user_joined(self, event: UserJoined) -> None:
        """Track new user for analytics."""
        today_key = "analytics:users:today"
        await self._cache.increment(today_key)

    async def track_favorite(self, event: FavoriteAdded) -> None:
        """Track favorite for analytics."""
        today_key = "analytics:favorites:today"
        await self._cache.increment(today_key)

    async def track_search(self, event: SearchPerformed) -> None:
        """Track search for analytics."""
        today_key = "analytics:searches:today"
        await self._cache.increment(today_key)

        # Track searches with no results
        if event.results_count == 0:
            no_results_key = "analytics:searches:no_results"
            await self._cache.increment(no_results_key)


class NotificationHandler:
    """
    Notification event handler.

    Sends notifications based on domain events.
    """

    def __init__(self, bot=None) -> None:
        self._bot = bot

    async def notify_admin_on_milestone(self, event: DomainEvent) -> None:
        """
        Notify admins on milestones.

        Called when certain thresholds are reached.
        """
        # Implementation would use self._bot to send messages
        # to admin chat
        pass

    async def send_welcome_message(self, event: UserJoined) -> None:
        """
        Send welcome message to new user.

        Could be triggered after UserJoined event.
        """
        if self._bot:
            # Implementation would send welcome message
            pass


def setup_event_handlers(
    event_bus,
    cache: CacheInterface,
    bot=None,
) -> None:
    """
    Register all event handlers with the event bus.

    Args:
        event_bus: Event bus instance
        cache: Cache interface
        bot: Telegram bot instance (optional)
    """
    # Main handlers
    handlers = EventHandlers(cache)
    event_bus.subscribe(MovieDownloaded, handlers.handle_movie_downloaded)
    event_bus.subscribe(MovieRated, handlers.handle_movie_rated)
    event_bus.subscribe(MovieCreated, handlers.handle_movie_created)
    event_bus.subscribe(MovieDeleted, handlers.handle_movie_deleted)
    event_bus.subscribe(UserJoined, handlers.handle_user_joined)
    event_bus.subscribe(UserBanned, handlers.handle_user_banned)
    event_bus.subscribe(FavoriteAdded, handlers.handle_favorite_added)
    event_bus.subscribe(FavoriteRemoved, handlers.handle_favorite_removed)
    event_bus.subscribe(SeriesPartWatched, handlers.handle_series_part_watched)
    event_bus.subscribe(SearchPerformed, handlers.handle_search_performed)

    # Analytics handlers
    analytics = AnalyticsHandler(cache)
    event_bus.subscribe(MovieDownloaded, analytics.track_download)
    event_bus.subscribe(MovieRated, analytics.track_rating)
    event_bus.subscribe(UserJoined, analytics.track_user_joined)
    event_bus.subscribe(FavoriteAdded, analytics.track_favorite)
    event_bus.subscribe(SearchPerformed, analytics.track_search)

    # Notification handlers (if bot is available)
    if bot:
        notifications = NotificationHandler(bot)
        event_bus.subscribe(UserJoined, notifications.send_welcome_message)

    logger.info("Event handlers registered successfully")
