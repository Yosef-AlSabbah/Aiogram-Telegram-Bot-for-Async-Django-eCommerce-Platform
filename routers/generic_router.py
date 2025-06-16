import aiogram.utils.markdown as md
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from api_client.openrouter_client import generate_customer_support_reply, clear_user_conversation, test_openrouter_connection

router = Router(name=__name__)


@router.message(Command('clear_chat', prefix='/'))
async def command_clear_chat(message: Message) -> None:
    """Command to clear the chat history for a user"""
    user_id = message.from_user.id
    await clear_user_conversation(user_id)
    await message.reply("Your conversation history has been cleared.")


@router.message(Command('test_ai', prefix='/'))
async def command_test_ai(message: Message) -> None:
    """Command to test the OpenRouter API connection"""
    # Only allow staff/admin to run this command
    if not message.from_user or message.from_user.id not in [123456789]:  # Replace with actual admin IDs
        await message.reply("This command is only available to administrators.")
        return

    await message.reply("Testing connection to OpenRouter API...")

    # Test the connection
    result = await test_openrouter_connection()

    if result["status"] == "success":
        models_text = "\n".join([f"• {m['id']} ({m['name']})" for m in result.get("available_models", [])])
        await message.reply(
            md.text(
                md.hbold("✅ Connection Successful"),
                md.text("The connection to OpenRouter API is working."),
                md.text("Available models:"),
                md.text(models_text if models_text else "No matching models found"),
                sep="\n"
            ),
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply(
            md.text(
                md.hbold("❌ Connection Failed"),
                md.text(f"Error: {result.get('message', 'Unknown error')}"),
                md.text("Please check your API key and network connection."),
                sep="\n"
            ),
            parse_mode=ParseMode.HTML
        )


@router.message(F.text)
async def generate_using_ai(message: Message):
    # Show typing indicator
    async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
    ):
        try:
            # Get user ID for session tracking
            user_id = message.from_user.id

            # Get AI response with user context
            ai_response = await generate_customer_support_reply(message.text, user_id=user_id)

            # Reply to user
            await message.reply(ai_response, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception(f"Error generating AI response: {str(e)}")
            await message.reply(
                md.hbold("❌ Error") + "\n\n" +
                f"I couldn't process your request",
                parse_mode=ParseMode.HTML,
            )
