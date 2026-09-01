from aiogram import F, Router
from aiogram.types import CallbackQuery


# Router раздела Title.
router = Router()


# =============================================================
# ИЗМЕНЕНИЕ TITLE
# =============================================================

@router.callback_query(F.data == "profile:edit_title")
async def edit_profile_title(
    callback: CallbackQuery,
):
    """
    Начало изменения профессионального Title.

    Следующим этапом сюда добавим FSM.

    Сценарий будет:

        💻 Изменить Title
                ↓
        FSM
                ↓
        Введите Title
                ↓
        Python Backend Developer
                ↓
        PostgreSQL
                ↓
        профиль
    """

    await callback.answer(
        "Редактирование Title сделаем следующим этапом 🙂",
        show_alert=True,
    )