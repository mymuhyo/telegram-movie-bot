"""Handlers package."""
from aiogram import Router

from src.bot.handlers.admin import router as admin_router
from src.bot.handlers.admin_movies import router as admin_movies_router
from src.bot.handlers.backup import router as backup_router
from src.bot.handlers.broadcast import router as broadcast_router
from src.bot.handlers.logs_requests import router as logs_requests_router
from src.bot.handlers.request import router as request_router
from src.bot.handlers.search import router as search_router
from src.bot.handlers.series import router as series_router
from src.bot.handlers.settings_admins import router as settings_admins_router
from src.bot.handlers.user import router as user_router

# Create main routers that include all sub-routers
user_router.include_router(request_router)
user_router.include_router(search_router)
admin_router.include_router(admin_movies_router)
admin_router.include_router(broadcast_router)
admin_router.include_router(series_router)
admin_router.include_router(backup_router)
admin_router.include_router(logs_requests_router)
admin_router.include_router(settings_admins_router)

__all__ = [
    "user_router",
    "admin_router",
]
