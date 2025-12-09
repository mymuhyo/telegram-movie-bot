"""Rating handlers."""

from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from src.application.services import MovieService, RatingService
from src.core.exceptions import MovieNotFoundError
from src.presentation.keyboards.user.rating import RatingKeyboard
from src.presentation.views.movie_view import MovieView

router = Router(name="rating")


@router.callback_query(F.data.startswith("rate:"))
async def handle_rating_callback(
    callback: CallbackQuery,
    movie_service: FromDishka[MovieService],
    rating_service: FromDishka[RatingService],
) -> None:
    """
    Handle rating callbacks.

    Callback data formats:
    - rate:{code}:{score} - Rate movie with score
    - rate:show:{code} - Show rating keyboard
    - rate:cancel - Cancel rating
    """
    await callback.answer()

    if not callback.data or not callback.from_user:
        return

    parts = callback.data.split(":")

    # Cancel rating
    if parts[1] == "cancel":
        await callback.message.edit_text("❌ Baholash bekor qilindi")
        return

    # Show rating keyboard
    if parts[1] == "show":
        code = int(parts[2])
        try:
            movie = await movie_service.get_by_code(code)
            if not movie:
                await callback.message.edit_text("❌ Kino topilmadi")
                return

            # Get user's current rating
            # Note: We need user_id from somewhere - typically from middleware
            # For now, we'll show keyboard without current rating highlight
            keyboard = RatingKeyboard.get_rating_keyboard(code)
            text = MovieView.format_rating_prompt(movie)

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        except MovieNotFoundError:
            await callback.message.edit_text("❌ Kino topilmadi")
        return

    # Rate movie: rate:{code}:{score}
    if len(parts) >= 3 and parts[1].isdigit():
        code = int(parts[1])
        score = int(parts[2])

        if not 1 <= score <= 5:
            await callback.answer("❌ Noto'g'ri baho", show_alert=True)
            return

        try:
            movie = await movie_service.get_by_code(code)
            if not movie:
                await callback.message.edit_text("❌ Kino topilmadi")
                return

            # Get user ID - in real implementation, this comes from middleware
            # For now, we'll use a placeholder approach
            user_id = await _get_user_id(callback.from_user.id)

            if user_id:
                # Rate the movie
                await rating_service.rate_movie(
                    user_id=user_id,
                    movie_id=movie.id,
                    score=score,
                )

                # Show success message
                stars = "⭐" * score
                await callback.message.edit_text(
                    f"✅ Rahmat! *{movie.title}* uchun bahongiz: {stars}",
                    parse_mode="Markdown",
                )
            else:
                await callback.answer(
                    "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                    show_alert=True,
                )

        except MovieNotFoundError:
            await callback.message.edit_text("❌ Kino topilmadi")
        except Exception as e:
            await callback.answer(f"❌ Xatolik: {e}", show_alert=True)


async def _get_user_id(telegram_id: int) -> UUID | None:
    """
    Get internal user ID from Telegram ID.

    Note: In production, this should come from middleware/DI.
    This is a placeholder for the user injection middleware.
    """
    # This will be replaced when we integrate with the user middleware
    # For now, return None to indicate the need for proper integration
    return None


# Additional handler for direct rating from movie card
@router.callback_query(F.data.regexp(r"^rate:\d+:\d+$"))
async def handle_direct_rating(
    callback: CallbackQuery,
    movie_service: FromDishka[MovieService],
    rating_service: FromDishka[RatingService],
) -> None:
    """
    Handle direct rating from movie card.

    This is triggered when user clicks on rating stars in movie card.
    """
    # This is handled by the main handler above
    # Keeping this for explicit routing if needed
    pass
