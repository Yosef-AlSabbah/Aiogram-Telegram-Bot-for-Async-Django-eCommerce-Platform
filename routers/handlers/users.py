from aiogram import Router, F
from aiogram.types import CallbackQuery

from routers.staff.users import UserCallbackPrefix
from routers.staff.utils.user_info import send_user_info

router = Router(name=__name__)


@router.callback_query(F.data.startswith(UserCallbackPrefix.INFO))
async def process_user_info_callback(callback: CallbackQuery):
    # Extract user ID from the callback data
    try:
         user_id = int(callback.data.split("_")[-1])
    except (ValueError, IndexError):
        await callback.answer("Invalid user ID in callback data.", show_alert=True)
        return

    # Acknowledge the callback
    await callback.answer()
    # Use callback.message as the target for the reply
    if callback.message:
        await send_user_info(callback.message, user_id)


