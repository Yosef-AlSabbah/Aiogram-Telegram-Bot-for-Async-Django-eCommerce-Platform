__all__ = ('router',)

from aiogram import Router

from .users import router as users_router

router = Router(name=__name__)

router.include_routers(
    users_router,
)
