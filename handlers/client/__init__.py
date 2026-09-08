from aiogram import Router

from .profile import router as profile_router


router = Router()

router.include_router(profile_router)