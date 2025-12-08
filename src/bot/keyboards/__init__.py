"""Keyboards package."""
from src.bot.keyboards.admin import (
    get_admin_panel_keyboard,
    get_back_to_admin_keyboard,
    get_broadcast_confirm_keyboard,
    get_broadcast_keyboard,
    get_confirm_keyboard,
    get_maintenance_keyboard,
    get_movie_edit_keyboard,
    get_pagination_keyboard,
    get_statistics_keyboard,
)
from src.bot.keyboards.user import (
    get_cancel_keyboard,
    get_movie_card_keyboard,
    get_search_results_keyboard,
    get_subscription_keyboard,
)

__all__ = [
    # User
    "get_subscription_keyboard",
    "get_search_results_keyboard",
    "get_cancel_keyboard",
    "get_movie_card_keyboard",
    # Admin
    "get_admin_panel_keyboard",
    "get_back_to_admin_keyboard",
    "get_movie_edit_keyboard",
    "get_confirm_keyboard",
    "get_pagination_keyboard",
    "get_maintenance_keyboard",
    "get_broadcast_keyboard",
    "get_broadcast_confirm_keyboard",
    "get_statistics_keyboard",
]
