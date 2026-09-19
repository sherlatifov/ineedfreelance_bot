from aiogram import Router

from handlers.client.jobs.create import router as create_job_router


router = Router()

router.include_router(create_job_router)