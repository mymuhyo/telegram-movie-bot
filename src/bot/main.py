"""Bot main entry point."""

import asyncio

from aiogram import Bot

# Import handlers
from src.bot.handlers import admin_router, user_router
from src.bot.loader import bot, dp, redis

# Import middlewares
from src.bot.middlewares import (
    DatabaseMiddleware,
    LoggingMiddleware,
    ThrottlingMiddleware,
    UserMiddleware,
)
from src.core import get_logger, setup_logging
from src.infrastructure import UnitOfWork
from src.infrastructure.database import async_session_factory, close_db

logger = get_logger(__name__)


async def on_startup(bot: Bot) -> None:
    """Called when bot starts."""
    logger.info("Bot starting up...")

    # Create UoW factory
    def uow_factory() -> UnitOfWork:
        # Pass redis only if it exists
        return UnitOfWork(async_session_factory, redis if redis else None)

    # Create super admin if not exists
    from src.core.config import settings

    async with uow_factory() as uow:
        admin = await uow.admins.get_by_telegram_id(settings.super_admin_id)
        if not admin:
            await uow.admins.create_admin(
                telegram_id=settings.super_admin_id,
                username="super_admin",
                is_super=True,
            )
            await uow.commit()
            logger.info("Super admin created", admin_id=settings.super_admin_id)

    # Register middlewares
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.outer_middleware(DatabaseMiddleware(uow_factory))
    dp.update.outer_middleware(UserMiddleware())
    dp.message.middleware(ThrottlingMiddleware())

    # Register routers
    dp.include_router(admin_router)
    dp.include_router(user_router)

    logger.info("Bot started successfully!")


async def on_shutdown(bot: Bot) -> None:
    """Called when bot shuts down."""
    logger.info("Bot shutting down...")
    if redis:
        await redis.aclose()
    await close_db()
    logger.info("Bot stopped.")


async def main() -> None:
    """Main function to run the bot."""
    # Setup logging
    setup_logging()

    # Register startup/shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Start polling
    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
