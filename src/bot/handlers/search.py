"""Search handlers."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from src.bot.keyboards import get_cancel_keyboard, get_search_results_keyboard
from src.core import get_logger
from src.core.config import settings
from src.infrastructure import UnitOfWork
from src.texts import messages

logger = get_logger(__name__)

router = Router(name="search")


class SearchStates(StatesGroup):
    """Search FSM states."""

    waiting_query = State()


@router.message(Command("search", "qidirish"))
async def cmd_search(
    message: Message,
    state: FSMContext,
) -> None:
    """Handle /search command."""
    # Check if query provided inline: /search avatar
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        # Direct search
        await process_search(message, args[1], message.bot.get("uow"))
        return

    # Ask for search query
    await message.answer(
        messages.SEARCH_PROMPT,
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(SearchStates.waiting_query)


@router.message(SearchStates.waiting_query)
async def handle_search_query(
    message: Message,
    state: FSMContext,
    uow: UnitOfWork,
) -> None:
    """Handle search query input."""
    await process_search(message, message.text, uow)
    await state.clear()


async def process_search(
    message: Message,
    query: str,
    uow: UnitOfWork,
) -> None:
    """Process search query."""
    # Validate query length
    if len(query) < settings.search_min_chars:
        await message.answer(messages.SEARCH_TOO_SHORT)
        return

    # Check if searching by year
    if query.isdigit() and len(query) == 4:
        year = int(query)
        if 1900 <= year <= 2100:
            results = await uow.movies.search_by_year(year, limit=settings.search_max_results)
        else:
            results = await uow.movies.search(query, limit=settings.search_max_results)
    else:
        results = await uow.movies.search(query, limit=settings.search_max_results)

    if not results:
        await message.answer(
            messages.SEARCH_NOT_FOUND.format(
                query=query,
                channel="@YourChannel",
            )
        )
        return

    # Format results
    results_text = "\n".join(
        [f"{i+1}. 🎬 {m.title} (kod: {m.code})" for i, m in enumerate(results)]
    )

    # Create keyboard with movie buttons
    keyboard_data = [(m.code, m.title) for m in results]

    await message.answer(
        messages.SEARCH_RESULTS.format(
            query=query,
            results=results_text,
        ),
        reply_markup=get_search_results_keyboard(keyboard_data),
    )

    logger.info(
        "search_performed",
        query=query,
        results_count=len(results),
    )
