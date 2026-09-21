from aiogram import F, Router
from aiogram.types import CallbackQuery


# Router отзывов.
router = Router()


# =============================================================
# ОТЗЫВЫ
# =============================================================

@router.callback_query(F.data == "profile:reviews")
async def profile_reviews(
    callback: CallbackQuery,
):
    """
    Просмотр отзывов фрилансера.

    В будущем здесь будет полноценная система:

        ⭐ 4.9
        💬 37 отзывов

        👤 Иван
        ⭐⭐⭐⭐⭐
        Отличный специалист...

        ─────────────────

        👤 Alex
        ⭐⭐⭐⭐
        Хорошо выполнил работу...

        [⬅️] [1/4] [➡️]

        [⬅️ Назад]
    """

    await callback.answer(
        "Систему отзывов сделаем позже 🙂",
        show_alert=True,
    )