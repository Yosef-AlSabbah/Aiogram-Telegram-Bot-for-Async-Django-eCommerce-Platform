__all__ = ('router',)

from aiogram import Router

from .login import router as login_router
from .logout import router as logout_router
from .register import router as register_router

router = Router(name=__name__)

router.include_routers(
    login_router,
    logout_router,
    register_router,
)
