"""User application service."""

from uuid import UUID

from src.application.dto import UserDTO
from src.application.interfaces import EventBus, UnitOfWork
from src.domain.entities import User
from src.domain.events import UserBanned, UserJoined, UserUnbanned


class UserService:
    """Application service for user operations."""

    def __init__(
        self,
        uow: UnitOfWork,
        event_bus: EventBus,
    ) -> None:
        self._uow = uow
        self._event_bus = event_bus

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
        full_name: str | None = None,
    ) -> tuple[UserDTO, bool]:
        """
        Get or create user.

        Args:
            telegram_id: Telegram user ID
            username: Optional username
            full_name: Optional full name

        Returns:
            Tuple of (user DTO, was_created)
        """
        async with self._uow:
            user, created = await self._uow.users.get_or_create(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
            )
            await self._uow.commit()

            if created:
                await self._event_bus.publish(
                    UserJoined(user_id=user.id, telegram_id=telegram_id)
                )

            dto = self._to_dto(user)
            return dto, created

    async def get_by_telegram_id(self, telegram_id: int) -> UserDTO | None:
        """Get user by Telegram ID."""
        async with self._uow:
            user = await self._uow.users.get_by_telegram_id(telegram_id)
            return self._to_dto(user) if user else None

    async def get_by_id(self, user_id: UUID) -> UserDTO | None:
        """Get user by internal ID."""
        async with self._uow:
            user = await self._uow.users.get_by_id(user_id)
            return self._to_dto(user) if user else None

    async def ban_user(
        self,
        user_id: UUID,
        reason: str | None = None,
        banned_by: int = 0,
    ) -> bool:
        """
        Ban a user.

        Args:
            user_id: User ID to ban
            reason: Optional ban reason
            banned_by: Admin's Telegram ID

        Returns:
            True if banned, False if already banned or not found
        """
        async with self._uow:
            user = await self._uow.users.get_by_id(user_id)
            if not user or user.is_banned:
                return False

            success = await self._uow.users.ban(user_id, reason)
            if success:
                await self._uow.commit()
                await self._event_bus.publish(
                    UserBanned(
                        user_id=user_id,
                        telegram_id=user.telegram_id,
                        reason=reason,
                        banned_by=banned_by,
                    )
                )
            return success

    async def unban_user(
        self,
        user_id: UUID,
        unbanned_by: int = 0,
    ) -> bool:
        """
        Unban a user.

        Args:
            user_id: User ID to unban
            unbanned_by: Admin's Telegram ID

        Returns:
            True if unbanned, False if not banned or not found
        """
        async with self._uow:
            user = await self._uow.users.get_by_id(user_id)
            if not user or not user.is_banned:
                return False

            success = await self._uow.users.unban(user_id)
            if success:
                await self._uow.commit()
                await self._event_bus.publish(
                    UserUnbanned(
                        user_id=user_id,
                        telegram_id=user.telegram_id,
                        unbanned_by=unbanned_by,
                    )
                )
            return success

    async def is_banned(self, telegram_id: int) -> bool:
        """Check if user is banned."""
        async with self._uow:
            user = await self._uow.users.get_by_telegram_id(telegram_id)
            return user.is_banned if user else False

    async def get_stats(self) -> dict:
        """Get user statistics."""
        async with self._uow:
            total = await self._uow.users.count()
            active_7d = await self._uow.users.count_active(7)
            active_30d = await self._uow.users.count_active(30)

            return {
                "total": total,
                "active_7d": active_7d,
                "active_30d": active_30d,
            }

    async def get_all_telegram_ids(self) -> list[int]:
        """Get all user Telegram IDs for broadcasting."""
        async with self._uow:
            return await self._uow.users.get_all_ids()

    async def get_active_telegram_ids(self, days: int = 30) -> list[int]:
        """Get active user Telegram IDs."""
        async with self._uow:
            return await self._uow.users.get_active_ids(days)

    def _to_dto(self, user: User) -> UserDTO:
        """Convert entity to DTO."""
        return UserDTO(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            full_name=user.full_name,
            is_banned=user.is_banned,
            ban_reason=user.ban_reason,
            total_downloads=user.total_downloads,
            joined_at=user.joined_at,
            last_active_at=user.last_active_at,
        )
