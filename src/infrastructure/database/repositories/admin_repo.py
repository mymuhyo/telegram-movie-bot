"""Admin repository implementation."""

from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.core.constants import ROLE_ADMIN, ROLE_SUPER_ADMIN
from src.infrastructure.database.models.admin import AdminModel
from src.infrastructure.database.repositories.base import SoftDeleteRepository


class AdminRepository(SoftDeleteRepository[AdminModel]):
    """Repository for admin operations."""

    model = AdminModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_telegram_id(self, telegram_id: int) -> AdminModel | None:
        """Get admin by Telegram ID."""
        query = (
            select(AdminModel)
            .where(AdminModel.telegram_id == telegram_id)
            .where(AdminModel.deleted_at.is_(None))
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def is_admin(self, telegram_id: int) -> bool:
        """Check if user is an admin."""
        admin = await self.get_by_telegram_id(telegram_id)
        return admin is not None

    async def is_super_admin(self, telegram_id: int) -> bool:
        """Check if user is a super admin."""
        admin = await self.get_by_telegram_id(telegram_id)
        return admin is not None and admin.role == ROLE_SUPER_ADMIN

    async def create_admin(
        self,
        telegram_id: int,
        username: str | None = None,
        is_super: bool = False,
    ) -> AdminModel:
        """Create a new admin."""
        admin = AdminModel(
            telegram_id=telegram_id,
            username=username,
            role=ROLE_SUPER_ADMIN if is_super else ROLE_ADMIN,
        )
        return await self.create(admin)

    async def update_last_action(self, telegram_id: int) -> None:
        """Update admin's last action timestamp."""
        stmt = (
            update(AdminModel)
            .where(AdminModel.telegram_id == telegram_id)
            .values(last_action_at=func.now())
        )
        await self._session.execute(stmt)

    async def get_all_admins(self) -> Sequence[AdminModel]:
        """Get all admins (excluding deleted)."""
        query = (
            select(AdminModel)
            .where(AdminModel.deleted_at.is_(None))
            .order_by(AdminModel.role, AdminModel.created_at)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_removable_admins(self) -> Sequence[AdminModel]:
        """Get admins that can be removed (not super_admin)."""
        query = (
            select(AdminModel)
            .where(AdminModel.deleted_at.is_(None))
            .where(AdminModel.role != ROLE_SUPER_ADMIN)
            .order_by(AdminModel.created_at)
        )
        result = await self._session.execute(query)
        return result.scalars().all()
