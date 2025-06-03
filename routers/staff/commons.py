from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name=__name__)


@router.message(Command('help', prefix='!'))
async def get_help(message: Message):
    await message.answer(
        text=(
            "Available commands:\n"
            "!users - Get the list of users\n"
            "!help - Get this help message\n"
        )
    )
