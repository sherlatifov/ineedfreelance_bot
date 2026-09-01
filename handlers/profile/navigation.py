from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.repositories.user import get_user
from keyboards.freelancer import freelancer_menu
from locales import t


# Router навигации профиля.
router = Router()


# =============================================================
# НАЗАД
# =============================================================

@router.callback_query(F.data == "profile:back")
async def profile_back(
    callback: CallbackQuery,
):
    """
    Возвращает пользователя из профиля
    обратно в меню фрилансера.

    Сейчас:

        Профиль
           ↓
        ⬅️ Назад
           ↓
        Меню фрилансера

    Позже здесь можно будет реализовать
    полноценную систему истории навигации.
    """

    # Получаем пользователя.
    user = await get_user(
        callback.from_user.id,
    )

    # Проверяем существование пользователя.
    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    # Получаем язык пользователя.
    language = user.language or "ru"

    # Проверяем права администратора.
    #
    # Это важно, чтобы администратор
    # продолжал видеть админ-панель.
    is_admin = user.is_admin

    # Создаём меню фрилансера.
    keyboard = freelancer_menu(
        language=language,
        is_admin=is_admin,
    )

    # Формируем текст меню.
    text = (
        t(language, "freelancer_mode")
        + "\n\n"
        + t(language, "choose_action")
    )

    # Убираем индикатор загрузки Telegram.
    await callback.answer()

    # Редактируем текущее сообщение.
    if callback.message:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )