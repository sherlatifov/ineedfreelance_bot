from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.repositories.user import get_user
from keyboards.client_menu import client_menu
from locales import t


router = Router()


# =============================================================
# НАЗАД ИЗ ПРОФИЛЯ КЛИЕНТА
# =============================================================

@router.callback_query(F.data == "client:profile:back")
async def client_profile_back(
    callback: CallbackQuery,
):
    """
    Возвращает пользователя из профиля
    обратно в меню заказчика.
    """

    user = await get_user(
        callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    language = user.language or "ru"

    is_admin = user.is_admin

    keyboard = client_menu(
        language=language,
        is_admin=is_admin,
    )

    text = (
        t(language, "client_mode")
        + "\n\n"
        + t(language, "choose_action")
    )

    await callback.answer()

    if callback.message:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )