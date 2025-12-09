"""Recommendation keyboard builder."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.application.dto import MovieDTO


class RecommendationKeyboard:
    """Keyboard builder for recommendations."""

    @staticmethod
    def get_recommendations_keyboard(
        movies: list[MovieDTO],
        show_refresh: bool = True,
    ) -> InlineKeyboardMarkup:
        """
        Get keyboard with recommended movies.

        Args:
            movies: List of recommended movies
            show_refresh: Whether to show refresh button

        Returns:
            Inline keyboard with movie buttons
        """
        buttons = []

        for movie in movies:
            # Format: title with rating
            rating = ""
            if movie.rating_count > 0:
                rating = f" ⭐{movie.average_rating:.1f}"

            title = movie.title[:35]
            if len(movie.title) > 35:
                title += "..."

            buttons.append([
                InlineKeyboardButton(
                    text=f"🎬 {title}{rating}",
                    callback_data=f"movie:{movie.code}",
                )
            ])

        # Action buttons
        action_row = []

        if show_refresh:
            action_row.append(
                InlineKeyboardButton(
                    text="🔄 Yangilash",
                    callback_data="rec:refresh",
                )
            )

        action_row.append(
            InlineKeyboardButton(
                text="❌ Yopish",
                callback_data="close",
            )
        )

        buttons.append(action_row)

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_similar_movies_keyboard(
        movies: list[MovieDTO],
        current_code: int,
    ) -> InlineKeyboardMarkup:
        """
        Get keyboard with similar movies.

        Args:
            movies: List of similar movies
            current_code: Current movie code (to go back)

        Returns:
            Inline keyboard with similar movie buttons
        """
        buttons = []

        for movie in movies:
            rating = ""
            if movie.rating_count > 0:
                rating = f" ⭐{movie.average_rating:.1f}"

            title = movie.title[:30]
            if len(movie.title) > 30:
                title += "..."

            # Show part info for series
            part_info = ""
            if movie.part_number:
                part_info = f" ({movie.part_number}-qism)"

            buttons.append([
                InlineKeyboardButton(
                    text=f"🎬 {title}{part_info}{rating}",
                    callback_data=f"movie:{movie.code}",
                )
            ])

        # Back button
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data=f"movie:{current_code}",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_continue_watching_keyboard(
        movies: list[MovieDTO],
    ) -> InlineKeyboardMarkup:
        """
        Get keyboard with continue watching options.

        Args:
            movies: List of next parts to watch

        Returns:
            Inline keyboard with continue options
        """
        buttons = []

        for movie in movies:
            part_info = f"{movie.part_number}-qism" if movie.part_number else ""
            title = movie.title[:25]
            if len(movie.title) > 25:
                title += "..."

            buttons.append([
                InlineKeyboardButton(
                    text=f"▶️ {title} {part_info}",
                    callback_data=f"movie:{movie.code}",
                )
            ])

        if not buttons:
            buttons.append([
                InlineKeyboardButton(
                    text="📭 Ko'rayotgan seriallar yo'q",
                    callback_data="noop",
                )
            ])

        # View all series
        buttons.append([
            InlineKeyboardButton(
                text="📺 Barcha seriallar",
                callback_data="series:list",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_movie_with_similar_button(
        movie_code: int,
        is_favorite: bool = False,
    ) -> InlineKeyboardMarkup:
        """
        Get movie keyboard with similar movies button.

        Args:
            movie_code: Movie code
            is_favorite: Whether movie is in favorites

        Returns:
            Keyboard with rate, favorite, share, and similar buttons
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

        # Similar movies button
        buttons.append([
            InlineKeyboardButton(
                text="🎯 O'xshash kinolar",
                callback_data=f"rec:similar:{movie_code}",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_empty_recommendations_keyboard() -> InlineKeyboardMarkup:
        """
        Get keyboard for empty recommendations.

        Returns:
            Keyboard with helpful suggestions
        """
        buttons = [
            [
                InlineKeyboardButton(
                    text="🔥 Mashhur kinolar",
                    callback_data="rec:popular",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Eng yaxshilari",
                    callback_data="rec:top",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🆕 Yangi kinolar",
                    callback_data="rec:recent",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Yopish",
                    callback_data="close",
                )
            ],
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)
