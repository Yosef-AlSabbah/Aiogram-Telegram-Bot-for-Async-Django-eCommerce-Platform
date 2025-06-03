import aiogram.utils.markdown as md
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from api_client.openrouter_client import generate_customer_support_reply

router = Router(name=__name__)


@router.message(F.text)
async def generate_using_ai(message: Message):
    # Show typing indicator
    async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
    ):
        try:
            # Get AI response
            ai_response = await generate_customer_support_reply(message.text)

            # Reply to user
            await message.reply(ai_response, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await message.reply(
                md.hbold("❌ Error") + "\n\n" +
                f"I couldn't process your request",
                parse_mode=ParseMode.HTML,
            )
