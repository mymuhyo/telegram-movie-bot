"""Settings and Admin user management handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.keyboards import get_back_to_admin_keyboard
from src.core import get_logger
from src.infrastructure import UnitOfWork

logger = get_logger(__name__)

router = Router(name="settings_admins")


# ========== SETTINGS ==========


class SettingsStates(StatesGroup):
    """States for settings."""

    waiting_channel = State()
    waiting_maintenance_message = State()


def get_settings_keyboard(channel_check: bool, maintenance: bool) -> InlineKeyboardMarkup:
    """Get settings keyboard."""
    channel_icon = "✅" if channel_check else "❌"
    maint_icon = "✅" if maintenance else "❌"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{channel_icon} Kanal tekshiruvi",
                    callback_data="settings:toggle_channel",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📢 Kanal sozlash",
                    callback_data="settings:set_channel",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{maint_icon} Texnik ishlar rejimi",
                    callback_data="settings:toggle_maintenance",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📝 Texnik xabar",
                    callback_data="settings:set_maint_message",
                ),
            ],
            [
                InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin:panel"),
            ],
        ]
    )


@router.callback_query(F.data == "admin:settings")
async def callback_settings_menu(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_super_admin: bool,
) -> None:
    """Show settings menu."""
    if not is_super_admin:
        await callback.answer("❌ Bu funksiya faqat super admin uchun!", show_alert=True)
        return

    channel_check = await uow.settings.is_channel_check_enabled()
    maintenance = await uow.settings.is_maintenance_mode()
    channel = await uow.settings.get_required_channel()
    maint_msg = await uow.settings.get_maintenance_message()

    text = (
        "⚙️ Bot sozlamalari\n\n"
        f"📢 Kanal tekshiruvi: {'✅' if channel_check else '❌'}\n"
        f"📢 Majburiy kanal: {channel or 'Sozlanmagan'}\n\n"
        f"🔧 Texnik ishlar: {'✅' if maintenance else '❌'}\n"
        f"📝 Xabar: {maint_msg[:50]}..."
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_settings_keyboard(channel_check, maintenance),
    )
    await callback.answer()


@router.callback_query(F.data == "settings:toggle_channel")
async def callback_toggle_channel(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_super_admin: bool,
) -> None:
    """Toggle channel check."""
    if not is_super_admin:
        await callback.answer("❌ Super admin emas!", show_alert=True)
        return

    current = await uow.settings.is_channel_check_enabled()
    await uow.settings.set("channel_check_enabled", not current)
    await uow.commit()
    status = "❌ O'chirildi" if current else "✅ Yoqildi"
    await callback.answer(f"{status}!")
    await callback_settings_menu(callback, uow, is_super_admin)


@router.callback_query(F.data == "settings:set_channel")
async def callback_set_channel(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start setting required channel."""
    await callback.message.edit_text(
        "📢 Majburiy kanalni kiriting:\n\nMasalan: @YourChannel",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(SettingsStates.waiting_channel)
    await callback.answer()


@router.message(SettingsStates.waiting_channel)
async def handle_channel_input(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle channel input."""
    channel = message.text.strip()

    if not channel.startswith("@"):
        await message.answer("❌ Kanal @ bilan boshlanishi kerak!")
        return

    await uow.settings.set("required_channel", channel)
    await uow.commit()
    await state.clear()

    await message.answer(
        f"✅ Majburiy kanal o'rnatildi: {channel}",
        reply_markup=get_back_to_admin_keyboard(),
    )
    logger.info("channel_set", channel=channel)


@router.callback_query(F.data == "settings:toggle_maintenance")
async def callback_toggle_maintenance(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_super_admin: bool,
) -> None:
    """Toggle maintenance mode."""
    if not is_super_admin:
        await callback.answer("❌ Super admin emas!", show_alert=True)
        return

    current = await uow.settings.is_maintenance_mode()
    await uow.settings.set("maintenance_mode", not current)
    await uow.commit()
    status = "❌ O'chirildi" if current else "✅ Yoqildi"
    await callback.answer(f"{status}!")
    await callback_settings_menu(callback, uow, is_super_admin)


@router.callback_query(F.data == "settings:set_maint_message")
async def callback_set_maint_message(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start setting maintenance message."""
    await callback.message.edit_text(
        "📝 Texnik ishlar xabarini kiriting:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(SettingsStates.waiting_maintenance_message)
    await callback.answer()


@router.message(SettingsStates.waiting_maintenance_message)
async def handle_maint_message_input(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle maintenance message input."""
    msg = message.text.strip()

    await uow.settings.set("maintenance_message", msg)
    await uow.commit()
    await state.clear()

    await message.answer(
        "✅ Texnik ishlar xabari o'rnatildi!",
        reply_markup=get_back_to_admin_keyboard(),
    )


# ========== ADMIN MANAGEMENT ==========


class AdminStates(StatesGroup):
    """States for admin management."""

    waiting_telegram_id = State()
    waiting_username = State()


def get_admins_keyboard() -> InlineKeyboardMarkup:
    """Get admins management keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Adminlar ro'yxati", callback_data="admins:list"),
            ],
            [
                InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="admins:add"),
            ],
            [
                InlineKeyboardButton(text="➖ Admin o'chirish", callback_data="admins:remove"),
            ],
            [
                InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin:panel"),
            ],
        ]
    )


@router.callback_query(F.data == "admin:admins")
async def callback_admins_menu(
    callback: CallbackQuery,
    is_super_admin: bool,
) -> None:
    """Show admins menu."""
    if not is_super_admin:
        await callback.answer("❌ Bu funksiya faqat super admin uchun!", show_alert=True)
        return

    await callback.message.edit_text(
        "👤 Adminlar boshqaruvi\n\nTanlang:",
        reply_markup=get_admins_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admins:list")
async def callback_admins_list(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Show list of admins."""
    admins = await uow.admins.get_all_admins()

    if not admins:
        await callback.message.edit_text(
            "👤 Adminlar ro'yxati\n\nAdminlar yo'q!",
            reply_markup=get_admins_keyboard(),
        )
        await callback.answer()
        return

    text = "👤 Adminlar ro'yxati\n\n"
    for i, admin in enumerate(admins, 1):
        role = "👑 Super" if admin.is_super else "🔧 Admin"
        text += f"{i}. {role} @{admin.username or 'noname'} ({admin.telegram_id})\n"

    await callback.message.edit_text(
        text,
        reply_markup=get_admins_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admins:add")
async def callback_add_admin(
    callback: CallbackQuery,
    state: FSMContext,
    is_super_admin: bool,
) -> None:
    """Start adding admin."""
    if not is_super_admin:
        await callback.answer("❌ Super admin emas!", show_alert=True)
        return

    await callback.message.edit_text(
        "➕ Yangi admin qo'shish\n\nTelegram ID kiriting:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(AdminStates.waiting_telegram_id)
    await callback.answer()


@router.message(AdminStates.waiting_telegram_id)
async def handle_admin_id(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle admin telegram ID input."""
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    telegram_id = int(message.text)

    # Check if already admin
    existing = await uow.admins.get_by_telegram_id(telegram_id)
    if existing:
        await message.answer("❌ Bu foydalanuvchi allaqachon admin!")
        return

    await state.update_data(telegram_id=telegram_id)
    await message.answer(
        "📝 Username kiriting (@ siz):",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(AdminStates.waiting_username)


@router.message(AdminStates.waiting_username)
async def handle_admin_username(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle admin username input and create admin."""
    username = message.text.strip().replace("@", "")
    data = await state.get_data()

    await uow.admins.create_admin(
        telegram_id=data["telegram_id"],
        username=username,
        is_super=False,
    )
    await uow.commit()
    await state.clear()

    await message.answer(
        f"✅ Admin qo'shildi!\n\n👤 @{username}\n🆔 {data['telegram_id']}",
        reply_markup=get_admins_keyboard(),
    )
    logger.info("admin_added", telegram_id=data["telegram_id"], username=username)


@router.callback_query(F.data == "admins:remove")
async def callback_remove_admin(
    callback: CallbackQuery,
    uow: UnitOfWork,
    is_super_admin: bool,
) -> None:
    """Show admins to remove."""
    if not is_super_admin:
        await callback.answer("❌ Super admin emas!", show_alert=True)
        return

    admins = await uow.admins.get_all_admins()
    admins = [a for a in admins if not a.is_super]  # Can't remove super admins

    if not admins:
        await callback.message.edit_text(
            "❌ O'chirish uchun admin yo'q!",
            reply_markup=get_admins_keyboard(),
        )
        await callback.answer()
        return

    keyboard = []
    for admin in admins:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"❌ @{admin.username or admin.telegram_id}",
                    callback_data=f"admins:delete:{admin.telegram_id}",
                )
            ]
        )
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin:admins")])

    await callback.message.edit_text(
        "➖ O'chirish uchun tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admins:delete:"))
async def callback_delete_admin(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Delete an admin."""
    telegram_id = int(callback.data.split(":")[2])

    admin = await uow.admins.get_by_telegram_id(telegram_id)
    if admin and not admin.is_super:
        await uow.admins.soft_delete(admin.id)
        await uow.commit()
        await callback.answer("✅ Admin o'chirildi!", show_alert=True)
        logger.info("admin_removed", telegram_id=telegram_id)
    else:
        await callback.answer("❌ O'chirib bo'lmadi!", show_alert=True)

    # Refresh list
    await callback_admins_menu(callback, True)
