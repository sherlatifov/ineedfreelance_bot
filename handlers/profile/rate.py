from aiogram import F, Router
from aiogram.types import CallbackQuery


# Router почасовой ставки.
router = Router()


# =============================================================
# ПОЧАСОВАЯ СТАВКА
# =============================================================

@router.callback_query(F.data == "profile:edit_rate")
async def edit_profile_rate(
    callback: CallbackQuery,
):
    """
    Редактирование почасовой ставки.

    Позже сделаем:

        💰 Ставка
             ↓
        Введите сумму
             ↓
        25
             ↓
        Выберите валюту
             ↓
        🇪🇺 EUR
        🇺🇸 USD
        🇬🇧 GBP
        🇷🇺 RUB
             ↓
        PostgreSQL
    """

    await callback.answer(
        "Ставку сделаем отдельным этапом 🙂",
        show_alert=True,
    )