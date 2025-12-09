"""Rating keyboard builder."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class RatingKeyboard:
    """Rating keyboard builder."""

    @staticmethod
    def get_rating_keyboard(
        movie_code: int,
        current_rating: int | None = None,
    ) -> InlineKeyboardMarkup:
        """
        Get rating keyboard with 1-5 stars.

        Args:
            movie_code: Movie code
            current_rating: User's current rating (highlighted)

        Returns:
            Inline keyboard with rating buttons
        """
        buttons = []

        # Rating buttons row
        rating_row = []
        for score in range(1, 6):
            if current_rating == score:
                # Highlighted current rating
                text = f"[{'⭐' * score}]"
            else:
                text = "⭐" * score

            rating_row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"rate:{movie_code}:{score}",
                )
            )

        buttons.append(rating_row)

        # Cancel button
        buttons.append([
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data="rate:cancel",
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def get_compact_rating_keyboard(
        movie_code: int,
        current_rating: int | None = None,
    ) -> InlineKeyboardMarkup:
        """
        Get compact rating keyboard (single row).

        Args:
            movie_code: Movie code
            current_rating: User's current rating

        Returns:
            Compact inline keyboard
        """
        rating_row = []

        for score in range(1, 6):
            if current_rating == score:
                text = f"[{score}⭐]"
            else:
                text = f"{score}⭐"

            rating_row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"rate:{movie_code}:{score}",
                )
            )

        return InlineKeyboardMarkup(inline_keyboard=[rating_row])

    @staticmethod
    def get_rating_confirmation_keyboard(
        movie_code: int,
        score: int,
    ) -> InlineKeyboardMarkup:
        """
        Get rating confirmation keyboard.

        Args:
            movie_code: Movie code
            score: Rating score to confirm

        Returns:
            Confirmation keyboard
        """
        stars = "⭐" * score

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"✅ {stars} tasdiqlash",
                        callback_data=f"rate:confirm:{movie_code}:{score}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔄 Qayta tanlash",
                        callback_data=f"rate:retry:{movie_code}",
                    ),
                    InlineKeyboardButton(
                        text="❌ Bekor",
                        callback_data="rate:cancel",
                    ),
                ],
            ]
        )
