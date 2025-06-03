import aiogram.utils.markdown as md
from aiogram.enums import ParseMode

from keyboards.inline_keyboards.users import generate_user_keyboard


async def get_user_card(user):
    """
    Helper function to format user information into a card-like structure.
    This can be used for inline keyboards or detailed user views.
    """
    return {
        'text': md.text(
            md.hbold("User Information:"),
            md.text(md.hbold("ID:"), user.id),
            md.text(md.hbold("Full Name:"), f"{user.first_name} {user.last_name}"),
            md.text(md.hbold("Phone:"), user.phone),
            md.text(md.hbold("Balance:"), user.balance),
            sep='\n'
        ),
        'reply_markup': generate_user_keyboard(user.id, user.phone),
        'parse_mode': ParseMode.HTML
    }
