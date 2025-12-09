"""User repository implementation."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.infrastructure.database.models.user import UserModel
from src.infrastructure.database.repositories.base import SoftDeleteRepository


class UserRepository(SoftDeleteRepository[UserModel]):
    """Repository for user operations."""

    model = UserModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_telegram_id(self, telegram_id: int) -> UserModel | None:
        """Get user by Telegram ID."""
        query = (
            select(UserModel)
            .where(UserModel.telegram_id == telegram_id)
            .where(UserModel.deleted_at.is_(None))
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
        full_name: str | None = None,
    ) -> tuple[UserModel, bool]:
        """Get existing user or create new one. Returns (user, created)."""
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            # Update user info if changed
            if username != user.username or full_name != user.full_name:
                user.username = username
                user.full_name = full_name
                user.last_active_at = datetime.now(UTC)
                await self._session.flush()
            return user, False

        # Create new user
        user = UserModel(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            last_active_at=datetime.now(UTC),
        )
        await self.create(user)
        return user, True

    async def update_activity(self, user_id: UUID) -> None:
        """Update user's last active timestamp."""
        stmt = update(UserModel).where(UserModel.id == user_id).values(last_active_at=func.now())
        await self._session.execute(stmt)

    async def increment_downloads(self, user_id: UUID) -> None:
        """Increment user's download count."""
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(total_downloads=UserModel.total_downloads + 1)
        )
        await self._session.execute(stmt)

    async def ban_user(
        self,
        user_id: UUID,
        reason: str | None = None,
        banned_by: UUID | None = None,
    ) -> bool:
        """Ban a user."""
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                is_banned=True,
                ban_reason=reason,
                banned_at=func.now(),
                banned_by=banned_by,
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0  # type: ignore

    async def unban_user(self, user_id: UUID) -> bool:
        """Unban a user."""
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                is_banned=False,
                ban_reason=None,
                banned_at=None,
                banned_by=None,
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0  # type: ignore

    async def get_all_active_ids(self) -> Sequence[int]:
        """Get all non-banned user Telegram IDs for broadcasting."""
        query = (
            select(UserModel.telegram_id)
            .where(UserModel.deleted_at.is_(None))
            .where(UserModel.is_banned.is_(False))
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_total_count(self) -> int:
        """Get total users count."""
        query = select(func.count()).select_from(UserModel).where(UserModel.deleted_at.is_(None))
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_count_by_period(self, days: int) -> int:
        """Get users joined in last N days."""
        since = datetime.now(UTC) - timedelta(days=days)
        query = (
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.deleted_at.is_(None))
            .where(UserModel.joined_at >= since)
        )
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def get_active_count(self, days: int = 7) -> int:
        """Get count of users active in last N days."""
        since = datetime.now(UTC) - timedelta(days=days)
        query = (
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.deleted_at.is_(None))
            .where(UserModel.last_active_at >= since)
        )
        result = await self._session.execute(query)
        return result.scalar() or 0
