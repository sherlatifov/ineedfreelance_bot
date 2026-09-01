from aiogram import F, Router
from aiogram.types import CallbackQuery


# Router раздела имени.
router = Router()


# =============================================================
# ИЗМЕНЕНИЕ ИМЕНИ
# =============================================================

@router.callback_query(F.data == "profile:edit_name")
async def edit_profile_name(
    callback: CallbackQuery,
):
    """
    Начало изменения имени.

    Позже здесь будет:

        кнопка
           ↓
        FSM
           ↓
        пользователь вводит имя
           ↓
        users.display_name
           ↓
        PostgreSQL
           ↓
        профиль
    """

    await callback.answer(
        "Редактирование имени сделаем следующим этапом 🙂",
        show_alert=True,
    )