import aiogram.utils.markdown as md
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from api_client.auth_client import AuthClient
from api_client.exceptions.common import ApiClientError
from routers.auth.utils.commons import is_user_authenticated

router = Router(name=__name__)


# Define states for login flow
class LoginStates(StatesGroup):
    waiting_for_username_or_password = State()
    waiting_for_password = State()


@router.message(Command('login'))
async def login(message: Message, state: FSMContext):
    # Check if user is already authenticated
    if await is_user_authenticated(telegram_id=message.from_user.id):
        await message.reply(
            f"{md.hbold('You are already logged in.')} {md.hitalic('Use /logout to log out first.')}",
            parse_mode="HTML"
        )
        return

    # User is not authenticated, start login flow
    await message.reply(
        f"{md.hbold('Login Process')}\n\n"
        f"Please enter your username or phone number:",
        parse_mode="HTML"
    )
    await state.set_state(LoginStates.waiting_for_username_or_password)


@router.message(LoginStates.waiting_for_username_or_password)
async def process_username_or_phone_number(message: Message, state: FSMContext):
    # Save username to state
    await state.update_data(username=message.text)

    # Ask for password
    await message.reply(
        "Please enter your password:\n\n"
        f"{md.hitalic('For security, I recommend deleting your password message after sending it.')}",
        parse_mode="HTML"
    )
    await state.set_state(LoginStates.waiting_for_password)


@router.message(LoginStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
    ):
        # Get username from state
        user_data = await state.get_data()
        username = user_data.get("username")
        password = message.text

        # Clear state
        await state.clear()

        # Send processing message
        processing_msg = await message.reply("Processing your login...")

        try:
            # Prepare credentials for login
            credentials = {
                "username": username,
                "password": password,
                "telegram_id": str(message.from_user.id)
            }

            # Create token using AuthClient
            token_data = await AuthClient.create_token(credentials)
            username = token_data.get('user', 'Known User')
            device_limit_info = token_data.get('data', {}).get('device_limit_info', None)
            # Success message
            await processing_msg.delete()

            # Prepare device limit message if available
            device_limit_msg = ""
            if device_limit_info:
                device_limit_msg = f"\n\n{md.hitalic('Device Information:')}\n{md.code(device_limit_info)}"

            await message.reply(
                f"{md.hbold('✅ Login successful!')}\n\n"
                f"Welcome back, {md.hbold(username)}! "
                f"You are now authenticated and can use all features.{device_limit_msg}",
                parse_mode="HTML"
            )

        except ApiClientError as e:
            # Handle authentication error
            await processing_msg.delete()
            await message.reply(
                f"{md.hbold('❌ Login failed')}\n\n"
                f"Error: {e}\n\n"
                f"Please try again with /login",
                parse_mode="HTML"
            )
        except Exception as e:
            # Handle unexpected errors
            await processing_msg.delete()
            await message.reply(
                f"{md.hbold('❌ An unexpected error occurred')}\n\n"
                f"Please try again later with /login",
                parse_mode="HTML"
            )
