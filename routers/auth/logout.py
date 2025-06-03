import aiogram.utils.markdown as md
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types.message import Message

from api_client.auth_client import AuthClient
from routers.auth.utils.commons import is_user_authenticated

router = Router(name=__name__)


@router.message(Command('logout'))
async def logout(message: Message):
    """
    Handle the /logout command to log out the user.

    This function sends a message to the user indicating that they have been logged out.
    """
    user_authenticated = await is_user_authenticated(telegram_id=message.from_user.id)
    if not user_authenticated:
        await message.reply(
            text="You are not logged in. Use /login to log in first."
        )
        return

    await AuthClient.destroy_token(telegram_id=message.from_user.id)

    await message.reply(
        text=md.text(
            md.hbold("Logout Successful"),
            "\n\n",
            md.text("You have been logged out successfully."),
            "\n",
            md.text("Use ", md.code("/login"), " to log in again."),
        ),
        parse_mode=ParseMode.HTML
    )
