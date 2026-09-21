from aiogram import F, Router
from aiogram.types import CallbackQuery


# Router навыков.
router = Router()


# =============================================================
# НАВЫКИ
# =============================================================

@router.callback_query(F.data == "profile:edit_skills")
async def edit_profile_skills(
    callback: CallbackQuery,
):
    """
    Управление навыками фрилансера.

    Позже здесь появится отдельный интерфейс:

        🛠 Навыки

        ☑ Python
        ☑ PostgreSQL
        ☐ FastAPI
        ☑ Aiogram

        [✅ Готово]
        [⬅️ Назад]
    """

    await callback.answer(
        "Навыки сделаем отдельным этапом 🙂",
        show_alert=True,
    )