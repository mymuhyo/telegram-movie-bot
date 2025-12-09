"""Recommendation handlers."""

from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from src.application.services import MovieService, RecommendationService
from src.presentation.keyboards.user.recommendation import RecommendationKeyboard
from src.presentation.views.recommendation_view import RecommendationView

router = Router(name="recommendation")


@router.message(F.text.in_(["/recommend", "/tavsiya", "/rec"]))
async def cmd_recommend(
    message: Message,
    recommendation_service: FromDishka[RecommendationService],
) -> None:
    """
    Handle /recommend command.

    Shows personalized recommendations for the user.
    """
    if not message.from_user:
        return

    user_id = await _get_user_id(message.from_user.id)

    if not user_id:
        # No user data yet - show popular movies instead
        await _show_popular_movies(message, recommendation_service)
        return

    movies = await recommendation_service.get_recommendations(user_id, limit=5)

    if not movies:
        text = RecommendationView.format_empty_recommendations()
        keyboard = RecommendationKeyboard.get_empty_recommendations_keyboard()
    else:
        text = RecommendationView.format_recommendation_list(movies)
        keyboard = RecommendationKeyboard.get_recommendations_keyboard(movies)

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.message(F.text.in_(["/popular", "/mashhur"]))
async def cmd_popular(
    message: Message,
    movie_service: FromDishka[MovieService],
) -> None:
    """
    Handle /popular command.

    Shows most downloaded movies.
    """
    if not message.from_user:
        return

    movies = await movie_service.get_popular(limit=10)

    if not movies:
        await message.answer("📭 Hozircha kinolar mavjud emas")
        return

    text = RecommendationView.format_popular_header() + "\n\n"
    for i, movie in enumerate(movies, 1):
        text += RecommendationView.format_recommendation_item(movie, i) + "\n\n"
    text += "⬇️ Kodni yuboring:"

    keyboard = RecommendationKeyboard.get_recommendations_keyboard(movies, show_refresh=False)

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.message(F.text.in_(["/top", "/best", "/yaxshi"]))
async def cmd_top_rated(
    message: Message,
    movie_service: FromDishka[MovieService],
) -> None:
    """
    Handle /top command.

    Shows top rated movies.
    """
    if not message.from_user:
        return

    movies = await movie_service.get_top_rated(limit=10)

    if not movies:
        await message.answer("📭 Baholangan kinolar mavjud emas")
        return

    text = RecommendationView.format_top_rated_header() + "\n\n"
    for i, movie in enumerate(movies, 1):
        text += RecommendationView.format_recommendation_item(movie, i) + "\n\n"
    text += "⬇️ Kodni yuboring:"

    keyboard = RecommendationKeyboard.get_recommendations_keyboard(movies, show_refresh=False)

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.message(F.text.in_(["/new", "/yangi", "/recent"]))
async def cmd_recent(
    message: Message,
    movie_service: FromDishka[MovieService],
) -> None:
    """
    Handle /new command.

    Shows recently added movies.
    """
    if not message.from_user:
        return

    movies = await movie_service.get_recent(limit=10)

    if not movies:
        await message.answer("📭 Hozircha kinolar mavjud emas")
        return

    text = RecommendationView.format_recent_header() + "\n\n"
    for i, movie in enumerate(movies, 1):
        text += RecommendationView.format_recommendation_item(movie, i) + "\n\n"
    text += "⬇️ Kodni yuboring:"

    keyboard = RecommendationKeyboard.get_recommendations_keyboard(movies, show_refresh=False)

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "rec:refresh")
async def refresh_recommendations(
    callback: CallbackQuery,
    recommendation_service: FromDishka[RecommendationService],
) -> None:
    """Refresh recommendations."""
    await callback.answer("🔄 Yangilanmoqda...")

    if not callback.from_user or not callback.message:
        return

    user_id = await _get_user_id(callback.from_user.id)

    if not user_id:
        await callback.answer("❌ Avval botdan foydalaning", show_alert=True)
        return

    # Invalidate cache and get fresh recommendations
    movies = await recommendation_service.get_recommendations(user_id, limit=5)

    if not movies:
        text = RecommendationView.format_empty_recommendations()
        keyboard = RecommendationKeyboard.get_empty_recommendations_keyboard()
    else:
        text = RecommendationView.format_recommendation_list(movies)
        keyboard = RecommendationKeyboard.get_recommendations_keyboard(movies)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("rec:similar:"))
async def show_similar_movies(
    callback: CallbackQuery,
    movie_service: FromDishka[MovieService],
    recommendation_service: FromDishka[RecommendationService],
) -> None:
    """
    Show similar movies.

    Callback data: rec:similar:{movie_code}
    """
    await callback.answer()

    if not callback.data or not callback.message:
        return

    movie_code = int(callback.data.split(":")[-1])

    movie = await movie_service.get_by_code(movie_code)
    if not movie:
        await callback.answer("❌ Kino topilmadi", show_alert=True)
        return

    similar = await recommendation_service.get_similar_movies(movie.id, limit=5)

    text = RecommendationView.format_similar_list(similar, movie.title)
    keyboard = RecommendationKeyboard.get_similar_movies_keyboard(similar, movie_code)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "rec:popular")
async def show_popular_callback(
    callback: CallbackQuery,
    movie_service: FromDishka[MovieService],
) -> None:
    """Show popular movies from callback."""
    await callback.answer()

    if not callback.message:
        return

    movies = await movie_service.get_popular(limit=10)

    if not movies:
        await callback.message.edit_text("📭 Hozircha kinolar mavjud emas")
        return

    text = RecommendationView.format_popular_header() + "\n\n"
    for i, movie in enumerate(movies, 1):
        text += RecommendationView.format_recommendation_item(movie, i) + "\n\n"

    keyboard = RecommendationKeyboard.get_recommendations_keyboard(movies, show_refresh=False)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "rec:top")
async def show_top_callback(
    callback: CallbackQuery,
    movie_service: FromDishka[MovieService],
) -> None:
    """Show top rated movies from callback."""
    await callback.answer()

    if not callback.message:
        return

    movies = await movie_service.get_top_rated(limit=10)

    if not movies:
        await callback.message.edit_text("📭 Baholangan kinolar mavjud emas")
        return

    text = RecommendationView.format_top_rated_header() + "\n\n"
    for i, movie in enumerate(movies, 1):
        text += RecommendationView.format_recommendation_item(movie, i) + "\n\n"

    keyboard = RecommendationKeyboard.get_recommendations_keyboard(movies, show_refresh=False)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "rec:recent")
async def show_recent_callback(
    callback: CallbackQuery,
    movie_service: FromDishka[MovieService],
) -> None:
    """Show recent movies from callback."""
    await callback.answer()

    if not callback.message:
        return

    movies = await movie_service.get_recent(limit=10)

    if not movies:
        await callback.message.edit_text("📭 Hozircha kinolar mavjud emas")
        return

    text = RecommendationView.format_recent_header() + "\n\n"
    for i, movie in enumerate(movies, 1):
        text += RecommendationView.format_recommendation_item(movie, i) + "\n\n"

    keyboard = RecommendationKeyboard.get_recommendations_keyboard(movies, show_refresh=False)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


async def _show_popular_movies(
    message: Message,
    recommendation_service: RecommendationService,
) -> None:
    """Show popular movies for new users."""
    # For new users, we'll show a helpful message
    text = RecommendationView.format_empty_recommendations()
    keyboard = RecommendationKeyboard.get_empty_recommendations_keyboard()

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


async def _get_user_id(telegram_id: int) -> UUID | None:
    """
    Get internal user ID from Telegram ID.

    Note: In production, this should come from middleware/DI.
    """
    return None
