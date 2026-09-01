import os

from dotenv import load_dotenv

# ============================================================
# ENVIRONMENT
# ============================================================

# Загружаем переменные из .env
load_dotenv()

# ============================================================
# TELEGRAM BOT
# ============================================================

# Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set"
    )

# ============================================================
# DATABASE
# ============================================================

# PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set"
    )

# ============================================================
# ADMIN
# ============================================================
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
