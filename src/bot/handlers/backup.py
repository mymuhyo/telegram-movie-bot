"""Backup handlers."""
import io
from datetime import datetime
from aiogram import F, Router
from aiogram.types import CallbackQuery, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.keyboards import get_back_to_admin_keyboard
from src.bot.loader import bot
from src.core import get_logger
from src.core.config import settings
from src.infrastructure import UnitOfWork
from src.texts import messages

logger = get_logger(__name__)

router = Router(name="backup")


def get_backup_keyboard() -> InlineKeyboardMarkup:
    """Get backup menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📥 Zaxira olish (JSON)", callback_data="backup:json"),
            ],
            [
                InlineKeyboardButton(text="📊 Excel export", callback_data="backup:excel"),
            ],
            [
                InlineKeyboardButton(text="📤 Kanalga yuborish", callback_data="backup:channel"),
            ],
            [
                InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin:panel"),
            ],
        ]
    )


@router.callback_query(F.data == "admin:backup")
async def callback_backup_menu(
    callback: CallbackQuery,
    is_admin: bool,
) -> None:
    """Show backup menu."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        "💾 Zaxira nusxalari\n\nTanlang:",
        reply_markup=get_backup_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "backup:json")
async def callback_backup_json(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Create JSON backup."""
    import json
    
    # Gather all data
    movies = await uow.movies.get_all(limit=10000)
    users = await uow.users.get_all(limit=100000)
    
    backup_data = {
        "created_at": datetime.now().isoformat(),
        "movies": [
            {
                "code": m.code,
                "title": m.title,
                "file_id": m.file_id,
                "download_count": m.download_count,
            }
            for m in movies
        ],
        "users_count": len(users),
        "movies_count": len(movies),
    }
    
    json_content = json.dumps(backup_data, ensure_ascii=False, indent=2)
    
    file = BufferedInputFile(
        file=json_content.encode('utf-8'),
        filename=f"backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
    )
    
    await callback.message.answer_document(
        document=file,
        caption=f"📥 Zaxira nusxasi\n\n🎬 Kinolar: {len(movies)}\n👤 Foydalanuvchilar: {len(users)}",
    )
    await callback.answer("✅ Zaxira tayyor!")
    logger.info("backup_created", format="json")


@router.callback_query(F.data == "backup:excel")
async def callback_backup_excel(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Create Excel backup."""
    from openpyxl import Workbook
    
    movies = await uow.movies.get_all(limit=10000)
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Kinolar"
    
    # Headers
    ws.append(["Kod", "Nomi", "Yuklanishlar", "File ID"])
    
    # Data
    for movie in movies:
        ws.append([movie.code, movie.title, movie.download_count, movie.file_id])
    
    # Save to bytes
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    file = BufferedInputFile(
        file=output.getvalue(),
        filename=f"movies_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    )
    
    await callback.message.answer_document(
        document=file,
        caption=f"📊 Excel export\n\n🎬 Jami: {len(movies)} ta kino",
    )
    await callback.answer("✅ Excel tayyor!")
    logger.info("backup_created", format="excel")


@router.callback_query(F.data == "backup:channel")
async def callback_backup_channel(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Send backup to backup channel."""
    if not settings.backup_channel_id:
        await callback.answer("❌ Backup kanal sozlanmagan!", show_alert=True)
        return
    
    import json
    
    movies = await uow.movies.get_all(limit=10000)
    users_count = await uow.users.get_total_count()
    
    backup_data = {
        "created_at": datetime.now().isoformat(),
        "movies": [
            {
                "code": m.code,
                "title": m.title,
                "file_id": m.file_id,
                "download_count": m.download_count,
            }
            for m in movies
        ],
    }
    
    json_content = json.dumps(backup_data, ensure_ascii=False, indent=2)
    
    file = BufferedInputFile(
        file=json_content.encode('utf-8'),
        filename=f"backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
    )
    
    try:
        await bot.send_document(
            chat_id=settings.backup_channel_id,
            document=file,
            caption=(
                f"💾 Avtomatik zaxira nusxasi\n\n"
                f"🎬 Kinolar: {len(movies)}\n"
                f"👤 Foydalanuvchilar: {users_count}\n"
                f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ),
        )
        await callback.answer("✅ Kanalga yuborildi!", show_alert=True)
        logger.info("backup_sent_to_channel")
    except Exception as e:
        await callback.answer(f"❌ Xatolik: {str(e)[:50]}", show_alert=True)
        logger.error("backup_channel_failed", error=str(e))
