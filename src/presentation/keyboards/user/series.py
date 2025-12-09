"""Series navigation keyboard builder."""

from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.dto import MovieDTO, SeriesWithPartsDTO, UserSeriesProgressDTO


class SeriesKeyboard:
    """Series keyboard builder for navigation and parts list."""

    @staticmethod
    def get_series_parts_keyboard(
        series_data: SeriesWithPartsDTO,
        progress: UserSeriesProgressDTO | None = None,
        page: int = 0,
        per_page: int = 8,
    ) -> InlineKeyboardMarkup:
        """
        Get keyboard with series parts list.

        Shows parts with watched status indicators.

        Args:
            series_data: Series with parts data
            progress: User's watch progress
            page: Current page (0-indexed)
            per_page: Items per page

        Returns:
            Inline keyboard with parts list
        """
        buttons = []
        parts = series_data.parts
        total_parts = len(parts)

        # Calculate pagination
        start = page * per_page
        end = min(start + per_page, total_parts)
        page_parts = parts[start:end]

        # Build parts grid (2 parts per row)
        for i in range(0, len(page_parts), 2):
            row = []
            for part in page_parts[i : i + 2]:
                is_watched = (
                    progress.is_watched(part.part_number)
                    if progress and part.part_number
                    else False
                )

                # Visual indicator for watched status
                watched_mark = "✅ " if is_watched else ""
                text = f"{watched_mark}{part.part_number}-qism"

                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=f"movie:{part.code}",
                    )
                )
            buttons.append(row)

        # Pagination row
        total_pages = (total_parts + per_page - 1) // per_page
        if total_pages > 1:
            nav_row = []

            if page > 0:
                nav_row.append(
                    InlineKeyboardButton(
                        text="◀️",
                        callback_data=f"series:page:{series_data.series.id}:{page - 1}",
                    )
                )

            nav_row.append(
                InlineKeyboardButton(
                    text=f"{page + 1}/{total_pages}",
                    callback_data="noop",
                )
            )

            if page < total_pages - 1:
                nav_row.append(
                    InlineKeyboardButton(
                        text="▶️",
                        callback_data=f"series:page:{series_data.series.id}:{page + 1}",
                    )
                )

            buttons.append(nav_row)

        # Progress bar and continue button
        if progress:
            watched = progress.watched_count
            total = progress.total_parts
            percent = int(progress.progress_percentage)

            # Progress indicator row
            buttons.append([
                InlineKeyboardButton(
                    text=f"📊 Ko'rilgan: {watched}/{total} ({percent}%)",
                    callback_data="noop",
                )
            ])

            # Continue watching button
            if progress.next_unwatched and progress.next_unwatched <= len(parts):
                next_part = series_data.get_part(progress.next_unwatched)
                if next_part:
                    buttons.append([
                        InlineKeyboardButton(
                            text=f"▶️ Davom etish ({progress.next_unwatched}-qism)",
                            callback_data=f"movie:{next_part.code}",
                        )
                    ])

        # Back button
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="series:list",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_series_list_keyboard(
        series_list: list[tuple[SeriesWithPartsDTO, UserSeriesProgressDTO | None]],
        page: int = 0,
        per_page: int = 5,
    ) -> InlineKeyboardMarkup:
        """
        Get keyboard with list of all series.

        Args:
            series_list: List of (series_data, user_progress) tuples
            page: Current page
            per_page: Items per page

        Returns:
            Inline keyboard with series list
        """
        buttons = []
        total = len(series_list)

        # Calculate pagination
        start = page * per_page
        end = min(start + per_page, total)
        page_items = series_list[start:end]

        # Build series list
        for series_data, progress in page_items:
            series = series_data.series

            # Build status text
            if progress and progress.watched_count > 0:
                if progress.watched_count >= progress.total_parts:
                    status = "✅"  # Completed
                else:
                    status = f"▶️ {progress.watched_count}/{progress.total_parts}"
            else:
                status = f"📺 {series.available_parts} qism"

            buttons.append([
                InlineKeyboardButton(
                    text=f"{series.name} {status}",
                    callback_data=f"series:view:{series.id}",
                )
            ])

        # Pagination row
        total_pages = (total + per_page - 1) // per_page
        if total_pages > 1:
            nav_row = []

            if page > 0:
                nav_row.append(
                    InlineKeyboardButton(
                        text="◀️",
                        callback_data=f"series:list:page:{page - 1}",
                    )
                )

            nav_row.append(
                InlineKeyboardButton(
                    text=f"{page + 1}/{total_pages}",
                    callback_data="noop",
                )
            )

            if page < total_pages - 1:
                nav_row.append(
                    InlineKeyboardButton(
                        text="▶️",
                        callback_data=f"series:list:page:{page + 1}",
                    )
                )

            buttons.append(nav_row)

        # Close button
        buttons.append([
            InlineKeyboardButton(
                text="❌ Yopish",
                callback_data="close",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_in_progress_keyboard(
        progress_list: list[tuple[SeriesWithPartsDTO, UserSeriesProgressDTO]],
    ) -> InlineKeyboardMarkup:
        """
        Get keyboard showing series in progress (continue watching).

        Args:
            progress_list: List of in-progress series with their progress

        Returns:
            Inline keyboard with continue watching options
        """
        buttons = []

        for series_data, progress in progress_list[:5]:  # Max 5 items
            next_part_num = progress.next_unwatched
            next_part = series_data.get_part(next_part_num) if next_part_num else None

            percent = int(progress.progress_percentage)
            text = f"▶️ {progress.series_name} ({percent}%)"

            if next_part:
                buttons.append([
                    InlineKeyboardButton(
                        text=text,
                        callback_data=f"movie:{next_part.code}",
                    ),
                    InlineKeyboardButton(
                        text="📋",
                        callback_data=f"series:view:{progress.series_id}",
                    )
                ])
            else:
                buttons.append([
                    InlineKeyboardButton(
                        text=text,
                        callback_data=f"series:view:{progress.series_id}",
                    )
                ])

        if not buttons:
            buttons.append([
                InlineKeyboardButton(
                    text="📭 Hozircha bo'sh",
                    callback_data="noop",
                )
            ])

        # View all series button
        buttons.append([
            InlineKeyboardButton(
                text="📺 Barcha seriallar",
                callback_data="series:list",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_part_navigation_keyboard(
        movie: MovieDTO,
        series_data: SeriesWithPartsDTO,
        is_favorite: bool = False,
    ) -> InlineKeyboardMarkup:
        """
        Get navigation keyboard for a series part.

        Includes prev/next navigation, all parts, favorite, and share.

        Args:
            movie: Current movie/part DTO
            series_data: Full series data
            is_favorite: Whether this movie is in favorites

        Returns:
            Navigation keyboard
        """
        buttons = []
        current_part = movie.part_number or 1

        # Row 1: Navigation
        nav_row = []
        prev_part = series_data.get_prev_part(current_part)
        next_part = series_data.get_next_part(current_part)

        if prev_part:
            nav_row.append(
                InlineKeyboardButton(
                    text="⬅️ Oldingi",
                    callback_data=f"movie:{prev_part.code}",
                )
            )

        nav_row.append(
            InlineKeyboardButton(
                text=f"{current_part}/{series_data.series.total_parts}",
                callback_data="noop",
            )
        )

        if next_part:
            nav_row.append(
                InlineKeyboardButton(
                    text="Keyingi ➡️",
                    callback_data=f"movie:{next_part.code}",
                )
            )

        buttons.append(nav_row)

        # Row 2: All parts
        buttons.append([
            InlineKeyboardButton(
                text="📺 Barcha qismlar",
                callback_data=f"series:view:{movie.series_id}",
            )
        ])

        # Row 3: Rate button
        buttons.append([
            InlineKeyboardButton(
                text="⭐ Baholash",
                callback_data=f"rate:show:{movie.code}",
            )
        ])

        # Row 4: Favorite & Share
        action_row = []

        if is_favorite:
            action_row.append(
                InlineKeyboardButton(
                    text="💔 Olib tashlash",
                    callback_data=f"fav:remove:{movie.code}",
                )
            )
        else:
            action_row.append(
                InlineKeyboardButton(
                    text="❤️ Sevimli",
                    callback_data=f"fav:add:{movie.code}",
                )
            )

        action_row.append(
            InlineKeyboardButton(
                text="📤 Ulashish",
                switch_inline_query=str(movie.code),
            )
        )
        buttons.append(action_row)

        return InlineKeyboardMarkup(inline_keyboard=buttons)
