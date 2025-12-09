"""Admin keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.texts import buttons


def get_admin_panel_keyboard(is_super_admin: bool = False) -> InlineKeyboardMarkup:
    """Get main admin panel keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(text=buttons.BTN_ADD_MOVIE, callback_data="admin:add_movie"),
            InlineKeyboardButton(text=buttons.BTN_MOVIES_LIST, callback_data="admin:movies"),
        ],
        [
            InlineKeyboardButton(text=buttons.BTN_EDIT_MOVIE, callback_data="admin:edit_movie"),
            InlineKeyboardButton(text=buttons.BTN_DELETE_MOVIE, callback_data="admin:delete_movie"),
        ],
        [
            InlineKeyboardButton(text=buttons.BTN_SERIES, callback_data="admin:series"),
            InlineKeyboardButton(text=buttons.BTN_STATISTICS, callback_data="admin:stats"),
        ],
        [
            InlineKeyboardButton(text=buttons.BTN_LOGS, callback_data="admin:logs"),
            InlineKeyboardButton(text=buttons.BTN_BROADCAST, callback_data="admin:broadcast"),
        ],
        [
            InlineKeyboardButton(text=buttons.BTN_MAINTENANCE, callback_data="admin:maintenance"),
            InlineKeyboardButton(text=buttons.BTN_REQUESTS, callback_data="admin:requests"),
        ],
        [
            InlineKeyboardButton(text=buttons.BTN_BACKUP, callback_data="admin:backup"),
            InlineKeyboardButton(text=buttons.BTN_SETTINGS, callback_data="admin:settings"),
        ],
    ]

    # Add admin management for super admin only
    if is_super_admin:
        keyboard.append(
            [
                InlineKeyboardButton(text=buttons.BTN_ADMINS, callback_data="admin:admins"),
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    """Get back to admin panel keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=buttons.BTN_ADMIN_PANEL,
                    callback_data="admin:panel",
                )
            ]
        ]
    )


def get_movie_edit_keyboard(code: int) -> InlineKeyboardMarkup:
    """Get movie edit options keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=buttons.BTN_EDIT_TITLE,
                    callback_data=f"edit:title:{code}",
                ),
                InlineKeyboardButton(
                    text=buttons.BTN_EDIT_CODE,
                    callback_data=f"edit:code:{code}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=buttons.BTN_EDIT_VIDEO,
                    callback_data=f"edit:video:{code}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=buttons.BTN_CANCEL,
                    callback_data="admin:panel",
                )
            ],
        ]
    )


def get_confirm_keyboard(action: str, entity_id: str) -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=buttons.BTN_YES,
                    callback_data=f"confirm:{action}:{entity_id}",
                ),
                InlineKeyboardButton(
                    text=buttons.BTN_NO,
                    callback_data="admin:panel",
                ),
            ],
        ]
    )


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str,
) -> InlineKeyboardMarkup:
    """Get pagination keyboard."""
    buttons_row = []

    if current_page > 1:
        buttons_row.append(
            InlineKeyboardButton(
                text=buttons.BTN_PREV,
                callback_data=f"{callback_prefix}:page:{current_page - 1}",
            )
        )

    buttons_row.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}",
            callback_data="noop",
        )
    )

    if current_page < total_pages:
        buttons_row.append(
            InlineKeyboardButton(
                text=buttons.BTN_NEXT,
                callback_data=f"{callback_prefix}:page:{current_page + 1}",
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons_row,
            [
                InlineKeyboardButton(
                    text=buttons.BTN_ADMIN_PANEL,
                    callback_data="admin:panel",
                )
            ],
        ]
    )


def get_maintenance_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    """Get maintenance mode keyboard."""
    toggle_text = buttons.BTN_TOGGLE_OFF if is_enabled else buttons.BTN_TOGGLE_ON

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data="maintenance:toggle",
                ),
                InlineKeyboardButton(
                    text=buttons.BTN_EDIT_MESSAGE,
                    callback_data="maintenance:edit_message",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=buttons.BTN_ADMIN_PANEL,
                    callback_data="admin:panel",
                )
            ],
        ]
    )


def get_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Get broadcast menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=buttons.BTN_CUSTOM_MESSAGE,
                    callback_data="broadcast:custom",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=buttons.BTN_WEEKLY_REPORT,
                    callback_data="broadcast:weekly",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=buttons.BTN_ADMIN_PANEL,
                    callback_data="admin:panel",
                )
            ],
        ]
    )


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Get broadcast confirmation keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=buttons.BTN_SEND,
                    callback_data="broadcast:send",
                ),
                InlineKeyboardButton(
                    text=buttons.BTN_CANCEL,
                    callback_data="admin:broadcast",
                ),
            ],
        ]
    )


def get_statistics_keyboard() -> InlineKeyboardMarkup:
    """Get statistics keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=buttons.BTN_REFRESH,
                    callback_data="admin:stats",
                ),
                InlineKeyboardButton(
                    text=buttons.BTN_EXPORT_CSV,
                    callback_data="stats:export",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=buttons.BTN_ADMIN_PANEL,
                    callback_data="admin:panel",
                )
            ],
        ]
    )
