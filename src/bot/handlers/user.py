"""User handlers for /start, /help, and movie codes."""
from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import get_movie_card_keyboard, get_subscription_keyboard
from src.core import MovieNotFoundError, get_logger
from src.infrastructure import UnitOfWork
from src.infrastructure.database.models.user import UserModel
from src.texts import messages

logger = get_logger(__name__)

router = Router(name="user")


async def check_user_subscription(bot: Bot, user_id: int, channel: str) -> bool:
    """Check if user is subscribed to channel.
    
    Args:
        bot: Telegram bot instance
        user_id: User's Telegram ID
        channel: Channel username (with @)
        
    Returns:
        True if subscribed or on error (don't block users on API issues)
    """
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.warning("subscription_check_failed", user_id=user_id, channel=channel, error=str(e))
        return True  # Don't block users on API errors


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    bot: Bot,
    uow: UnitOfWork,
    user: UserModel,
    user_created: bool,
) -> None:
    """Handle /start command."""
    # Check if user is banned
    if user.is_banned:
        from src.core.config import settings
        await message.answer(messages.USER_BANNED.format(admin=settings.admin_username))
        return

    # Check maintenance mode
    if await uow.settings.is_maintenance_mode():
        is_admin = await uow.admins.is_admin(message.from_user.id)
        if not is_admin:
            msg = await uow.settings.get_maintenance_message()
            await message.answer(messages.MAINTENANCE.format(message=msg))
            return

    # Check channel subscription
    if await uow.settings.is_channel_check_enabled():
        channel = await uow.settings.get_required_channel()
        if channel:
            is_subscribed = await check_user_subscription(bot, message.from_user.id, channel)
            if not is_subscribed:
                await message.answer(
                    messages.SUBSCRIBE_REQUIRED.format(channel=channel),
                    reply_markup=get_subscription_keyboard(channel),
                )
                return

    # Get channel for display
    channel = await uow.settings.get_required_channel() or "@YourChannel"

    # Send welcome message
    await message.answer(
        messages.WELCOME.format(channel=channel)
    )

    if user_created:
        logger.info("new_user_joined", user_id=user.telegram_id)


@router.message(Command("help"))
async def cmd_help(message: Message, uow: UnitOfWork) -> None:
    """Handle /help command."""
    channel = await uow.settings.get_required_channel() or "@YourChannel"
    from src.core.config import settings
    
    await message.answer(
        messages.HELP.format(
            channel=channel,
            admin=settings.admin_username,
        )
    )


@router.message(StateFilter(None), F.text.regexp(r"^\d+$"))
async def handle_movie_code(
    message: Message,
    bot: Bot,
    uow: UnitOfWork,
    user: UserModel,
) -> None:
    """Handle movie code request (only when NOT in FSM state)."""
    # Check if user is banned
    if user.is_banned:
        from src.core.config import settings
        await message.answer(messages.USER_BANNED.format(admin=settings.admin_username))
        return

    # Check maintenance mode
    if await uow.settings.is_maintenance_mode():
        is_admin = await uow.admins.is_admin(message.from_user.id)
        if not is_admin:
            msg = await uow.settings.get_maintenance_message()
            await message.answer(messages.MAINTENANCE.format(message=msg))
            return

    # Check channel subscription
    if await uow.settings.is_channel_check_enabled():
        channel = await uow.settings.get_required_channel()
        if channel:
            is_subscribed = await check_user_subscription(bot, message.from_user.id, channel)
            if not is_subscribed:
                await message.answer(
                    messages.SUBSCRIBE_REQUIRED.format(channel=channel),
                    reply_markup=get_subscription_keyboard(channel),
                )
                return

    code = int(message.text)
    
    # Get movie by code
    movie = await uow.movies.get_by_code(code)
    
    if not movie:
        # Get popular movies for suggestions
        popular = await uow.movies.get_popular(limit=3)
        suggestions = "\n".join([
            f"├── {m.code} — {m.title}" for m in popular[:-1]
        ])
        if popular:
            suggestions += f"\n└── {popular[-1].code} — {popular[-1].title}"
        
        channel = await uow.settings.get_required_channel() or "@YourChannel"
        
        await message.answer(
            messages.MOVIE_NOT_FOUND.format(
                code=code,
                suggestions=suggestions or "Kinolar mavjud emas",
                channel=channel,
            )
        )
        return

    # Format movie card with rich info if available
    if movie.year and movie.duration_minutes and movie.description:
        card = messages.MOVIE_CARD_RICH.format(
            title=movie.title,
            code=movie.code,
            year=movie.year,
            duration=movie.duration_minutes,
            downloads=movie.download_count,
            description=movie.description[:200] + "..." if len(movie.description) > 200 else movie.description,
        )
    elif movie.year and movie.duration_minutes:
        card = messages.MOVIE_CARD_ENHANCED.format(
            title=movie.title,
            code=movie.code,
            year=movie.year,
            duration=movie.duration_minutes,
            downloads=movie.download_count,
        )
    else:
        card = messages.MOVIE_CARD.format(
            title=movie.title,
            code=movie.code,
            downloads=movie.download_count,
        )

    # Check if part of series
    if movie.series_id and movie.series:
        series_movies = await uow.movies.get_by_series(movie.series_id)
        parts_list = []
        for sm in series_movies:
            marker = "(bu)" if sm.id == movie.id else "✅"
            parts_list.append(f"├── {sm.part_number}-qism: kod {sm.code} {marker}")
        
        if parts_list:
            parts_list[-1] = parts_list[-1].replace("├──", "└──")
            series_info = messages.SERIES_INFO.format(
                series_name=movie.series.name,
                parts_list="\n".join(parts_list),
            )
            card = f"🎬 {movie.series.name}\n\n📺 {movie.part_number}-qism: {movie.title}\n\n" + card.split("\n\n", 1)[1]
            card += f"\n\n{series_info}"

    # Send movie card with share button
    await message.answer(
        card,
        reply_markup=get_movie_card_keyboard(movie.code),
    )

    # Send video
    await message.answer_video(
        video=movie.file_id,
        caption=f"🎬 {movie.title}",
    )

    # Track download
    await uow.downloads.create_download(
        user_id=user.id,
        movie_id=movie.id,
        movie_code=movie.code,
        source="code",
    )
    await uow.movies.increment_downloads(movie.id)
    await uow.users.increment_downloads(user.id)

    logger.info(
        "movie_downloaded",
        user_id=user.telegram_id,
        movie_code=movie.code,
    )


@router.callback_query(F.data == "check_subscription")
async def callback_check_subscription(
    callback: CallbackQuery,
    bot: Bot,
    uow: UnitOfWork,
) -> None:
    """Handle subscription check callback."""
    channel = await uow.settings.get_required_channel()
    
    if not channel:
        await callback.answer(messages.SUBSCRIBE_SUCCESS, show_alert=True)
        await callback.message.delete()
        return
    
    is_subscribed = await check_user_subscription(bot, callback.from_user.id, channel)
    
    if is_subscribed:
        await callback.answer(messages.SUBSCRIBE_SUCCESS, show_alert=True)
        await callback.message.delete()
        # Show welcome message after successful subscription
        await callback.message.answer(
            messages.WELCOME.format(channel=channel)
        )
    else:
        await callback.answer(messages.SUBSCRIBE_FAIL, show_alert=True)


@router.callback_query(F.data.startswith("movie:"))
async def callback_movie_code(
    callback: CallbackQuery,
    uow: UnitOfWork,
    user: UserModel,
) -> None:
    """Handle movie code callback from search results."""
    code = int(callback.data.split(":")[1])
    
    # Get movie
    movie = await uow.movies.get_by_code(code)
    if not movie:
        await callback.answer(messages.NOT_FOUND, show_alert=True)
        return

    # Format movie card with rich info if available
    if movie.year and movie.duration_minutes and movie.description:
        card = messages.MOVIE_CARD_RICH.format(
            title=movie.title,
            code=movie.code,
            year=movie.year,
            duration=movie.duration_minutes,
            downloads=movie.download_count,
            description=movie.description[:200] + "..." if len(movie.description) > 200 else movie.description,
        )
    elif movie.year and movie.duration_minutes:
        card = messages.MOVIE_CARD_ENHANCED.format(
            title=movie.title,
            code=movie.code,
            year=movie.year,
            duration=movie.duration_minutes,
            downloads=movie.download_count,
        )
    else:
        card = messages.MOVIE_CARD.format(
            title=movie.title,
            code=movie.code,
            downloads=movie.download_count,
        )
    
    # Send movie card with share button
    await callback.message.answer(
        card,
        reply_markup=get_movie_card_keyboard(movie.code),
    )

    # Send video
    await callback.message.answer_video(
        video=movie.file_id,
        caption=f"🎬 {movie.title}",
    )

    # Track download
    await uow.downloads.create_download(
        user_id=user.id,
        movie_id=movie.id,
        movie_code=movie.code,
        source="search",
    )
    await uow.movies.increment_downloads(movie.id)
    await uow.users.increment_downloads(user.id)

    await callback.answer()


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery) -> None:
    """Handle cancel callback."""
    await callback.message.delete()
    await callback.answer(messages.CANCELLED)


@router.message(F.text)
async def handle_text_fallback(
    message: Message,
    uow: UnitOfWork,
) -> None:
    """Handle arbitrary text inputs (Smart Fallback)."""
    text = message.text.lower().strip()
    
    # Common greetings
    if text in ("salom", "assalomu alaykum", "start", "/start"):
         channel = await uow.settings.get_required_channel() or "@YourChannel"
         await message.answer(messages.WELCOME.format(channel=channel))
         return

    # If it looks like a search query (not just numbers, handled by other handler)
    if len(text) > 2:
        # Search by title
        results = await uow.movies.search(text, limit=5)
        if results:
            text_res = "🔎 Qidiruv natijalari:\n\n"
            for m in results:
                text_res += f"🎬 {m.title} — {m.code}\n"
            text_res += "\nKino olish uchun kodini yuboring."
            await message.answer(text_res)
            return

    await message.answer(messages.INVALID_INPUT)
