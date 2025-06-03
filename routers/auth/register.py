import aiogram.utils.markdown as md
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from api_client.auth_client import AuthClient
from api_client.exceptions.common import ApiClientError
from routers.auth.utils.commons import is_user_authenticated
from validators import user_validators as validators

router = Router(name=__name__)


# Define states for registration flow
class RegisterStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()
    waiting_for_phone = State()
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    confirm_registration = State()


@router.message(Command('register'))
async def register(message: Message, state: FSMContext):
    # Check if user is already authenticated
    if await is_user_authenticated(telegram_id=message.from_user.id):
        await message.reply(
            f"{md.hbold('You are already registered and logged in.')} {md.hitalic('Use /logout first if you want to register a new account.')}",
            parse_mode=ParseMode.HTML
        )
        return

    # User is not authenticated, start registration flow
    await message.reply(
        f"{md.hbold('Registration Process')}\n\n"
        f"Please enter your desired {md.hbold('username')}:\n\n"
        f"{md.hitalic('You can cancel registration at any time by typing /stop')}",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RegisterStates.waiting_for_username)


@router.message(Command('stop'), StateFilter(RegisterStates))
async def stop_registration(message: Message, state: FSMContext):
    # Clear the state
    await state.clear()

    # Inform the user
    await message.reply(
        f"{md.hbold('Registration process stopped.')}\n\n"
        f"You can start over with the /register command whenever you're ready.",
        parse_mode=ParseMode.HTML
    )


@router.message(RegisterStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext) -> None:
    username = message.text
    validation_result, validation_text = validators.validate_username(username)

    if not validation_result:
        await message.reply(
            f"{md.hbold('❌ Invalid username')}\n\n"
            f"{validation_text}\n\n"
            f"{md.hitalic('Please try another username.')}",
            parse_mode=ParseMode.HTML
        )
        return

    # Save valid username to state
    await state.update_data(username=username)

    # Ask for password
    await message.reply(
        f"{md.hbold('Step 2 of 5')}\n\n"
        f"Please enter your {md.hbold('password')}:\n\n"
        f"{md.hitalic('For security, I recommend deleting your password message after sending it.')}",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RegisterStates.waiting_for_password)


@router.message(RegisterStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text

    # Validate password using the validator function
    validation_result = validators.validate_password(password)
    if validation_result is not True:
        await message.reply(
            f"{md.hbold('❌ Invalid password')}\n\n"
            f"{validation_result}",
            parse_mode=ParseMode.HTML
        )
        return

    # Save valid password to state
    await state.update_data(password=password)

    # Ask for phone number
    await message.reply(
        f"{md.hbold('Step 3 of 5')}\n\n"
        f"Please enter your {md.hbold('phone number')} (format: +1234567890):",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RegisterStates.waiting_for_phone)


@router.message(RegisterStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text

    # Validate phone using the validator function
    validation_result = validators.validate_phone(phone)
    if validation_result is not True:
        await message.reply(
            f"{md.hbold('❌ Invalid phone number')}\n\n"
            f"{validation_result}",
            parse_mode=ParseMode.HTML
        )
        return

    # Save valid phone to state
    await state.update_data(phone=phone)

    # Ask for first name
    await message.reply(
        f"{md.hbold('Step 4 of 5')}\n\n"
        f"Please enter your {md.hbold('first name')}:",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RegisterStates.waiting_for_first_name)


@router.message(RegisterStates.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    first_name = message.text

    # Validate first name using validator function
    validation_result = validators.validate_name(first_name)
    if validation_result is not True:
        await message.reply(
            f"{md.hbold('❌ Invalid first name')}\n\n"
            f"{validation_result}",
            parse_mode=ParseMode.HTML
        )
        return

    # Save valid first name to state
    await state.update_data(first_name=first_name)

    # Ask for last name
    await message.reply(
        f"{md.hbold('Step 5 of 5')}\n\n"
        f"Please enter your {md.hbold('last name')}:",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RegisterStates.waiting_for_last_name)


@router.message(RegisterStates.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    last_name = message.text

    # Validate last name using validator function
    validation_result = validators.validate_name(last_name)
    if validation_result is not True:
        await message.reply(
            f"{md.hbold('❌ Invalid last name')}\n\n"
            f"{validation_result}",
            parse_mode=ParseMode.HTML
        )
        return

    # Save valid last name to state
    await state.update_data(last_name=last_name)

    # Get all registration data from state
    user_data = await state.get_data()

    # Ask for confirmation
    await message.reply(
        f"{md.hbold('Registration Summary')}\n\n"
        f"{md.hbold('Username')}: {md.hcode(user_data['username'])}\n"
        f"{md.hbold('Phone')}: {md.hcode(user_data['phone'])}\n"
        f"{md.hbold('First Name')}: {md.hcode(user_data['first_name'])}\n"
        f"{md.hbold('Last Name')}: {md.hcode(user_data['last_name'])}\n\n"
        f"Please confirm your registration by typing {md.hbold('/confirm')} or cancel by typing {md.hbold('/cancel')}",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(RegisterStates.confirm_registration)


@router.message(Command('confirm'), StateFilter(RegisterStates.confirm_registration))
async def confirm_registration(message: Message, state: FSMContext):
    async with ChatActionSender.typing(
            bot=message.bot,
            chat_id=message.chat.id,
    ):
        # Get all registration data from state
        user_data = await state.get_data()

        # Clear state
        await state.clear()

        # Send processing message
        processing_msg = await message.reply("Processing your registration...")

        try:
            # Prepare registration data
            registration_data = {
                "username": user_data["username"],
                "password": user_data["password"],
                "phone": user_data["phone"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "telegram_id": str(message.from_user.id)
            }

            # Submit registration using AuthClient
            result = await AuthClient.register(user_data=registration_data)

            # Success message
            await processing_msg.delete()
            await message.reply(
                f"{md.hbold('✅ Registration successful!')}\n\n"
                f"Welcome, {md.hbold(user_data['first_name'])}! "
                f"Your account has been created.\n\n"
                f"You can now log in with the /login command.",
                parse_mode=ParseMode.HTML
            )

        except ApiClientError as e:
            await processing_msg.delete()
            error_message = f"{md.hbold('❌ Registration failed')}\n"
            if hasattr(e, "response_errors") and isinstance(e.response_errors, dict):
                resp = e.response_errors
                for field, error in resp.items():
                    error_text = error[0] if isinstance(error, list) and error else error
                    error_message += f"\n{md.hbold(field.replace('_', ' ').capitalize())}: {error_text}"
                error_message += (
                    f"\n\nPlease review the highlighted fields and try again with /register."
                )
            else:
                error_message += f"\n\n{str(e)}\n\nPlease try again with /register"
            await message.reply(
                error_message,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            # Handle unexpected errors
            await processing_msg.delete()
            await message.reply(
                f"{md.hbold('❌ An unexpected error occurred')}\n\n"
                f"Please try again later with /register",
                parse_mode=ParseMode.HTML
            )
