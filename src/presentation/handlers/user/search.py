"""Search handlers with filters."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from src.application.dto import SearchFilters, SearchResult
from src.application.services import MovieService
from src.presentation.keyboards.user.search import SearchKeyboard
from src.presentation.views.search_view import SearchView

router = Router(name="search")


class SearchStates(StatesGroup):
    """Search FSM states."""

    waiting_query = State()
    selecting_filters = State()


# Store user filters in FSM data
DEFAULT_FILTERS = SearchFilters()


@router.message(F.text.in_(["/search", "/qidirish", "/qidir"]))
async def cmd_search(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Handle /search command.

    Shows search help and quick options.
    """
    if not message.from_user:
        return

    # Reset filters
    await state.update_data(filters=DEFAULT_FILTERS.__dict__)
    await state.set_state(SearchStates.waiting_query)

    text = SearchView.format_quick_search_help()
    keyboard = SearchKeyboard.get_quick_search_keyboard()

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.message(SearchStates.waiting_query)
async def process_search_query(
    message: Message,
    state: FSMContext,
    movie_service: FromDishka[MovieService],
) -> None:
    """
    Process search query in search state.

    Args:
        message: User's search query
        state: FSM context
        movie_service: Movie service
    """
    if not message.text or not message.from_user:
        return

    query = message.text.strip()

    # Get stored filters
    data = await state.get_data()
    filters_dict = data.get("filters", {})
    filters = SearchFilters(**filters_dict)
    filters.query = query

    # Store current query
    await state.update_data(query=query, filters=filters.__dict__)

    # Perform search
    result = await movie_service.search_advanced(
        query=query,
        filters=filters,
        page=1,
        per_page=10,
    )

    if not result.movies:
        text = SearchView.format_no_results(query, filters)
        keyboard = SearchKeyboard.get_no_results_keyboard(query)
    else:
        text = SearchView.format_search_results(result)
        keyboard = SearchKeyboard.get_search_results_keyboard(result)

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("search:page:"))
async def search_pagination(
    callback: CallbackQuery,
    state: FSMContext,
    movie_service: FromDishka[MovieService],
) -> None:
    """Handle search results pagination."""
    await callback.answer()

    if not callback.data or not callback.message:
        return

    page = int(callback.data.split(":")[-1])

    # Get stored query and filters
    data = await state.get_data()
    query = data.get("query", "")
    filters_dict = data.get("filters", {})
    filters = SearchFilters(**filters_dict)

    if not query:
        await callback.answer("❌ Qidiruv topilmadi", show_alert=True)
        return

    # Perform search with new page
    result = await movie_service.search_advanced(
        query=query,
        filters=filters,
        page=page,
        per_page=10,
    )

    text = SearchView.format_search_results(result)
    keyboard = SearchKeyboard.get_search_results_keyboard(result)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "search:filters")
async def show_filters(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Show filters menu."""
    await callback.answer()

    if not callback.message:
        return

    # Get current filters
    data = await state.get_data()
    filters_dict = data.get("filters", {})
    filters = SearchFilters(**filters_dict)

    await state.set_state(SearchStates.selecting_filters)

    text = SearchView.format_filters_menu(filters)
    keyboard = SearchKeyboard.get_filters_keyboard(filters)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "search:clear")
async def clear_filters(
    callback: CallbackQuery,
    state: FSMContext,
    movie_service: FromDishka[MovieService],
) -> None:
    """Clear all filters and re-search."""
    await callback.answer("✅ Filtrlar tozalandi")

    if not callback.message:
        return

    data = await state.get_data()
    query = data.get("query", "")

    # Reset filters but keep query
    new_filters = SearchFilters(query=query)
    await state.update_data(filters=new_filters.__dict__)

    if query:
        result = await movie_service.search_advanced(
            query=query,
            filters=new_filters,
            page=1,
            per_page=10,
        )

        text = SearchView.format_search_results(result)
        keyboard = SearchKeyboard.get_search_results_keyboard(result)
    else:
        text = SearchView.format_quick_search_help()
        keyboard = SearchKeyboard.get_quick_search_keyboard()

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "filter:year")
async def show_year_filter(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Show year filter options."""
    await callback.answer()

    if not callback.message:
        return

    data = await state.get_data()
    filters_dict = data.get("filters", {})
    current_year = filters_dict.get("year")

    text = SearchView.format_year_filter()
    keyboard = SearchKeyboard.get_year_filter_keyboard(current_year)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("filter:year:"))
async def set_year_filter(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Set year filter value."""
    await callback.answer()

    if not callback.data or not callback.message:
        return

    value = callback.data.split(":")[-1]

    data = await state.get_data()
    filters_dict = data.get("filters", {})

    if value == "all":
        filters_dict["year"] = None
        filters_dict["year_from"] = None
        filters_dict["year_to"] = None
    elif value == "<2010":
        filters_dict["year"] = None
        filters_dict["year_from"] = None
        filters_dict["year_to"] = 2009
    elif "-" in value:
        years = value.split("-")
        filters_dict["year"] = None
        filters_dict["year_from"] = int(years[0])
        filters_dict["year_to"] = int(years[1])
    else:
        filters_dict["year"] = int(value)
        filters_dict["year_from"] = None
        filters_dict["year_to"] = None

    await state.update_data(filters=filters_dict)

    # Return to filters menu
    filters = SearchFilters(**filters_dict)
    text = SearchView.format_filters_menu(filters)
    keyboard = SearchKeyboard.get_filters_keyboard(filters)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "filter:quality")
async def show_quality_filter(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Show quality filter options."""
    await callback.answer()

    if not callback.message:
        return

    data = await state.get_data()
    filters_dict = data.get("filters", {})
    current_quality = filters_dict.get("quality")

    text = SearchView.format_quality_filter()
    keyboard = SearchKeyboard.get_quality_filter_keyboard(current_quality)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("filter:quality:"))
async def set_quality_filter(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Set quality filter value."""
    await callback.answer()

    if not callback.data or not callback.message:
        return

    value = callback.data.split(":")[-1]

    data = await state.get_data()
    filters_dict = data.get("filters", {})

    if value == "all":
        filters_dict["quality"] = None
    else:
        filters_dict["quality"] = value

    await state.update_data(filters=filters_dict)

    # Return to filters menu
    filters = SearchFilters(**filters_dict)
    text = SearchView.format_filters_menu(filters)
    keyboard = SearchKeyboard.get_filters_keyboard(filters)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "filter:rating")
async def show_rating_filter(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Show rating filter options."""
    await callback.answer()

    if not callback.message:
        return

    data = await state.get_data()
    filters_dict = data.get("filters", {})
    current_rating = filters_dict.get("min_rating")

    text = SearchView.format_rating_filter()
    keyboard = SearchKeyboard.get_rating_filter_keyboard(current_rating)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("filter:rating:"))
async def set_rating_filter(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Set rating filter value."""
    await callback.answer()

    if not callback.data or not callback.message:
        return

    value = callback.data.split(":")[-1]

    data = await state.get_data()
    filters_dict = data.get("filters", {})

    if value == "all":
        filters_dict["min_rating"] = None
    else:
        filters_dict["min_rating"] = float(value)

    await state.update_data(filters=filters_dict)

    # Return to filters menu
    filters = SearchFilters(**filters_dict)
    text = SearchView.format_filters_menu(filters)
    keyboard = SearchKeyboard.get_filters_keyboard(filters)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "filter:series")
async def toggle_series_filter(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Toggle series-only filter."""
    await callback.answer()

    if not callback.message:
        return

    data = await state.get_data()
    filters_dict = data.get("filters", {})

    # Toggle series_only
    filters_dict["series_only"] = not filters_dict.get("series_only", False)

    await state.update_data(filters=filters_dict)

    # Return to filters menu
    filters = SearchFilters(**filters_dict)
    text = SearchView.format_filters_menu(filters)
    keyboard = SearchKeyboard.get_filters_keyboard(filters)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "filter:sort")
async def show_sort_options(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Show sort options."""
    await callback.answer()

    if not callback.message:
        return

    data = await state.get_data()
    filters_dict = data.get("filters", {})
    current_sort = filters_dict.get("sort_by", "relevance")

    text = SearchView.format_sort_options()
    keyboard = SearchKeyboard.get_sort_keyboard(current_sort)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data.startswith("filter:sort:"))
async def set_sort_option(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Set sort option."""
    await callback.answer()

    if not callback.data or not callback.message:
        return

    value = callback.data.split(":")[-1]

    data = await state.get_data()
    filters_dict = data.get("filters", {})
    filters_dict["sort_by"] = value

    await state.update_data(filters=filters_dict)

    # Return to filters menu
    filters = SearchFilters(**filters_dict)
    text = SearchView.format_filters_menu(filters)
    keyboard = SearchKeyboard.get_filters_keyboard(filters)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "filter:apply")
async def apply_filters(
    callback: CallbackQuery,
    state: FSMContext,
    movie_service: FromDishka[MovieService],
) -> None:
    """Apply filters and search."""
    await callback.answer("✅ Filtrlar qo'llandi")

    if not callback.message:
        return

    data = await state.get_data()
    query = data.get("query", "")
    filters_dict = data.get("filters", {})
    filters = SearchFilters(**filters_dict)

    await state.set_state(SearchStates.waiting_query)

    if query:
        result = await movie_service.search_advanced(
            query=query,
            filters=filters,
            page=1,
            per_page=10,
        )

        if not result.movies:
            text = SearchView.format_no_results(query, filters)
            keyboard = SearchKeyboard.get_no_results_keyboard(query)
        else:
            text = SearchView.format_search_results(result)
            keyboard = SearchKeyboard.get_search_results_keyboard(result)
    else:
        text = SearchView.format_quick_search_help()
        keyboard = SearchKeyboard.get_quick_search_keyboard()

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )


@router.callback_query(F.data == "filter:cancel")
async def cancel_filters(
    callback: CallbackQuery,
    state: FSMContext,
    movie_service: FromDishka[MovieService],
) -> None:
    """Cancel filter selection and return to results."""
    await callback.answer()

    if not callback.message:
        return

    data = await state.get_data()
    query = data.get("query", "")
    filters_dict = data.get("filters", {})
    filters = SearchFilters(**filters_dict)

    await state.set_state(SearchStates.waiting_query)

    if query:
        result = await movie_service.search_advanced(
            query=query,
            filters=filters,
            page=1,
            per_page=10,
        )

        text = SearchView.format_search_results(result)
        keyboard = SearchKeyboard.get_search_results_keyboard(result)
    else:
        text = SearchView.format_quick_search_help()
        keyboard = SearchKeyboard.get_quick_search_keyboard()

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="MarkdownV2",
    )
