"""Base repository with common CRUD operations."""
from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.infrastructure.database.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""

    model: Type[T]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Get entity by ID."""
        return await self._session.get(self.model, entity_id)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[T]:
        """Get all entities with pagination."""
        query = select(self.model).offset(offset).limit(limit)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def count(self) -> int:
        """Count all entities."""
        query = select(func.count()).select_from(self.model)
        result = await self._session.execute(query)
        return result.scalar() or 0

    async def create(self, entity: T) -> T:
        """Create a new entity."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        await self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """Hard delete an entity."""
        await self._session.delete(entity)
        await self._session.flush()

    async def bulk_create(self, entities: list[T]) -> list[T]:
        """Create multiple entities."""
        self._session.add_all(entities)
        await self._session.flush()
        for entity in entities:
            await self._session.refresh(entity)
        return entities


class SoftDeleteRepository(BaseRepository[T]):
    """Repository with soft delete support."""

    async def soft_delete(self, entity_id: UUID) -> bool:
        """Soft delete an entity."""
        stmt = (
            update(self.model)
            .where(self.model.id == entity_id)  # type: ignore
            .values(deleted_at=func.now())
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0  # type: ignore

    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Get entity by ID (excluding soft deleted)."""
        query = (
            select(self.model)
            .where(self.model.id == entity_id)  # type: ignore
            .where(self.model.deleted_at.is_(None))  # type: ignore
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> Sequence[T]:
        """Get all entities with pagination."""
        query = select(self.model).offset(offset).limit(limit)
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))  # type: ignore
        result = await self._session.execute(query)
        return result.scalars().all()

    async def count(self, include_deleted: bool = False) -> int:
        """Count entities."""
        query = select(func.count()).select_from(self.model)
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))  # type: ignore
        result = await self._session.execute(query)
        return result.scalar() or 0
