"""User Series Progress repository implementation."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import UserSeriesProgress
from src.infrastructure.database.models import UserSeriesProgressModel


class SeriesProgressRepository:
    """User Series Progress repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, progress_id: UUID) -> UserSeriesProgress | None:
        """Get progress by ID."""
        result = await self._session.execute(
            select(UserSeriesProgressModel)
            .where(UserSeriesProgressModel.id == progress_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_and_series(
        self, user_id: UUID, series_id: UUID
    ) -> UserSeriesProgress | None:
        """Get progress for specific user and series."""
        result = await self._session.execute(
            select(UserSeriesProgressModel)
            .where(UserSeriesProgressModel.user_id == user_id)
            .where(UserSeriesProgressModel.series_id == series_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user(self, user_id: UUID) -> list[UserSeriesProgress]:
        """Get all progress records for user."""
        result = await self._session.execute(
            select(UserSeriesProgressModel)
            .where(UserSeriesProgressModel.user_id == user_id)
            .order_by(UserSeriesProgressModel.updated_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, progress: UserSeriesProgress) -> UserSeriesProgress:
        """Create new progress record."""
        model = UserSeriesProgressModel(
            id=progress.id,
            user_id=progress.user_id,
            series_id=progress.series_id,
            last_watched_part=progress.last_watched_part,
            completed_parts=progress.completed_parts,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, progress: UserSeriesProgress) -> UserSeriesProgress:
        """Update progress record."""
        result = await self._session.execute(
            select(UserSeriesProgressModel)
            .where(UserSeriesProgressModel.id == progress.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.last_watched_part = progress.last_watched_part
            model.completed_parts = progress.completed_parts
            await self._session.flush()
            return self._to_entity(model)
        return progress

    async def upsert(
        self,
        user_id: UUID,
        series_id: UUID,
        part_number: int,
    ) -> UserSeriesProgress:
        """Update or create progress record."""
        result = await self._session.execute(
            select(UserSeriesProgressModel)
            .where(UserSeriesProgressModel.user_id == user_id)
            .where(UserSeriesProgressModel.series_id == series_id)
        )
        model = result.scalar_one_or_none()

        if model:
            # Update existing
            if part_number not in model.completed_parts:
                model.completed_parts = model.completed_parts + [part_number]
            if part_number > model.last_watched_part:
                model.last_watched_part = part_number
            await self._session.flush()
            return self._to_entity(model)
        else:
            # Create new
            new_model = UserSeriesProgressModel(
                id=uuid4(),
                user_id=user_id,
                series_id=series_id,
                last_watched_part=part_number,
                completed_parts=[part_number],
            )
            self._session.add(new_model)
            await self._session.flush()
            return self._to_entity(new_model)

    async def delete(self, progress_id: UUID) -> bool:
        """Delete progress record."""
        result = await self._session.execute(
            select(UserSeriesProgressModel)
            .where(UserSeriesProgressModel.id == progress_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            return True
        return False

    def _to_entity(self, model: UserSeriesProgressModel) -> UserSeriesProgress:
        """Convert model to entity."""
        return UserSeriesProgress(
            id=model.id,
            user_id=model.user_id,
            series_id=model.series_id,
            last_watched_part=model.last_watched_part,
            completed_parts=list(model.completed_parts or []),
            updated_at=model.updated_at,
        )
