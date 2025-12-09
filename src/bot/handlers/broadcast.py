"""Broadcast handlers with progress tracking."""

import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import (
    get_back_to_admin_keyboard,
    get_broadcast_confirm_keyboard,
    get_broadcast_keyboard,
)
from src.bot.loader import bot
from src.core import get_logger
from src.core.config import settings
from src.infrastructure import UnitOfWork
from src.texts import messages

logger = get_logger(__name__)

router = Router(name="broadcast")


class BroadcastStates(StatesGroup):
    """States for broadcasting."""

    waiting_content = State()
    confirm = State()
    sending = State()


@router.callback_query(F.data == "admin:broadcast")
async def callback_broadcast_menu(
    callback: CallbackQuery,
    is_admin: bool,
) -> None:
    """Show broadcast menu."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        messages.BROADCAST_MENU,
        reply_markup=get_broadcast_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast:custom")
async def callback_broadcast_custom(
    callback: CallbackQuery,
    state: FSMContext,
    is_admin: bool,
) -> None:
    """Start custom broadcast."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        messages.BROADCAST_ASK_CONTENT,
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(BroadcastStates.waiting_content)
    await callback.answer()


@router.message(BroadcastStates.waiting_content)
async def handle_broadcast_content(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle broadcast content."""
    # Store content info
    content_type = "text"
    content = message.text or message.caption or ""
    file_id = None

    if message.photo:
        content_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        content_type = "video"
        file_id = message.video.file_id

    await state.update_data(
        content_type=content_type,
        content=content,
        file_id=file_id,
    )

    # Get user count
    user_ids = await uow.users.get_all_active_ids()
    user_count = len(user_ids)

    await message.answer(
        messages.BROADCAST_CONFIRM.format(count=user_count),
        reply_markup=get_broadcast_confirm_keyboard(),
    )
    await state.set_state(BroadcastStates.confirm)


@router.callback_query(F.data == "broadcast:send")
async def callback_broadcast_send(
    callback: CallbackQuery,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Start sending broadcast."""
    data = await state.get_data()
    content_type = data.get("content_type", "text")
    content = data.get("content", "")
    file_id = data.get("file_id")

    # Get all user IDs
    user_ids = await uow.users.get_all_active_ids()
    total = len(user_ids)

    if total == 0:
        await callback.message.edit_text(
            "❌ Foydalanuvchilar yo'q!",
            reply_markup=get_back_to_admin_keyboard(),
        )
        await state.clear()
        await callback.answer()
        return

    await state.set_state(BroadcastStates.sending)
    await callback.answer()

    # Progress tracking
    sent = 0
    failed = 0
    batch_size = settings.broadcast_batch_size
    delay_ms = settings.broadcast_delay_ms

    # Initial progress message
    progress_msg = await callback.message.edit_text(
        _format_progress(sent, failed, total, 0),
    )

    # Send in batches
    for i, user_id in enumerate(user_ids):
        try:
            if content_type == "text":
                await bot.send_message(user_id, content)
            elif content_type == "photo":
                await bot.send_photo(user_id, file_id, caption=content)
            elif content_type == "video":
                await bot.send_video(user_id, file_id, caption=content)
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning("broadcast_failed", user_id=user_id, error=str(e))

        # Update progress every batch
        if (i + 1) % batch_size == 0 or i == total - 1:
            percent = int((i + 1) / total * 100)
            try:
                await progress_msg.edit_text(
                    _format_progress(sent, failed, total, percent),
                )
            except Exception as e:
                # Silently ignore Telegram API edit errors (message not modified, etc.)
                logger.debug("broadcast_progress_update_failed", error=str(e))

        # Rate limiting delay
        await asyncio.sleep(delay_ms / 1000)

    # Final result
    await progress_msg.edit_text(
        messages.BROADCAST_SUCCESS.format(success=sent, fail=failed),
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.clear()

    logger.info("broadcast_completed", total=total, sent=sent, failed=failed)


def _format_progress(sent: int, failed: int, total: int, percent: int) -> str:
    """Format progress message."""
    bar_length = 10
    filled = int(bar_length * percent / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    remaining = total - sent - failed
    # Rough estimate: ~50ms per message
    eta_seconds = remaining * 0.05
    if eta_seconds < 60:
        eta = f"{int(eta_seconds)} soniya"
    else:
        eta = f"{int(eta_seconds / 60)} daqiqa"

    return messages.BROADCAST_PROGRESS.format(
        progress_bar=bar,
        percent=percent,
        sent=sent,
        total=total,
        failed=failed,
        remaining=eta,
    )


@router.callback_query(F.data == "admin:broadcast", BroadcastStates)
async def callback_cancel_broadcast(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Cancel broadcast."""
    await state.clear()
    await callback.message.edit_text(
        messages.BROADCAST_CANCELLED,
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()
