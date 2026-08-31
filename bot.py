import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database.database import init_db
from handlers.start import router
from handlers.profile import router as profile_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def main():

    logging.info("🚀 Запускаем FreelanceJob...")
    # Создаём таблицы
    await init_db()
    logging.info("База данных готова")

    bot = Bot(
        token=BOT_TOKEN
    )

    dp = Dispatcher()

    # Подключаем handlers
    dp.include_router(router)
    dp.include_router(profile_router)

    logging.info("🤖 Бот успешно запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())