"""User request handlers."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.core import get_logger
from src.infrastructure import UnitOfWork
from src.infrastructure.database.models.request import MovieRequestModel
from src.infrastructure.database.models.user import UserModel
from src.texts import messages

logger = get_logger(__name__)

router = Router(name="request")


class RequestStates(StatesGroup):
    """States for movie request."""

    waiting_title = State()


@router.message(Command("request"))
async def cmd_request(
    message: Message,
    state: FSMContext,
    user: UserModel,
) -> None:
    """Handle /request command."""
    # Check if user is banned
    if user.is_banned:
        from src.core.config import settings

        await message.answer(messages.USER_BANNED.format(admin=settings.admin_username))
        return

    await message.answer(messages.REQUEST_START)
    await state.set_state(RequestStates.waiting_title)


@router.message(RequestStates.waiting_title)
async def handle_request_title(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
    user: UserModel,
) -> None:
    """Handle movie title input."""
    title = message.text.strip()
    if len(title) < 2:
        await message.answer("❌ Nom juda qisqa!")
        return

    # Create request
    request = MovieRequestModel(
        user_id=user.id,
        movie_title=title,
    )
    await uow.requests.create(request)
    await uow.commit()  # Commit explicitly if needed, or rely on UOW context if applicable (but here we are in handler)
    # Wait, usually repository create methods don't commit?
    # Let's check BaseRepository.create. It usually just adds to session.
    # The middleware usually handles commit if no exception.
    # But for safety we might want to check.
    # Assuming middleware handles commit for successful handlers.

    await message.answer(messages.REQUEST_SUBMITTED)
    await state.clear()

    logger.info("movie_requested", user_id=user.telegram_id, title=title)


@router.message(Command("myrequest"))
async def cmd_myrequest(
    message: Message,
    uow: UnitOfWork,
    user: UserModel,
) -> None:
    """Handle /myrequest command."""
    # Check if user is banned
    if user.is_banned:
        from src.core.config import settings

        await message.answer(messages.USER_BANNED.format(admin=settings.admin_username))
        return

    # specific query for user requests
    from sqlalchemy import select

    query = (
        select(MovieRequestModel)
        .where(MovieRequestModel.user_id == user.id)
        .order_by(MovieRequestModel.created_at.desc())
        .limit(10)
    )
    result = await uow._session.execute(query)
    requests = result.scalars().all()

    if not requests:
        await message.answer(messages.REQUEST_EMPTY)
        return

    text = ""
    for req in requests:
        status_icon = {
            "pending": "🆕",
            "approved": "✅",
            "rejected": "❌",
            "added": "✅",
        }.get(req.status, "❓")

        status_text = {
            "pending": "Kutilmoqda",
            "approved": "Qabul qilindi",
            "rejected": "Rad etildi",
            "added": "Qo'shildi",
        }.get(req.status, req.status)

        text += f"{status_icon} {req.movie_title} — {status_text}\n"

    await message.answer(messages.REQUEST_LIST.format(requests=text))
