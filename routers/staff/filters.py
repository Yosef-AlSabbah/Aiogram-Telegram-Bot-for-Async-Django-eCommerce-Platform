from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from api_client.auth_client import AuthClient


class IsStaff(BaseFilter):
    """Magic filter that checks if a user has staff privileges."""

    async def __call__(self, obj, **kwargs) -> bool:
        if isinstance(obj, Message):
            telegram_id = obj.from_user.id
        elif isinstance(obj, CallbackQuery):
            telegram_id = obj.from_user.id
        else:
            print('IsStaff Filter: Unsupported object type', type(obj))
            return False
        print('IsStaff Filter ', telegram_id)
        return await AuthClient.is_staff(str(telegram_id))
