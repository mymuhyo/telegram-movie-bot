"""Admin panel handlers."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import (
    get_admin_panel_keyboard,
    get_back_to_admin_keyboard,
    get_maintenance_keyboard,
    get_statistics_keyboard,
)
from src.core import get_logger
from src.infrastructure import UnitOfWork
from src.infrastructure.database.models.admin import AdminModel
from src.texts import messages

logger = get_logger(__name__)

router = Router(name="admin")


@router.message(Command("admin"))
async def cmd_admin(
    message: Message,
    is_admin: bool,
    is_super_admin: bool,
    admin: AdminModel | None,
) -> None:
    """Handle /admin command."""
    if not is_admin:
        await message.answer(messages.ADMIN_ONLY)
        return

    await message.answer(
        messages.ADMIN_PANEL,
        reply_markup=get_admin_panel_keyboard(is_super_admin),
    )

    logger.info("admin_panel_accessed", admin_id=admin.telegram_id if admin else None)


@router.callback_query(F.data == "admin:panel")
async def callback_admin_panel(
    callback: CallbackQuery,
    is_admin: bool,
    is_super_admin: bool,
) -> None:
    """Handle admin panel callback."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        messages.ADMIN_PANEL,
        reply_markup=get_admin_panel_keyboard(is_super_admin),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def callback_statistics(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_admin: bool,
) -> None:
    """Handle statistics callback."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    # Gather statistics
    total_users = await uow.users.get_total_count()
    active_users = await uow.users.get_active_count(days=7)
    today_users = await uow.users.get_count_by_period(days=1)
    week_users = await uow.users.get_count_by_period(days=7)
    month_users = await uow.users.get_count_by_period(days=30)

    total_downloads = await uow.downloads.get_total_count()
    today_downloads = await uow.downloads.get_today_count()
    week_downloads = await uow.downloads.get_count_by_period(days=7)
    month_downloads = await uow.downloads.get_count_by_period(days=30)

    total_movies = await uow.movies.get_total_count()

    # Get top movies
    top_all_time = await uow.downloads.get_top_movies(limit=5)
    top_week = await uow.downloads.get_top_movies(limit=5, days=7)

    # Format top movies
    def format_top(top_list: list[tuple[int, int]]) -> str:
        if not top_list:
            return "Ma'lumot yo'q"
        lines = []
        for i, (code, count) in enumerate(top_list, 1):
            lines.append(f"{i}. Kod {code} — {count} ta")
        return "\n".join(lines)

    await callback.message.edit_text(
        messages.STATISTICS.format(
            total_users=total_users,
            active_users=active_users,
            today_users=today_users,
            week_users=week_users,
            month_users=month_users,
            total_downloads=total_downloads,
            today_downloads=today_downloads,
            week_downloads=week_downloads,
            month_downloads=month_downloads,
            total_movies=total_movies,
            top_all_time=format_top(top_all_time),
            top_week=format_top(top_week),
        ),
        reply_markup=get_statistics_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:maintenance")
async def callback_maintenance(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_admin: bool,
) -> None:
    """Handle maintenance mode callback."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    is_enabled = await uow.settings.is_maintenance_mode()
    message_text = await uow.settings.get_maintenance_message()

    status = "✅ Yoqilgan" if is_enabled else "❌ O'chirilgan"

    await callback.message.edit_text(
        messages.MAINTENANCE_STATUS.format(
            status=status,
            message=message_text,
        ),
        reply_markup=get_maintenance_keyboard(is_enabled),
    )
    await callback.answer()


@router.callback_query(F.data == "maintenance:toggle")
async def callback_maintenance_toggle(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_admin: bool,
) -> None:
    """Handle maintenance toggle."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    current = await uow.settings.is_maintenance_mode()
    await uow.settings.set("maintenance_mode", not current)

    if current:
        await callback.answer(messages.MAINTENANCE_OFF)
    else:
        await callback.answer(messages.MAINTENANCE_ON)

    # Refresh view
    await callback_maintenance(callback, uow, is_admin)


@router.callback_query(F.data == "admin:movies")
async def callback_movies_list(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_admin: bool,
) -> None:
    """Handle movies list callback."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    movies = await uow.movies.get_all(limit=10)
    total = await uow.movies.get_total_count()

    if not movies:
        await callback.message.edit_text(
            "📋 Kinolar ro'yxati\n\nKinolar mavjud emas.",
            reply_markup=get_back_to_admin_keyboard(),
        )
        await callback.answer()
        return

    movies_text = "\n".join([f"{i+1}. {m.title} — kod: {m.code}" for i, m in enumerate(movies)])

    await callback.message.edit_text(
        messages.MOVIE_LIST.format(
            total=total,
            movies=movies_text,
        ),
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()
