"""Dependency Injection Providers."""

from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.interfaces import (
    CacheInterface,
    EventBus,
    UnitOfWork,
)
from src.application.services import (
    FavoriteService,
    MovieService,
    RatingService,
    RecommendationService,
    SeriesService,
    UserService,
)


class DatabaseProvider(Provider):
    """Database dependencies provider."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self._session_factory = session_factory

    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        """Provide database session."""
        async with self._session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_uow(self, session: AsyncSession) -> AsyncIterator[UnitOfWork]:
        """Provide Unit of Work."""
        from src.infrastructure.unit_of_work import SQLAlchemyUnitOfWork

        uow = SQLAlchemyUnitOfWork(session)
        yield uow


class CacheProvider(Provider):
    """Cache dependencies provider."""

    def __init__(self, redis_url: str | None = None) -> None:
        super().__init__()
        self._redis_url = redis_url

    @provide(scope=Scope.APP)
    async def get_cache(self) -> CacheInterface:
        """Provide cache interface."""
        from src.infrastructure.cache.redis_cache import RedisCache
        from src.infrastructure.cache.memory_cache import MemoryCache

        if self._redis_url:
            try:
                cache = RedisCache(self._redis_url)
                await cache.connect()
                return cache
            except Exception:
                pass

        return MemoryCache()


class EventBusProvider(Provider):
    """Event bus dependencies provider."""

    @provide(scope=Scope.APP)
    def get_event_bus(self) -> EventBus:
        """Provide event bus."""
        from src.infrastructure.events.event_bus import InMemoryEventBus

        return InMemoryEventBus()


class ServiceProvider(Provider):
    """Application services provider."""

    @provide(scope=Scope.REQUEST)
    def get_movie_service(
        self,
        uow: UnitOfWork,
        cache: CacheInterface,
        event_bus: EventBus,
    ) -> MovieService:
        """Provide movie service."""
        return MovieService(uow, cache, event_bus)

    @provide(scope=Scope.REQUEST)
    def get_user_service(
        self,
        uow: UnitOfWork,
        event_bus: EventBus,
    ) -> UserService:
        """Provide user service."""
        return UserService(uow, event_bus)

    @provide(scope=Scope.REQUEST)
    def get_rating_service(
        self,
        uow: UnitOfWork,
        cache: CacheInterface,
        event_bus: EventBus,
    ) -> RatingService:
        """Provide rating service."""
        return RatingService(uow, cache, event_bus)

    @provide(scope=Scope.REQUEST)
    def get_series_service(
        self,
        uow: UnitOfWork,
    ) -> SeriesService:
        """Provide series service."""
        return SeriesService(uow)

    @provide(scope=Scope.REQUEST)
    def get_favorite_service(
        self,
        uow: UnitOfWork,
    ) -> FavoriteService:
        """Provide favorite service."""
        return FavoriteService(uow)

    @provide(scope=Scope.REQUEST)
    def get_recommendation_service(
        self,
        uow: UnitOfWork,
        cache: CacheInterface,
    ) -> RecommendationService:
        """Provide recommendation service."""
        return RecommendationService(uow, cache)
