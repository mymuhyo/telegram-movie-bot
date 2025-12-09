"""Favorite handlers."""

from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from src.application.dto import PaginatedResult
from src.application.services import FavoriteService, MovieService
from src.core.exceptions import MovieNotFoundError
from src.presentation.keyboards.user.favorite import FavoriteKeyboard

router = Router(name="favorite")


@router.message(F.text == "/favorites")
async def handle_favorites_command(
    message: Message,
    favorite_service: FromDishka[FavoriteService],
) -> None:
    """Handle /favorites command - show user's favorites."""
    if not message.from_user:
        return

    user_id = await _get_user_id(message.from_user.id)
    if not user_id:
        await message.answer("❌ Xatolik yuz berdi")
        return

    result = await favorite_service.get_favorites(user_id, page=1, per_page=10)

    if result.is_empty:
        await message.answer(
            "📭 Sevimlilar ro'yxati bo'sh\n\n"
            "Kino kartasidagi ❤️ tugmasini bosib qo'shishingiz mumkin."
        )
        return

    text = _format_favorites_list(result)
    keyboard = FavoriteKeyboard.get_favorites_list_keyboard(result)

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data.startswith("fav:"))
async def handle_favorite_callback(
    callback: CallbackQuery,
    favorite_service: FromDishka[FavoriteService],
    movie_service: FromDishka[MovieService],
) -> None:
    """
    Handle favorite callbacks.

    Callback data formats:
    - fav:add:{code} - Add to favorites
    - fav:remove:{code} - Remove from favorites
    - fav:page:{page} - Navigate favorites list
    """
    await callback.answer()

    if not callback.data or not callback.from_user:
        return

    parts = callback.data.split(":")
    action = parts[1]

    user_id = await _get_user_id(callback.from_user.id)
    if not user_id:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        return

    # Add to favorites
    if action == "add":
        code = int(parts[2])
        try:
            movie = await movie_service.get_by_code(code)
            if not movie:
                await callback.answer("❌ Kino topilmadi", show_alert=True)
                return

            added = await favorite_service.add_to_favorites(user_id, movie.id)

            if added:
                await callback.answer("❤️ Sevimlilarga qo'shildi!", show_alert=True)
            else:
                await callback.answer("Allaqachon sevimlilarda", show_alert=True)

        except MovieNotFoundError:
            await callback.answer("❌ Kino topilmadi", show_alert=True)

    # Remove from favorites
    elif action == "remove":
        code = int(parts[2])
        try:
            movie = await movie_service.get_by_code(code)
            if not movie:
                await callback.answer("❌ Kino topilmadi", show_alert=True)
                return

            removed = await favorite_service.remove_from_favorites(user_id, movie.id)

            if removed:
                await callback.answer("💔 Sevimlilardan olib tashlandi", show_alert=True)
            else:
                await callback.answer("Sevimlilarda yo'q edi", show_alert=True)

        except MovieNotFoundError:
            await callback.answer("❌ Kino topilmadi", show_alert=True)

    # Navigate pages
    elif action == "page":
        page = int(parts[2])
        result = await favorite_service.get_favorites(user_id, page=page, per_page=10)

        if result.is_empty:
            await callback.message.edit_text("📭 Sevimlilar ro'yxati bo'sh")
            return

        text = _format_favorites_list(result)
        keyboard = FavoriteKeyboard.get_favorites_list_keyboard(result)

        await callback.message.edit_text(
            text, reply_markup=keyboard, parse_mode="Markdown"
        )


def _format_favorites_list(result: PaginatedResult) -> str:
    """Format favorites list for display."""
    lines = ["❤️ *Sevimli kinolar*", ""]

    for i, movie in enumerate(result.items, start=result.start_index):
        title = movie.title[:35]
        if len(movie.title) > 35:
            title += "..."

        rating = ""
        if movie.rating_count > 0:
            rating = f" ⭐{movie.average_rating}"

        lines.append(f"{i}. `{movie.code}` — {title}{rating}")

    lines.append("")
    lines.append(f"📊 Jami: {result.total} ta")

    if result.total_pages > 1:
        lines.append(f"📄 Sahifa: {result.page}/{result.total_pages}")

    return "\n".join(lines)


async def _get_user_id(telegram_id: int) -> UUID | None:
    """Get internal user ID from Telegram ID."""
    # Placeholder - will be replaced with proper user middleware
    return None
