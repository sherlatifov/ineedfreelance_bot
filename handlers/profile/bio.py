from aiogram import F, Router
from aiogram.types import CallbackQuery


# Router раздела "О себе".
router = Router()


# =============================================================
# О СЕБЕ
# =============================================================

@router.callback_query(F.data == "profile:edit_bio")
async def edit_profile_bio(
    callback: CallbackQuery,
):
    """
    Начало редактирования информации "О себе".

    Позже добавим FSM и сохранение в:

        freelancer_profiles.bio
    """

    await callback.answer(
        "Поле «О себе» сделаем следующим этапом 🙂",
        show_alert=True,
    )