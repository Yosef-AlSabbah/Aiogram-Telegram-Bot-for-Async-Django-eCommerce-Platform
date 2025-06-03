__all__ = ('router',)

from aiogram import Router

from .auth import router as auth_router
from .commons import router as commons_router
from .generic_router import router as generic_router
from .handlers import router as handlers_router
from .staff import router as staff_router

router = Router(name=__name__)

router.include_routers(
    auth_router,
    commons_router,
    handlers_router,
    staff_router,
    generic_router,
)
