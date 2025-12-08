"""Admin movie handlers with FSM for adding/editing/deleting movies."""
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import get_back_to_admin_keyboard
from src.core import get_logger
from src.infrastructure import UnitOfWork
from src.infrastructure.database.models.admin import AdminModel
from src.infrastructure.database.models.movie import MovieModel
from src.texts import messages

logger = get_logger(__name__)

router = Router(name="admin_movies")


class AddMovieStates(StatesGroup):
    """States for adding a movie."""
    waiting_video = State()
    waiting_title = State()
    waiting_code = State()


class EditMovieStates(StatesGroup):
    """States for editing a movie."""
    waiting_code = State()
    waiting_choice = State()
    waiting_new_title = State()
    waiting_new_code = State()
    waiting_new_video = State()


class DeleteMovieStates(StatesGroup):
    """States for deleting a movie."""
    waiting_code = State()
    confirm = State()


# ========== ADD MOVIE ==========

@router.callback_query(F.data == "admin:add_movie")
async def callback_add_movie_start(
    callback: CallbackQuery,
    state: FSMContext,
    is_admin: bool,
) -> None:
    """Start add movie flow."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        messages.ADD_MOVIE_VIDEO,
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(AddMovieStates.waiting_video)
    await callback.answer()


@router.message(AddMovieStates.waiting_video, F.video)
async def handle_add_movie_video(
    message: Message,
    state: FSMContext,
) -> None:
    """Handle video upload - only accepts forwarded videos from channel."""
    # Check if video is forwarded (has forward_origin or forward_from_chat)
    is_forwarded = (
        message.forward_origin is not None or 
        message.forward_from_chat is not None or
        message.forward_from is not None
    )
    
    if not is_forwarded:
        await message.answer(
            "⚠️ Faqat kanaldan forward qilingan video qabul qilinadi!\n\n"
            "💡 Qanday qilish kerak:\n"
            "1. Videoni avval shaxsiy kanalingizga yuklang\n"
            "2. Kanaldan bu chatga forward qiling\n\n"
            "📌 Sabab: Telegram Bot API 50 MB cheklovi",
            reply_markup=get_back_to_admin_keyboard(),
        )
        return
    
    file_id = message.video.file_id
    await state.update_data(file_id=file_id)
    
    await message.answer(
        messages.ADD_MOVIE_TITLE,
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(AddMovieStates.waiting_title)


@router.message(AddMovieStates.waiting_video)
async def handle_add_movie_video_invalid(message: Message) -> None:
    """Handle invalid video upload."""
    await message.answer(
        "❌ Iltimos, kanaldan video forward qiling!\n\n"
        "💡 Videoni avval kanalingizga yuklang, keyin forward qiling."
    )


@router.message(AddMovieStates.waiting_title)
async def handle_add_movie_title(
    message: Message,
    state: FSMContext,
) -> None:
    """Handle movie title input."""
    title = message.text.strip()
    if len(title) < 2:
        await message.answer("❌ Nom juda qisqa! Kamida 2 ta belgi kiriting.")
        return
    
    await state.update_data(title=title)
    await message.answer(
        messages.ADD_MOVIE_CODE,
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(AddMovieStates.waiting_code)


@router.message(AddMovieStates.waiting_code)
async def handle_add_movie_code(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
    admin: AdminModel,
) -> None:
    """Handle movie code input and save movie."""
    # Validate code
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    
    code = int(message.text)
    
    # Check if code exists
    existing = await uow.movies.get_by_code(code)
    if existing:
        await message.answer(
            messages.ADD_MOVIE_CODE_EXISTS.format(title=existing.title)
        )
        return
    
    # Get stored data
    data = await state.get_data()
    
    # Create movie
    movie = MovieModel(
        code=code,
        title=data["title"],
        file_id=data["file_id"],
        added_by=admin.telegram_id,
    )
    
    await uow.movies.create(movie)
    await state.clear()
    
    await message.answer(
        messages.ADD_MOVIE_SUCCESS.format(
            title=data["title"],
            code=code,
        ),
        reply_markup=get_back_to_admin_keyboard(),
    )
    
    logger.info(
        "movie_added",
        code=code,
        title=data["title"],
        admin_id=admin.telegram_id,
    )


# ========== DELETE MOVIE ==========

@router.callback_query(F.data == "admin:delete_movie")
async def callback_delete_movie_start(
    callback: CallbackQuery,
    state: FSMContext,
    is_admin: bool,
) -> None:
    """Start delete movie flow."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        messages.DELETE_MOVIE_ASK_CODE,
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(DeleteMovieStates.waiting_code)
    await callback.answer()


@router.message(DeleteMovieStates.waiting_code)
async def handle_delete_movie_code(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle movie code for deletion."""
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    
    code = int(message.text)
    movie = await uow.movies.get_by_code(code)
    
    if not movie:
        await message.answer(f"❌ Kod {code} topilmadi!")
        return
    
    await state.update_data(code=code, movie_id=str(movie.id))
    
    from src.bot.keyboards.admin import get_confirm_keyboard
    await message.answer(
        messages.DELETE_MOVIE_CONFIRM.format(
            title=movie.title,
            code=movie.code,
        ),
        reply_markup=get_confirm_keyboard("delete_movie", str(code)),
    )
    await state.set_state(DeleteMovieStates.confirm)


@router.callback_query(F.data.startswith("confirm:delete_movie:"))
async def callback_confirm_delete(
    callback: CallbackQuery,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Confirm movie deletion."""
    code = int(callback.data.split(":")[2])
    
    movie = await uow.movies.get_by_code(code)
    if movie:
        await uow.movies.soft_delete(movie.id)
        await callback.message.edit_text(
            messages.DELETE_MOVIE_SUCCESS,
            reply_markup=get_back_to_admin_keyboard(),
        )
        logger.info("movie_deleted", code=code)
    else:
        await callback.message.edit_text(
            messages.NOT_FOUND,
            reply_markup=get_back_to_admin_keyboard(),
        )
    
    await state.clear()
    await callback.answer()


# ========== CANCEL ==========

@router.callback_query(F.data == "admin:panel", AddMovieStates)
@router.callback_query(F.data == "admin:panel", DeleteMovieStates)
@router.callback_query(F.data == "admin:panel", EditMovieStates)
async def callback_cancel_state(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Cancel current admin operation."""
    await state.clear()
    # Let the main admin handler take over


# ========== EDIT MOVIE ==========

@router.callback_query(F.data == "admin:edit_movie")
async def callback_edit_movie_start(
    callback: CallbackQuery,
    state: FSMContext,
    is_admin: bool,
) -> None:
    """Start edit movie flow."""
    if not is_admin:
        await callback.answer(messages.ADMIN_ONLY, show_alert=True)
        return

    await callback.message.edit_text(
        messages.EDIT_MOVIE_ASK_CODE,
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(EditMovieStates.waiting_code)
    await callback.answer()


@router.message(EditMovieStates.waiting_code)
async def handle_edit_movie_code(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle movie code for editing."""
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    
    code = int(message.text)
    movie = await uow.movies.get_by_code(code)
    
    if not movie:
        await message.answer(f"❌ Kod {code} topilmadi!")
        return
    
    await state.update_data(code=code, movie_id=str(movie.id))
    
    from src.bot.keyboards.admin import get_movie_edit_keyboard
    await message.answer(
        messages.EDIT_MOVIE_INFO.format(
            title=movie.title,
            code=movie.code,
            downloads=movie.download_count,
        ),
        reply_markup=get_movie_edit_keyboard(code),
    )
    await state.set_state(EditMovieStates.waiting_choice)


@router.callback_query(F.data.startswith("edit:title:"), EditMovieStates.waiting_choice)
async def callback_edit_title(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start editing title."""
    await callback.message.edit_text(
        "📝 Yangi nomni kiriting:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(EditMovieStates.waiting_new_title)
    await callback.answer()


@router.message(EditMovieStates.waiting_new_title)
async def handle_new_title(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle new title input."""
    new_title = message.text.strip()
    if len(new_title) < 2:
        await message.answer("❌ Nom juda qisqa!")
        return
    
    data = await state.get_data()
    code = data["code"]
    
    movie = await uow.movies.get_by_code(code)
    if movie:
        movie.title = new_title
        await uow.movies.update(movie)
        
        await message.answer(
            messages.EDIT_MOVIE_SUCCESS,
            reply_markup=get_back_to_admin_keyboard(),
        )
        logger.info("movie_edited", code=code, field="title", new_value=new_title)
    
    await state.clear()


@router.callback_query(F.data.startswith("edit:code:"), EditMovieStates.waiting_choice)
async def callback_edit_code(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start editing code."""
    await callback.message.edit_text(
        "🔢 Yangi kodni kiriting:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(EditMovieStates.waiting_new_code)
    await callback.answer()


@router.message(EditMovieStates.waiting_new_code)
async def handle_new_code(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle new code input."""
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    
    new_code = int(message.text)
    data = await state.get_data()
    old_code = data["code"]
    
    # Check if new code exists
    existing = await uow.movies.get_by_code(new_code)
    if existing:
        await message.answer(
            messages.ADD_MOVIE_CODE_EXISTS.format(title=existing.title)
        )
        return
    
    movie = await uow.movies.get_by_code(old_code)
    if movie:
        movie.code = new_code
        await uow.movies.update(movie)
        
        await message.answer(
            messages.EDIT_MOVIE_SUCCESS,
            reply_markup=get_back_to_admin_keyboard(),
        )
        logger.info("movie_edited", old_code=old_code, new_code=new_code)
    
    await state.clear()


@router.callback_query(F.data.startswith("edit:video:"), EditMovieStates.waiting_choice)
async def callback_edit_video(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Start editing video."""
    await callback.message.edit_text(
        "🎬 Yangi video yuboring:",
        reply_markup=get_back_to_admin_keyboard(),
    )
    await state.set_state(EditMovieStates.waiting_new_video)
    await callback.answer()


@router.message(EditMovieStates.waiting_new_video, F.video)
async def handle_new_video(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle new video upload."""
    new_file_id = message.video.file_id
    data = await state.get_data()
    code = data["code"]
    
    movie = await uow.movies.get_by_code(code)
    if movie:
        movie.file_id = new_file_id
        await uow.movies.update(movie)
        
        await message.answer(
            messages.EDIT_MOVIE_SUCCESS,
            reply_markup=get_back_to_admin_keyboard(),
        )
        logger.info("movie_edited", code=code, field="video")
    
    await state.clear()


@router.message(EditMovieStates.waiting_new_video)
async def handle_new_video_invalid(message: Message) -> None:
    """Handle invalid video upload."""
    await message.answer("❌ Iltimos, video yuboring!")

