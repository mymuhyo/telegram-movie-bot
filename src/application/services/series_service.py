"""Series application service."""

from uuid import UUID

from src.application.dto import (
    MovieDTO,
    SeriesDTO,
    SeriesWithPartsDTO,
    UserSeriesProgressDTO,
)
from src.application.interfaces import UnitOfWork
from src.core.exceptions import SeriesNotFoundError
from src.domain.entities import Movie, Series


class SeriesService:
    """Application service for series operations."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def get_series_with_parts(
        self,
        series_id: UUID,
    ) -> SeriesWithPartsDTO:
        """
        Get series with all its parts.

        Args:
            series_id: Series ID

        Returns:
            Series with parts DTO

        Raises:
            SeriesNotFoundError: If series not found
        """
        async with self._uow:
            series = await self._uow.series.get_by_id(series_id)
            if not series:
                raise SeriesNotFoundError(series_id)

            movies = await self._uow.movies.get_by_series(series_id)
            # Sort by part number
            movies.sort(key=lambda m: m.part_number or 0)

            return SeriesWithPartsDTO(
                series=self._series_to_dto(series, len(movies)),
                parts=[self._movie_to_dto(m) for m in movies],
            )

    async def get_user_progress(
        self,
        user_id: UUID,
        series_id: UUID,
    ) -> UserSeriesProgressDTO | None:
        """Get user's progress in a series."""
        async with self._uow:
            series = await self._uow.series.get_by_id(series_id)
            if not series:
                return None

            progress = await self._uow.series_progress.get_by_user_and_series(
                user_id, series_id
            )

            if not progress:
                return UserSeriesProgressDTO(
                    user_id=user_id,
                    series_id=series_id,
                    series_name=series.name,
                    total_parts=series.total_parts,
                    last_watched_part=0,
                    completed_parts=[],
                )

            return UserSeriesProgressDTO(
                user_id=user_id,
                series_id=series_id,
                series_name=series.name,
                total_parts=series.total_parts,
                last_watched_part=progress.last_watched_part,
                completed_parts=progress.completed_parts,
            )

    async def mark_part_watched(
        self,
        user_id: UUID,
        series_id: UUID,
        part_number: int,
    ) -> UserSeriesProgressDTO:
        """
        Mark a part as watched.

        Args:
            user_id: User ID
            series_id: Series ID
            part_number: Part number to mark

        Returns:
            Updated progress
        """
        async with self._uow:
            series = await self._uow.series.get_by_id(series_id)
            if not series:
                raise SeriesNotFoundError(series_id)

            progress = await self._uow.series_progress.upsert(
                user_id=user_id,
                series_id=series_id,
                part_number=part_number,
            )
            await self._uow.commit()

            return UserSeriesProgressDTO(
                user_id=user_id,
                series_id=series_id,
                series_name=series.name,
                total_parts=series.total_parts,
                last_watched_part=progress.last_watched_part,
                completed_parts=progress.completed_parts,
            )

    async def get_next_part(
        self,
        series_id: UUID,
        current_part: int,
    ) -> MovieDTO | None:
        """Get next part in series."""
        async with self._uow:
            movies = await self._uow.movies.get_by_series(series_id)
            for movie in movies:
                if movie.part_number == current_part + 1:
                    return self._movie_to_dto(movie)
            return None

    async def get_previous_part(
        self,
        series_id: UUID,
        current_part: int,
    ) -> MovieDTO | None:
        """Get previous part in series."""
        async with self._uow:
            movies = await self._uow.movies.get_by_series(series_id)
            for movie in movies:
                if movie.part_number == current_part - 1:
                    return self._movie_to_dto(movie)
            return None

    async def get_all_series(self) -> list[SeriesDTO]:
        """Get all series."""
        async with self._uow:
            series_list = await self._uow.series.get_all()
            result = []
            for series in series_list:
                movies = await self._uow.movies.get_by_series(series.id)
                result.append(self._series_to_dto(series, len(movies)))
            return result

    async def get_user_in_progress_series(
        self,
        user_id: UUID,
    ) -> list[UserSeriesProgressDTO]:
        """Get series user is currently watching."""
        async with self._uow:
            progress_list = await self._uow.series_progress.get_by_user(user_id)
            result = []

            for progress in progress_list:
                series = await self._uow.series.get_by_id(progress.series_id)
                if series and progress.watched_count < series.total_parts:
                    result.append(
                        UserSeriesProgressDTO(
                            user_id=user_id,
                            series_id=series.id,
                            series_name=series.name,
                            total_parts=series.total_parts,
                            last_watched_part=progress.last_watched_part,
                            completed_parts=progress.completed_parts,
                        )
                    )

            return result

    def _series_to_dto(self, series: Series, available_parts: int) -> SeriesDTO:
        """Convert series entity to DTO."""
        return SeriesDTO(
            id=series.id,
            name=series.name,
            description=series.description,
            total_parts=series.total_parts,
            available_parts=available_parts,
        )

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
