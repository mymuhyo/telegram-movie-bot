"""User keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.texts import buttons


def get_subscription_keyboard(channel: str) -> InlineKeyboardMarkup:
    """Get subscription check keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=channel,
                    url=f"https://t.me/{channel.lstrip('@')}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=buttons.BTN_CHECK_SUBSCRIPTION,
                    callback_data="check_subscription",
                )
            ],
        ]
    )


def get_search_results_keyboard(
    results: list[tuple[int, str]],  # [(code, title), ...]
) -> InlineKeyboardMarkup:
    """Get inline keyboard for search results."""
    keyboard = []
    for code, title in results:
        # Truncate title if too long
        display_title = title[:30] + "..." if len(title) > 30 else title
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📥 {code} — {display_title}",
                    callback_data=f"movie:{code}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text=buttons.BTN_CANCEL,
                callback_data="cancel",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=buttons.BTN_CANCEL,
                    callback_data="cancel",
                )
            ]
        ]
    )


def get_movie_card_keyboard(code: int) -> InlineKeyboardMarkup:
    """Get inline keyboard for movie card with share button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=buttons.BTN_SHARE_MOVIE,
                    switch_inline_query=str(code),
                ),
            ],
        ]
    )
