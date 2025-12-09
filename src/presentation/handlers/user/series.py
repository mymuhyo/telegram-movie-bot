"""Series navigation handlers."""

from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from src.application.services import MovieService, SeriesService
from src.core.exceptions import SeriesNotFoundError
from src.presentation.keyboards.user.series import SeriesKeyboard
from src.presentation.views.series_view import SeriesView

router = Router(name="series")


@router.message(F.text == "/series")
async def cmd_series(
    message: Message,
    series_service: FromDishka[SeriesService],
) -> None:
    """
    Handle /series command.

    Shows list of all available series.
    """
    if not message.from_user:
        return

    series_list = await series_service.get_all_series()

    if not series_list:
        await message.answer(
            SeriesView.format_empty_series_list(),
            parse_mode="MarkdownV2",
        )
        return

    # Get series with progress for current user
    # Note: User progress will be integrated with middleware
    user_id = await _get_user_id(message.from_user.id)

    series_with_progress = []
    for series_dto in series_list:
        series_data = await series_service.get_series_with_parts(series_dto.id)
        progress = None
        if user_id:
            progress = await series_service.get_user_progress(user_id, series_dto.id)
        series_with_progress.append((series_data, progress))

    keyboard = SeriesKeyboard.get_series_list_keyboard(series_with_progress)

    await message.answer(
        SeriesView.format_series_list_header(),
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.message(F.text == "/continue")
async def cmd_continue(
    message: Message,
    series_service: FromDishka[SeriesService],
) -> None:
    """
    Handle /continue command.

    Shows series that user is currently watching.
    """
    if not message.from_user:
        return

    user_id = await _get_user_id(message.from_user.id)

    if not user_id:
        await message.answer(
            "❌ Avval botni ishlatishni boshlang.",
        )
        return

    progress_list = await series_service.get_user_in_progress_series(user_id)

    if not progress_list:
        await message.answer(
            SeriesView.format_no_progress(),
            parse_mode="MarkdownV2",
        )
        return

    # Get series data for each progress
    series_with_progress = []
    for progress in progress_list:
        series_data = await series_service.get_series_with_parts(progress.series_id)
        series_with_progress.append((series_data, progress))

    keyboard = SeriesKeyboard.get_in_progress_keyboard(series_with_progress)

    await message.answer(
        SeriesView.format_in_progress_header(),
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "series:list")
async def show_series_list(
    callback: CallbackQuery,
    series_service: FromDishka[SeriesService],
) -> None:
    """Show all series list."""
    await callback.answer()

    if not callback.from_user or not callback.message:
        return

    series_list = await series_service.get_all_series()

    if not series_list:
        await callback.message.edit_text(
            SeriesView.format_empty_series_list(),
            parse_mode="MarkdownV2",
        )
        return

    user_id = await _get_user_id(callback.from_user.id)

    series_with_progress = []
    for series_dto in series_list:
        series_data = await series_service.get_series_with_parts(series_dto.id)
        progress = None
        if user_id:
            progress = await series_service.get_user_progress(user_id, series_dto.id)
        series_with_progress.append((series_data, progress))

    keyboard = SeriesKeyboard.get_series_list_keyboard(series_with_progress)

    await callback.message.edit_text(
        SeriesView.format_series_list_header(),
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("series:list:page:"))
async def series_list_pagination(
    callback: CallbackQuery,
    series_service: FromDishka[SeriesService],
) -> None:
    """Handle series list pagination."""
    await callback.answer()

    if not callback.data or not callback.from_user or not callback.message:
        return

    page = int(callback.data.split(":")[-1])

    series_list = await series_service.get_all_series()
    user_id = await _get_user_id(callback.from_user.id)

    series_with_progress = []
    for series_dto in series_list:
        series_data = await series_service.get_series_with_parts(series_dto.id)
        progress = None
        if user_id:
            progress = await series_service.get_user_progress(user_id, series_dto.id)
        series_with_progress.append((series_data, progress))

    keyboard = SeriesKeyboard.get_series_list_keyboard(series_with_progress, page=page)

    await callback.message.edit_text(
        SeriesView.format_series_list_header(),
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("series:view:"))
async def view_series(
    callback: CallbackQuery,
    series_service: FromDishka[SeriesService],
) -> None:
    """
    View series details and parts list.

    Callback data: series:view:{series_id}
    """
    await callback.answer()

    if not callback.data or not callback.from_user or not callback.message:
        return

    series_id_str = callback.data.split(":")[-1]

    try:
        series_id = UUID(series_id_str)
    except ValueError:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        return

    try:
        series_data = await series_service.get_series_with_parts(series_id)
    except SeriesNotFoundError:
        await callback.message.edit_text("❌ Serial topilmadi")
        return

    user_id = await _get_user_id(callback.from_user.id)
    progress = None

    if user_id:
        progress = await series_service.get_user_progress(user_id, series_id)

    keyboard = SeriesKeyboard.get_series_parts_keyboard(series_data, progress)
    text = SeriesView.format_series_with_progress(series_data, progress)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("series:page:"))
async def series_parts_pagination(
    callback: CallbackQuery,
    series_service: FromDishka[SeriesService],
) -> None:
    """
    Handle series parts pagination.

    Callback data: series:page:{series_id}:{page}
    """
    await callback.answer()

    if not callback.data or not callback.from_user or not callback.message:
        return

    parts = callback.data.split(":")
    series_id_str = parts[2]
    page = int(parts[3])

    try:
        series_id = UUID(series_id_str)
    except ValueError:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        return

    try:
        series_data = await series_service.get_series_with_parts(series_id)
    except SeriesNotFoundError:
        await callback.message.edit_text("❌ Serial topilmadi")
        return

    user_id = await _get_user_id(callback.from_user.id)
    progress = None

    if user_id:
        progress = await series_service.get_user_progress(user_id, series_id)

    keyboard = SeriesKeyboard.get_series_parts_keyboard(series_data, progress, page=page)
    text = SeriesView.format_series_with_progress(series_data, progress)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("series:mark:"))
async def mark_part_watched(
    callback: CallbackQuery,
    series_service: FromDishka[SeriesService],
) -> None:
    """
    Mark a part as watched.

    Callback data: series:mark:{series_id}:{part_number}
    """
    await callback.answer()

    if not callback.data or not callback.from_user or not callback.message:
        return

    parts = callback.data.split(":")
    series_id_str = parts[2]
    part_number = int(parts[3])

    try:
        series_id = UUID(series_id_str)
    except ValueError:
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        return

    user_id = await _get_user_id(callback.from_user.id)

    if not user_id:
        await callback.answer("❌ Avval botni ishlatishni boshlang", show_alert=True)
        return

    try:
        progress = await series_service.mark_part_watched(
            user_id=user_id,
            series_id=series_id,
            part_number=part_number,
        )

        text = SeriesView.format_progress_updated(
            series_name=progress.series_name,
            part_number=part_number,
            total_parts=progress.total_parts,
            watched_count=progress.watched_count,
        )

        await callback.message.edit_text(
            text,
            parse_mode="MarkdownV2",
        )

    except SeriesNotFoundError:
        await callback.message.edit_text("❌ Serial topilmadi")


@router.callback_query(F.data == "close")
async def close_message(callback: CallbackQuery) -> None:
    """Close/delete the message."""
    await callback.answer()
    if callback.message:
        await callback.message.delete()


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery) -> None:
    """Handle no-operation callbacks (like page counters)."""
    await callback.answer()


async def _get_user_id(telegram_id: int) -> UUID | None:
    """
    Get internal user ID from Telegram ID.

    Note: In production, this should come from middleware/DI.
    This is a placeholder for the user injection middleware.
    """
    # This will be replaced when we integrate with the user middleware
    # For now, return None to indicate the need for proper integration
    return None
