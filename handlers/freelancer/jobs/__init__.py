from aiogram import Router

from .jobs import router as jobs_router

router = Router()

# Подключаем каждый раздел.
router.include_router(jobs_router)