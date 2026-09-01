import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден")


if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден")