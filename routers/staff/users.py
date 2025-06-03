from enum import Enum

import aiogram.utils.markdown as md
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from api_client import UserClient
from routers.staff.utils.user_info import send_user_info
from routers.staff.utils.users import get_user_card
from utils.decorators import validate_command


router = Router(name=__name__)


class UserCallbackPrefix(str, Enum):
    INFO = "user_info_"


@router.message(Command('user', prefix='!'))
@validate_command(params=[{"name": "User ID", "type": int, "description": "User's ID"}], min_args=1, )
async def get_user(message: Message, command_args, *args, **kwargs):
    async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
    ):
        try:
            user_id = int(command_args[0])
        except ValueError:
            await message.answer(
                text=md.text(
                    md.hbold("Error:"),
                    md.text("User ID must be a number."),
                    f"Usage: {md.hcode('!user <user_id>')}",
                    sep='\n'
                ),
                parse_mode='HTML',
            )
            return

        await send_user_info(message, user_id)


@router.message(Command('users', prefix='!'))
@validate_command(
    params=[
        {"name": "search", "type": str, "description": "Optional query to search for users"},
        {"name": "ordering", "type": str, "description": "Page number for pagination"},
        {"name": "page_size", "type": int, "description": "Number of users per page"}
    ],
    min_args=0)
async def get_users(message: Message, command_args, *args, **kwargs):
    """
    Handler for the !users command.
    This function is called when a staff member sends the command.

    Usage: !users [search] [ordering] [page_size]
    """
    try:
        users = await UserClient.get_users(**kwargs)
        if not users:
            await message.answer(
                text=md.text(md.hbold("No users found."), sep='\n'),
                parse_mode=ParseMode.HTML
            )
            return

        for user in users:
            user_card = await get_user_card(user)
            await message.answer(**user_card)
    except Exception as e:
        await message.reply(
            text=md.text(
                md.hbold("Error retrieving users:"),
                md.hcode(str(e)),
                sep='\n'
            ),
            parse_mode=ParseMode.HTML
        )
