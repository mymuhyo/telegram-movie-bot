"""Favorite repository implementation."""

from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Favorite
from src.infrastructure.database.models import FavoriteModel


class FavoriteRepository:
    """Favorite repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, favorite_id: UUID) -> Favorite | None:
        """Get favorite by ID."""
        result = await self._session.execute(
            select(FavoriteModel).where(FavoriteModel.id == favorite_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_and_movie(
        self, user_id: UUID, movie_id: UUID
    ) -> Favorite | None:
        """Get specific favorite."""
        result = await self._session.execute(
            select(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
            .where(FavoriteModel.movie_id == movie_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Favorite]:
        """Get user's favorites."""
        result = await self._session.execute(
            select(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
            .order_by(FavoriteModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_by_user(self, user_id: UUID) -> int:
        """Count user's favorites."""
        result = await self._session.execute(
            select(func.count())
            .select_from(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
        )
        return result.scalar() or 0

    async def exists(self, user_id: UUID, movie_id: UUID) -> bool:
        """Check if favorite exists."""
        result = await self._session.execute(
            select(func.count())
            .select_from(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
            .where(FavoriteModel.movie_id == movie_id)
        )
        return (result.scalar() or 0) > 0

    async def create(self, favorite: Favorite) -> Favorite:
        """Create new favorite."""
        model = FavoriteModel(
            id=favorite.id,
            user_id=favorite.user_id,
            movie_id=favorite.movie_id,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def remove(self, user_id: UUID, movie_id: UUID) -> bool:
        """Remove favorite."""
        result = await self._session.execute(
            delete(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
            .where(FavoriteModel.movie_id == movie_id)
        )
        return result.rowcount > 0

    async def delete(self, favorite_id: UUID) -> bool:
        """Delete favorite by ID."""
        result = await self._session.execute(
            delete(FavoriteModel).where(FavoriteModel.id == favorite_id)
        )
        return result.rowcount > 0

    async def update(self, favorite: Favorite) -> Favorite:
        """Update favorite (not typically used)."""
        return favorite

    def _to_entity(self, model: FavoriteModel) -> Favorite:
        """Convert model to entity."""
        return Favorite(
            id=model.id,
            user_id=model.user_id,
            movie_id=model.movie_id,
            created_at=model.created_at,
        )
