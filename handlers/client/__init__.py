from aiogram import Router

from .profile import router as profile_router
from .jobs import router as jobs_router

router = Router()

router.include_router(profile_router)
router.include_router(jobs_router)