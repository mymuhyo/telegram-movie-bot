"""Favorite application service."""

from uuid import UUID

from src.application.dto import MovieDTO, PaginatedResult
from src.application.interfaces import UnitOfWork
from src.core.exceptions import MovieNotFoundError
from src.domain.entities import Movie


class FavoriteService:
    """Application service for favorites/bookmarks."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def add_to_favorites(
        self,
        user_id: UUID,
        movie_id: UUID,
    ) -> bool:
        """
        Add movie to favorites.

        Args:
            user_id: User ID
            movie_id: Movie ID

        Returns:
            True if added, False if already exists

        Raises:
            MovieNotFoundError: If movie not found
        """
        async with self._uow:
            # Verify movie exists
            movie = await self._uow.movies.get_by_id(movie_id)
            if not movie:
                raise MovieNotFoundError(movie_id)

            # Check if already favorite
            if await self._uow.favorites.exists(user_id, movie_id):
                return False

            # Add favorite
            from uuid import uuid4
            from src.domain.entities import Favorite

            favorite = Favorite(
                id=uuid4(),
                user_id=user_id,
                movie_id=movie_id,
            )
            await self._uow.favorites.create(favorite)
            await self._uow.commit()
            return True

    async def remove_from_favorites(
        self,
        user_id: UUID,
        movie_id: UUID,
    ) -> bool:
        """
        Remove movie from favorites.

        Args:
            user_id: User ID
            movie_id: Movie ID

        Returns:
            True if removed, False if not found
        """
        async with self._uow:
            removed = await self._uow.favorites.remove(user_id, movie_id)
            if removed:
                await self._uow.commit()
            return removed

    async def toggle_favorite(
        self,
        user_id: UUID,
        movie_id: UUID,
    ) -> bool:
        """
        Toggle favorite status.

        Args:
            user_id: User ID
            movie_id: Movie ID

        Returns:
            True if now favorite, False if removed
        """
        async with self._uow:
            if await self._uow.favorites.exists(user_id, movie_id):
                await self._uow.favorites.remove(user_id, movie_id)
                await self._uow.commit()
                return False
            else:
                movie = await self._uow.movies.get_by_id(movie_id)
                if not movie:
                    raise MovieNotFoundError(movie_id)

                from uuid import uuid4
                from src.domain.entities import Favorite

                favorite = Favorite(
                    id=uuid4(),
                    user_id=user_id,
                    movie_id=movie_id,
                )
                await self._uow.favorites.create(favorite)
                await self._uow.commit()
                return True

    async def is_favorite(
        self,
        user_id: UUID,
        movie_id: UUID,
    ) -> bool:
        """Check if movie is in favorites."""
        async with self._uow:
            return await self._uow.favorites.exists(user_id, movie_id)

    async def get_favorites(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 10,
    ) -> PaginatedResult[MovieDTO]:
        """
        Get user's favorite movies.

        Args:
            user_id: User ID
            page: Page number
            per_page: Items per page

        Returns:
            Paginated result of movies
        """
        async with self._uow:
            total = await self._uow.favorites.count_by_user(user_id)
            offset = (page - 1) * per_page

            favorites = await self._uow.favorites.get_by_user(
                user_id, limit=per_page, offset=offset
            )

            movies: list[MovieDTO] = []
            for fav in favorites:
                movie = await self._uow.movies.get_by_id(fav.movie_id)
                if movie:
                    movies.append(self._movie_to_dto(movie))

            return PaginatedResult(
                items=movies,
                total=total,
                page=page,
                per_page=per_page,
            )

    async def get_favorites_count(self, user_id: UUID) -> int:
        """Get count of user's favorites."""
        async with self._uow:
            return await self._uow.favorites.count_by_user(user_id)

    def _movie_to_dto(self, movie: Movie) -> MovieDTO:
        """Convert movie entity to DTO."""
        return MovieDTO(
            id=movie.id,
            code=movie.code,
            title=movie.title,
            file_id=movie.file_id,
            quality=movie.quality,
            year=movie.year,
            duration_minutes=movie.duration_minutes,
            description=movie.description,
            poster_file_id=movie.poster_file_id,
            series_id=movie.series_id,
            part_number=movie.part_number,
            average_rating=movie.average_rating,
            rating_count=movie.rating_count,
            download_count=movie.download_count,
        )
