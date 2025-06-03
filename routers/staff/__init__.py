__all__ = ('router',)

from aiogram import Router

from .commons import router as commons_router
from .filters import IsStaff
from .users import router as users_router

router = Router(name=__name__)

router.message.filter(IsStaff())

router.include_routers(
    users_router,
    commons_router,
)
