"""Download repository implementation."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.infrastructure.database.models.download import DownloadModel
from src.infrastructure.database.repositories.base import BaseRepository


class DownloadRepository(BaseRepository[DownloadModel]):
    """Repository for download tracking."""

    model = DownloadModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_download(
        self,
        user_id: UUID,
        movie_id: UUID,
        movie_code: int,
        source: str = "code",
    ) -> DownloadModel:
        """Create a download record."""
        download = DownloadModel(
            user_id=user_id,
            movie_id=movie_id,
            movie_code=movie_code,
            source=source,
        )
        return await self.create(download)

    async def get_total_count(self) -> int:
        """Get total downloads count."""
        query = select(func.count()).select_from(DownloadModel)
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_count_by_period(self, days: int) -> int:
        """Get downloads in last N days."""
        since = datetime.now(UTC) - timedelta(days=days)
        query = (
            select(func.count())
            .select_from(DownloadModel)
            .where(DownloadModel.downloaded_at >= since)
        )
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_today_count(self) -> int:
        """Get today's download count."""
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        query = (
            select(func.count())
            .select_from(DownloadModel)
            .where(DownloadModel.downloaded_at >= today)
        )
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_top_movies(
        self,
        limit: int = 5,
        days: int | None = None,
    ) -> Sequence[tuple[int, int]]:
        """Get top movies by download count. Returns [(movie_code, count), ...]."""
        query = (
            select(
                DownloadModel.movie_code,
                func.count(DownloadModel.id).label("count"),
            )
            .group_by(DownloadModel.movie_code)
            .order_by(func.count(DownloadModel.id).desc())
            .limit(limit)
        )

        if days:
            since = datetime.now(UTC) - timedelta(days=days)
            query = query.where(DownloadModel.downloaded_at >= since)

        result = await self._session.execute(query)
        return [(row[0], row[1]) for row in result.all()]

    async def get_user_downloads(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> Sequence[DownloadModel]:
        """Get user's recent downloads."""
        query = (
            select(DownloadModel)
            .where(DownloadModel.user_id == user_id)
            .order_by(DownloadModel.downloaded_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        return result.scalars().all()
