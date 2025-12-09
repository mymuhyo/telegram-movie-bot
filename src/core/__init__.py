"""Core module exports."""

from src.core.config import Settings, get_settings, settings
from src.core.exceptions import (
    AccessDeniedError,
    BotException,
    DuplicateCodeError,
    EntityNotFoundError,
    MaintenanceModeError,
    MovieNotFoundError,
    NotAdminError,
    NotSuperAdminError,
    RateLimitError,
    SearchQueryTooShortError,
    SubscriptionRequiredError,
    UserBannedError,
    UserNotFoundError,
    ValidationError,
)
from src.core.logging import get_logger, log_context, setup_logging

__all__ = [
    # Config
    "Settings",
    "get_settings",
    "settings",
    # Logging
    "setup_logging",
    "get_logger",
    "log_context",
    # Exceptions
    "BotException",
    "EntityNotFoundError",
    "MovieNotFoundError",
    "UserNotFoundError",
    "AccessDeniedError",
    "UserBannedError",
    "NotAdminError",
    "NotSuperAdminError",
    "ValidationError",
    "DuplicateCodeError",
    "SearchQueryTooShortError",
    "RateLimitError",
    "MaintenanceModeError",
    "SubscriptionRequiredError",
]
