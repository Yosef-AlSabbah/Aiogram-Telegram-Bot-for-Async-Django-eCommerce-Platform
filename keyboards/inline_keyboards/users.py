from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def staff_user_show_keyboard(user_info) -> InlineKeyboardMarkup:
    pass


def generate_user_keyboard(user_id: int, phone: str) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for user information display.

    :param phone: User phone number.
    :param user_id: User id.
    :return: InlineKeyboardMarkup object with user-related buttons.
    """
    builder = InlineKeyboardBuilder()

    # Add user information buttons
    builder.button(
        text=f"ℹ️ More Info",
        callback_data=f"user_info_{user_id}",
    )
    builder.button(
        text="📞 Call User",
        url=f"tel:{phone}",
    )

    builder.adjust(2)
    return builder.as_markup()
