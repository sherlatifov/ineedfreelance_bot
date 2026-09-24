from aiogram import Router

from handlers.client.jobs.create import router as create_job_router
from handlers.client.jobs.my_jobs import router as client_jobs


router = Router()

router.include_router(create_job_router)
router.include_router(client_jobs)