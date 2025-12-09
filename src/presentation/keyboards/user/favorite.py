"""Favorite keyboard builder."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.dto import MovieDTO, PaginatedResult


class FavoriteKeyboard:
    """Favorite keyboard builder."""

    @staticmethod
    def get_favorites_list_keyboard(
        result: PaginatedResult[MovieDTO],
    ) -> InlineKeyboardMarkup:
        """
        Get favorites list keyboard with movie buttons and pagination.

        Args:
            result: Paginated favorites result

        Returns:
            Inline keyboard
        """
        buttons = []

        # Movie buttons (code to get movie)
        for movie in result.items:
            title = movie.title[:25]
            if len(movie.title) > 25:
                title += "..."

            buttons.append([
                InlineKeyboardButton(
                    text=f"📥 {movie.code} — {title}",
                    callback_data=f"movie:{movie.code}",
                )
            ])

        # Pagination row
        if result.total_pages > 1:
            nav_row = []

            if result.has_prev:
                nav_row.append(
                    InlineKeyboardButton(
                        text="⬅️",
                        callback_data=f"fav:page:{result.page - 1}",
                    )
                )

            nav_row.append(
                InlineKeyboardButton(
                    text=f"{result.page}/{result.total_pages}",
                    callback_data="noop",
                )
            )

            if result.has_next:
                nav_row.append(
                    InlineKeyboardButton(
                        text="➡️",
                        callback_data=f"fav:page:{result.page + 1}",
                    )
                )

            buttons.append(nav_row)

        # Refresh button
        buttons.append([
            InlineKeyboardButton(
                text="🔄 Yangilash",
                callback_data="fav:page:1",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_favorite_toggle_button(
        movie_code: int,
        is_favorite: bool,
    ) -> InlineKeyboardButton:
        """
        Get single favorite toggle button.

        Args:
            movie_code: Movie code
            is_favorite: Current favorite status

        Returns:
            Toggle button
        """
        if is_favorite:
            return InlineKeyboardButton(
                text="💔 Olib tashlash",
                callback_data=f"fav:remove:{movie_code}",
            )
        else:
            return InlineKeyboardButton(
                text="❤️ Sevimli",
                callback_data=f"fav:add:{movie_code}",
            )
