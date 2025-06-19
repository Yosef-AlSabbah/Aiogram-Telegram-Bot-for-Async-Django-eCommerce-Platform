from aiogram.types import Message, InlineKeyboardMarkup
from typing import Optional

async def send_message_with_optional_photo(
    message: Message,
    text: str,
    photo_url: Optional[str],
    reply_markup: Optional[InlineKeyboardMarkup] = None
):
    """
    Sends a message with a photo if a URL is provided, otherwise sends a text-only message.
    """
    if photo_url:
        await message.answer_photo(photo=photo_url, caption=text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)

