"""Genre repository implementation."""

from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Genre
from src.infrastructure.database.models import GenreModel, MovieGenreModel


class GenreRepository:
    """Genre repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """Get genre by ID."""
        result = await self._session.execute(
            select(GenreModel).where(GenreModel.id == genre_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> Genre | None:
        """Get genre by slug."""
        result = await self._session.execute(
            select(GenreModel).where(GenreModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> list[Genre]:
        """Get all genres."""
        result = await self._session.execute(
            select(GenreModel).order_by(GenreModel.name_uz)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_movie(self, movie_id: UUID) -> list[Genre]:
        """Get genres for a movie."""
        result = await self._session.execute(
            select(GenreModel)
            .join(MovieGenreModel, MovieGenreModel.genre_id == GenreModel.id)
            .where(MovieGenreModel.movie_id == movie_id)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, genre: Genre) -> Genre:
        """Create new genre."""
        model = GenreModel(
            id=genre.id,
            name=genre.name,
            name_uz=genre.name_uz,
            slug=genre.slug,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, genre: Genre) -> Genre:
        """Update genre."""
        result = await self._session.execute(
            select(GenreModel).where(GenreModel.id == genre.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.name = genre.name
            model.name_uz = genre.name_uz
            model.slug = genre.slug
            await self._session.flush()
            return self._to_entity(model)
        return genre

    async def delete(self, genre_id: UUID) -> bool:
        """Delete genre."""
        result = await self._session.execute(
            delete(GenreModel).where(GenreModel.id == genre_id)
        )
        return result.rowcount > 0

    async def add_to_movie(self, movie_id: UUID, genre_id: UUID) -> None:
        """Add genre to movie."""
        model = MovieGenreModel(movie_id=movie_id, genre_id=genre_id)
        self._session.add(model)
        await self._session.flush()

    async def remove_from_movie(self, movie_id: UUID, genre_id: UUID) -> None:
        """Remove genre from movie."""
        await self._session.execute(
            delete(MovieGenreModel)
            .where(MovieGenreModel.movie_id == movie_id)
            .where(MovieGenreModel.genre_id == genre_id)
        )

    def _to_entity(self, model: GenreModel) -> Genre:
        """Convert model to entity."""
        return Genre(
            id=model.id,
            name=model.name,
            name_uz=model.name_uz,
            slug=model.slug,
            created_at=model.created_at,
        )
