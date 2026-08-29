import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv


# Загружаем переменные окружения
load_dotenv()

# Получаем токен
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден")


# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Создаём Bot и Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# /start
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Добро пожаловать в FreelanceHub!\n\n"
        "Здесь заказчики смогут публиковать задания,\n"
        "а фрилансеры — находить работу.\n\n"
        "🚀 Пока мы только начинаем."
    )


# /test
@dp.message(Command("test"))
async def test_handler(message: Message):
    await message.answer(
        "✅ Бот работает!\n\n"
        "Python 3.11 + aiogram"
    )


# Запуск
async def main():
    logging.info("🚀 Запускаем FreelanceHub...")

    # Удаляем старый webhook, если он был установлен
    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("🤖 Бот успешно запущен!")

    # Получаем обновления через Long Polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())