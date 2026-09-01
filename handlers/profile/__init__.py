from aiogram import Router

# Импортируем router каждого раздела профиля.
from .main import router as main_router
from .navigation import router as navigation_router
from .name import router as name_router
from .title import router as title_router
from .bio import router as bio_router
from .skills import router as skills_router
from .rate import router as rate_router
from .reviews import router as reviews_router


# =============================================================
# ГЛАВНЫЙ ROUTER ПРОФИЛЯ
# =============================================================
#
# Этот router является "точкой входа" для всего профиля.
#
# bot.py не нужно знать, сколько внутри профиля файлов.
#
# bot.py
#   ↓
# profile.router
#   ↓
# ┌───────────────┐
# │ main          │
# │ navigation    │
# │ name          │
# │ title         │
# │ bio           │
# │ skills        │
# │ rate          │
# │ reviews       │
# └───────────────┘

router = Router()


# Подключаем каждый раздел.
router.include_router(main_router)
router.include_router(navigation_router)
router.include_router(name_router)
router.include_router(title_router)
router.include_router(bio_router)
router.include_router(skills_router)
router.include_router(rate_router)
router.include_router(reviews_router)