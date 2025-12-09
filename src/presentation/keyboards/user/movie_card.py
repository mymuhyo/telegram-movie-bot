"""Movie card keyboard builder."""

from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.dto import MovieCardDTO


class MovieCardKeyboard:
    """Movie card keyboard builder with all actions."""

    @staticmethod
    def get_movie_card_keyboard(
        card: MovieCardDTO,
    ) -> InlineKeyboardMarkup:
        """
        Get full movie card keyboard with all actions.

        Args:
            card: Movie card DTO with user data

        Returns:
            Inline keyboard with rating, favorite, share, series buttons
        """
        buttons = []

        # Row 1: Rating stars (compact)
        rating_row = []
        for score in range(1, 6):
            if card.user_rating == score:
                text = f"[{score}]"
            else:
                text = str(score)

            rating_row.append(
                InlineKeyboardButton(
                    text=f"{text}⭐",
                    callback_data=f"rate:{card.movie.code}:{score}",
                )
            )
        buttons.append(rating_row)

        # Row 2: Favorite & Share
        action_row = []

        # Favorite toggle
        if card.is_favorite:
            action_row.append(
                InlineKeyboardButton(
                    text="💔 Olib tashlash",
                    callback_data=f"fav:remove:{card.movie.code}",
                )
            )
        else:
            action_row.append(
                InlineKeyboardButton(
                    text="❤️ Sevimli",
                    callback_data=f"fav:add:{card.movie.code}",
                )
            )

        # Share
        action_row.append(
            InlineKeyboardButton(
                text="📤 Ulashish",
                switch_inline_query=str(card.movie.code),
            )
        )
        buttons.append(action_row)

        # Row 3: Series navigation (if applicable)
        if card.movie.is_series:
            series_row = []

            if card.has_prev_part and card.prev_part_code:
                series_row.append(
                    InlineKeyboardButton(
                        text="⬅️ Oldingi",
                        callback_data=f"movie:{card.prev_part_code}",
                    )
                )

            series_row.append(
                InlineKeyboardButton(
                    text="📺 Barcha qismlar",
                    callback_data=f"series:view:{card.movie.series_id}",
                )
            )

            if card.has_next_part and card.next_part_code:
                series_row.append(
                    InlineKeyboardButton(
                        text="Keyingi ➡️",
                        callback_data=f"movie:{card.next_part_code}",
                    )
                )

            buttons.append(series_row)

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_simple_movie_keyboard(
        movie_code: int,
        is_favorite: bool = False,
    ) -> InlineKeyboardMarkup:
        """
        Get simple movie keyboard (rating + favorite + share).

        Args:
            movie_code: Movie code
            is_favorite: Whether movie is in favorites

        Returns:
            Simple inline keyboard
        """
        buttons = []

        # Rate button
        buttons.append([
            InlineKeyboardButton(
                text="⭐ Baholash",
                callback_data=f"rate:show:{movie_code}",
            )
        ])

        # Favorite & Share row
        action_row = []

        if is_favorite:
            action_row.append(
                InlineKeyboardButton(
                    text="💔 Olib tashlash",
                    callback_data=f"fav:remove:{movie_code}",
                )
            )
        else:
            action_row.append(
                InlineKeyboardButton(
                    text="❤️ Sevimli",
                    callback_data=f"fav:add:{movie_code}",
                )
            )

        action_row.append(
            InlineKeyboardButton(
                text="📤 Ulashish",
                switch_inline_query=str(movie_code),
            )
        )
        buttons.append(action_row)

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_series_navigation_keyboard(
        series_id: UUID,
        current_part: int,
        total_parts: int,
        prev_code: int | None = None,
        next_code: int | None = None,
    ) -> InlineKeyboardMarkup:
        """
        Get series navigation keyboard.

        Args:
            series_id: Series ID
            current_part: Current part number
            total_parts: Total parts in series
            prev_code: Previous part movie code
            next_code: Next part movie code

        Returns:
            Series navigation keyboard
        """
        buttons = []

        # Navigation row
        nav_row = []

        if prev_code:
            nav_row.append(
                InlineKeyboardButton(
                    text="⬅️ Oldingi",
                    callback_data=f"movie:{prev_code}",
                )
            )

        nav_row.append(
            InlineKeyboardButton(
                text=f"{current_part}/{total_parts}",
                callback_data="noop",
            )
        )

        if next_code:
            nav_row.append(
                InlineKeyboardButton(
                    text="Keyingi ➡️",
                    callback_data=f"movie:{next_code}",
                )
            )

        buttons.append(nav_row)

        # All parts button
        buttons.append([
            InlineKeyboardButton(
                text="📺 Barcha qismlar",
                callback_data=f"series:view:{series_id}",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)
