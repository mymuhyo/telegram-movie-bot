"""Series management handlers."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.keyboards import get_back_to_admin_keyboard
from src.core import get_logger
from src.infrastructure import UnitOfWork
from src.infrastructure.database.models.series import SeriesModel
from src.texts import buttons, messages

logger = get_logger(__name__)

router = Router(name="series")


class SeriesStates(StatesGroup):
    """States for series management."""

    waiting_name = State()
    waiting_description = State()
    add_movie_code = State()
    add_movie_part = State()


def get_series_keyboard() -> InlineKeyboardMarkup:
    """Get series menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=buttons.BTN_NEW_SERIES, callback_data="series:new"),
            ],
            [
                InlineKeyboardButton(text="📋 Seriallar ro'yxati", callback_data="series:list"),
            ],
            [
                InlineKeyboardButton(text=buttons.BTN_ADD_PARTS, callback_data="series:add_parts"),
            ],
            [
                InlineKeyboardButton(text=buttons.BTN_ADMIN_PANEL, callback_data="admin:panel"),
            ],
        ]
    )


@router.callback_query(F.data == "admin:series")
async def callback_series_menu(
    callback: CallbackQuery,
    is_admin: bool,
) -> None:
    """Show series menu."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        "📺 Seriallar boshqaruvi\n\nTanlang:",
        reply_markup=get_series_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "series:new")
async def callback_new_series(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start creating new series."""
    await callback.message.edit_text(
        "📺 Yangi serial yaratish\n\nSerial nomini kiriting:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(SeriesStates.waiting_name)
    await callback.answer()


@router.message(SeriesStates.waiting_name)
async def handle_series_name(
    message: Message,
    state: FSMContext,
) -> None:
    """Handle series name input."""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("❌ Nom juda qisqa!")
        return

    await state.update_data(name=name)
    await message.answer(
        "📝 Tavsif kiriting (ixtiyoriy, /skip):",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(SeriesStates.waiting_description)


@router.message(SeriesStates.waiting_description)
async def handle_series_description(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle series description input."""
    description = None if message.text == "/skip" else message.text.strip()

    data = await state.get_data()

    series = SeriesModel(
        name=data["name"],
        description=description,
    )
    await uow.series.create(series)
    await state.clear()

    await message.answer(
        f"✅ Serial yaratildi!\n\n📺 {data['name']}\n\nEndi kinolarni qo'shishingiz mumkin.",
        reply_markup=get_series_keyboard(),
    )
    logger.info("series_created", name=data["name"])


@router.callback_query(F.data == "series:list")
async def callback_series_list(
    callback: CallbackQuery,
    uow: UnitOfWork,
) -> None:
    """Show series list."""
    series_list = await uow.series.get_all(limit=20)

    if not series_list:
        await callback.message.edit_text(
            "📺 Seriallar ro'yxati\n\nSeriallar mavjud emas.",
            reply_markup=get_series_keyboard(),
        )
        await callback.answer()
        return

    text = "📺 Seriallar ro'yxati\n\n"
    for i, s in enumerate(series_list, 1):
        movies_count = len(s.movies) if hasattr(s, "movies") else 0
        text += f"{i}. {s.name} ({movies_count} qism)\n"

    await callback.message.edit_text(
        text,
        reply_markup=get_series_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "series:add_parts")
async def callback_add_parts(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start adding movie to series."""
    await callback.message.edit_text(
        "🎬 Serialga kino qo'shish\n\nKino kodini kiriting:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(SeriesStates.add_movie_code)
    await callback.answer()


@router.message(SeriesStates.add_movie_code)
async def handle_add_movie_code(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle movie code for adding to series."""
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    code = int(message.text)
    movie = await uow.movies.get_by_code(code)

    if not movie:
        await message.answer(f"❌ Kod {code} topilmadi!")
        return

    await state.update_data(movie_code=code, movie_id=str(movie.id))

    # Show series list for selection
    series_list = await uow.series.get_all(limit=20)

    if not series_list:
        await message.answer(
            "❌ Avval serial yarating!",
            reply_markup=get_series_keyboard(),
        )
        await state.clear()
        return

    keyboard = []
    for s in series_list:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=s.name,
                    callback_data=f"series:select:{s.id}",
                )
            ]
        )
    keyboard.append([InlineKeyboardButton(text=buttons.BTN_CANCEL, callback_data="admin:series")])

    await message.answer(
        f"📽 {movie.title}\n\nQaysi serialga qo'shmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data.startswith("series:select:"))
async def callback_select_series(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Handle series selection."""
    series_id = callback.data.split(":")[2]
    await state.update_data(series_id=series_id)

    await callback.message.edit_text(
        "🔢 Qism raqamini kiriting (masalan: 1, 2, 3):",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(SeriesStates.add_movie_part)
    await callback.answer()


@router.message(SeriesStates.add_movie_part)
async def handle_add_movie_part(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle part number input."""
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    part_number = int(message.text)
    data = await state.get_data()

    from uuid import UUID

    movie = await uow.movies.get_by_code(data["movie_code"])

    if movie:
        movie.series_id = UUID(data["series_id"])
        movie.part_number = part_number
        await uow.movies.update(movie)

        await message.answer(
            f"✅ Kino serialga qo'shildi!\n\n📽 {movie.title}\n🔢 {part_number}-qism",
            reply_markup=get_series_keyboard(),
        )
        logger.info("movie_added_to_series", code=data["movie_code"], part=part_number)

    await state.clear()


# Add series repository
