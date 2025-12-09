"""Rating repository implementation."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Rating
from src.infrastructure.database.models import RatingModel


class RatingRepository:
    """Rating repository implementation."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, rating_id: UUID) -> Rating | None:
        """Get rating by ID."""
        result = await self._session.execute(
            select(RatingModel).where(RatingModel.id == rating_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_and_movie(
        self, user_id: UUID, movie_id: UUID
    ) -> Rating | None:
        """Get user's rating for a movie."""
        result = await self._session.execute(
            select(RatingModel)
            .where(RatingModel.user_id == user_id)
            .where(RatingModel.movie_id == movie_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_movie(self, movie_id: UUID) -> list[Rating]:
        """Get all ratings for a movie."""
        result = await self._session.execute(
            select(RatingModel)
            .where(RatingModel.movie_id == movie_id)
            .order_by(RatingModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_user(self, user_id: UUID, limit: int = 50) -> list[Rating]:
        """Get user's ratings."""
        result = await self._session.execute(
            select(RatingModel)
            .where(RatingModel.user_id == user_id)
            .order_by(RatingModel.created_at.desc())
            .limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, rating: Rating) -> Rating:
        """Create new rating."""
        model = RatingModel(
            id=rating.id,
            user_id=rating.user_id,
            movie_id=rating.movie_id,
            score=rating.score,
            review=rating.review,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def update(self, rating: Rating) -> Rating:
        """Update rating."""
        result = await self._session.execute(
            select(RatingModel).where(RatingModel.id == rating.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.score = rating.score
            model.review = rating.review
            await self._session.flush()
            return self._to_entity(model)
        return rating

    async def upsert(
        self, user_id: UUID, movie_id: UUID, score: int
    ) -> tuple[Rating, int | None]:
        """Create or update rating. Returns (rating, old_score or None)."""
        result = await self._session.execute(
            select(RatingModel)
            .where(RatingModel.user_id == user_id)
            .where(RatingModel.movie_id == movie_id)
        )
        model = result.scalar_one_or_none()

        if model:
            old_score = model.score
            model.score = score
            await self._session.flush()
            return self._to_entity(model), old_score
        else:
            new_model = RatingModel(
                id=uuid4(),
                user_id=user_id,
                movie_id=movie_id,
                score=score,
            )
            self._session.add(new_model)
            await self._session.flush()
            return self._to_entity(new_model), None

    async def delete(self, rating_id: UUID) -> bool:
        """Delete rating."""
        result = await self._session.execute(
            select(RatingModel).where(RatingModel.id == rating_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            return True
        return False

    def _to_entity(self, model: RatingModel) -> Rating:
        """Convert model to entity."""
        return Rating(
            id=model.id,
            user_id=model.user_id,
            movie_id=model.movie_id,
            score=model.score,
            review=model.review,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
