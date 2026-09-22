import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database.database import init_db
from database.seed import seed_categories

from handlers.start import router as start_router
from handlers.mode import router as mode_router
from handlers.client import router as client_router
from handlers.freelancer import router as freelancer_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

async def main():

    logging.info("🚀 Запуск FreelanceJob...")

    await init_db()
    await seed_categories()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(mode_router)
    dp.include_router(client_router)
    dp.include_router(freelancer_router)

    logging.info("🤖 Бот успешно запущен")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())