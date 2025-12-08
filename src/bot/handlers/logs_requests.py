"""Admin logs viewer and user requests handlers."""
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.keyboards import get_back_to_admin_keyboard
from src.core import get_logger
from src.infrastructure import UnitOfWork
from src.texts import messages

logger = get_logger(__name__)

router = Router(name="logs_requests")


# ========== ADMIN LOGS ==========

@router.callback_query(F.data == "admin:logs")
async def callback_admin_logs(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_admin: bool,
) -> None:
    """Show recent admin logs."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    # Get recent logs from admin_logs table
    from sqlalchemy import select, desc
    from src.infrastructure.database.models.admin_log import AdminLogModel
    
    query = (
        select(AdminLogModel)
        .order_by(desc(AdminLogModel.created_at))
        .limit(20)
    )
    result = await uow._session.execute(query)
    logs = result.scalars().all()
    
    if not logs:
        await callback.message.edit_text(
            "📜 Admin loglari\n\nLoglar mavjud emas.",
            reply_markup=get_back_to_admin_keyboard(),
        )
        await callback.answer()
        return
    
    text = "📜 So'nggi admin loglari\n\n"
    for log in logs[:15]:
        time_str = log.created_at.strftime("%d.%m %H:%M")
        text += f"• [{time_str}] {log.action_type}\n"
        if log.details:
            text += f"  └ {log.details[:50]}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_admin_keyboard(),
    )
    await callback.answer()


# ========== USER REQUESTS ==========

@router.callback_query(F.data == "admin:requests")
async def callback_requests_menu(
    callback: CallbackQuery,
    is_admin: bool,
) -> None:
    """Show requests menu."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        "📩 Foydalanuvchi so'rovlari\n\nTanlang:",
        reply_markup=get_requests_keyboard(),
    )
    await callback.answer()

def get_requests_keyboard() -> InlineKeyboardMarkup:
    """Get requests menu keyboard."""
    from src.texts import buttons
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🆕 Yangi so'rovlar", callback_data="requests:pending"),
            ],
            [
                InlineKeyboardButton(text="✅ Ko'rib chiqilganlar", callback_data="requests:processed"),
            ],
            [
                InlineKeyboardButton(text=buttons.BTN_STATISTICS, callback_data="requests:stats"),
            ],
            [
                InlineKeyboardButton(text=buttons.BTN_ADMIN_PANEL, callback_data="admin:panel"),
            ],
        ]
    )

@router.callback_query(F.data == "requests:pending")
async def callback_pending_requests(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Show pending requests."""
    from sqlalchemy import select
    from src.infrastructure.database.models.request import MovieRequestModel
    from src.texts import buttons
    
    query = (
        select(MovieRequestModel)
        .where(MovieRequestModel.status == "pending")
        .order_by(MovieRequestModel.created_at.desc())
        .limit(20)
    )
    result = await uow._session.execute(query)
    requests = result.scalars().all()
    
    if not requests:
        await callback.message.edit_text(
            "📩 Yangi so'rovlar\n\nYangi so'rovlar yo'q!",
            reply_markup=get_requests_keyboard(),
        )
        await callback.answer()
        return
    
    text = "📩 Yangi so'rovlar\n\n"
    keyboard = []
    
    for req in requests[:10]:
        text += f"• {req.title}\n"
        keyboard.append([
            InlineKeyboardButton(
                text=f"✅ {req.title[:20]}",
                callback_data=f"request:approve:{req.id}",
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=f"request:reject:{req.id}",
            ),
        ])
    
    keyboard.append([
        InlineKeyboardButton(text=buttons.BTN_BACK, callback_data="admin:requests")
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("request:approve:"))
async def callback_approve_request(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Approve a request."""
    request_id = callback.data.split(":")[2]
    
    from sqlalchemy import update
    from src.infrastructure.database.models.request import MovieRequestModel
    from uuid import UUID
    
    await uow._session.execute(
        update(MovieRequestModel)
        .where(MovieRequestModel.id == UUID(request_id))
        .values(status="approved")
    )
    await uow.commit()
    
    await callback.answer("✅ So'rov qabul qilindi!", show_alert=True)
    # Refresh list
    await callback_pending_requests(callback, uow)


@router.callback_query(F.data.startswith("request:reject:"))
async def callback_reject_request(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Reject a request."""
    request_id = callback.data.split(":")[2]
    
    from sqlalchemy import update
    from src.infrastructure.database.models.request import MovieRequestModel
    from uuid import UUID
    
    await uow._session.execute(
        update(MovieRequestModel)
        .where(MovieRequestModel.id == UUID(request_id))
        .values(status="rejected")
    )
    await uow.commit()
    
    await callback.answer("❌ So'rov rad etildi!", show_alert=True)
    # Refresh list
    await callback_pending_requests(callback, uow)


@router.callback_query(F.data == "requests:processed")
async def callback_processed_requests(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Show processed requests."""
    from sqlalchemy import select, or_
    from src.infrastructure.database.models.request import MovieRequestModel
    
    query = (
        select(MovieRequestModel)
        .where(or_(
            MovieRequestModel.status == "approved",
            MovieRequestModel.status == "rejected",
        ))
        .order_by(MovieRequestModel.created_at.desc())
        .limit(20)
    )
    result = await uow._session.execute(query)
    requests = result.scalars().all()
    
    if not requests:
        await callback.message.edit_text(
            "📩 Ko'rib chiqilgan so'rovlar\n\nMa'lumot yo'q.",
            reply_markup=get_requests_keyboard(),
        )
        await callback.answer()
        return
    
    text = "📩 Ko'rib chiqilgan so'rovlar\n\n"
    for req in requests[:10]:
        status_icon = "✅" if req.status == "approved" else "❌"
        text += f"{status_icon} {req.title}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_requests_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "requests:stats")
async def callback_requests_stats(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Show request statistics."""
    from sqlalchemy import select, func
    from src.infrastructure.database.models.request import MovieRequestModel
    
    # Count by status
    query = select(
        MovieRequestModel.status,
        func.count(MovieRequestModel.id),
    ).group_by(MovieRequestModel.status)
    
    result = await uow._session.execute(query)
    counts = dict(result.all())
    
    pending = counts.get("pending", 0)
    approved = counts.get("approved", 0)
    rejected = counts.get("rejected", 0)
    total = pending + approved + rejected
    
    text = (
        "📊 So'rovlar statistikasi\n\n"
        f"📩 Jami: {total}\n"
        f"🆕 Kutilmoqda: {pending}\n"
        f"✅ Qabul qilingan: {approved}\n"
        f"❌ Rad etilgan: {rejected}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_requests_keyboard(),
    )
    await callback.answer()
