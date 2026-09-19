from aiogram import Router

from handlers.freelancer.jobs import router as jobs_router


router = Router()

router.include_router(jobs_router)