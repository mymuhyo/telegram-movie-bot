"""Series repository implementation."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.database.models.series import SeriesModel
from src.infrastructure.database.repositories.base import SoftDeleteRepository


class SeriesRepository(SoftDeleteRepository[SeriesModel]):
    """Repository for series operations."""

    model = SeriesModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_name(self, name: str) -> SeriesModel | None:
        """Get series by name."""
        query = (
            select(SeriesModel)
            .where(SeriesModel.name == name)
            .where(SeriesModel.deleted_at.is_(None))
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_with_movies(self, limit: int = 20) -> Sequence[SeriesModel]:
        """Get all series with their movies."""
        query = (
            select(SeriesModel)
            .where(SeriesModel.deleted_at.is_(None))
            .options(selectinload(SeriesModel.movies))
            .limit(limit)
        )
        result = await self._session.execute(query)
        return result.scalars().all()
