from aiogram import Router

from .main import router as main_router
from .navigation import router as navigation_router



router = Router()


router.include_router(main_router)
router.include_router(navigation_router)
