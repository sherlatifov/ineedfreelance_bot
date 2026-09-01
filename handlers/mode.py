from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.repositories.user import (
    get_user,
    is_admin,
    update_role,
)

from keyboards.freelancer import freelancer_menu
from keyboards.client import client_menu

from locales import t


router = Router()


# ============================================================
# CONSTANTS
# ============================================================

VALID_ROLES = (
    "freelancer",
    "client",
)


# ============================================================
# SHOW MODE
# ============================================================

async def show_mode(
    callback: CallbackQuery,
    role: str,
):
    """
    Показывает главное меню выбранного режима.

    Используется для:

        role:freelancer
        role:client

    и:

        switch:freelancer
        switch:client
    """

    telegram_id = callback.from_user.id

    # ========================================================
    # Проверяем роль
    # ========================================================

    if role not in VALID_ROLES:
        await callback.answer(
            "Unknown role",
            show_alert=True,
        )
        return

    # ========================================================
    # Получаем пользователя
    # ========================================================

    user = await get_user(
        telegram_id
    )

    if user is None:
        await callback.answer(
            "User not found",
            show_alert=True,
        )
        return

    # ========================================================
    # Проверяем имя
    # ========================================================

    if not user.display_name:
        await callback.answer(
            "Profile name is required",
            show_alert=True,
        )
        return

    # ========================================================
    # Сохраняем роль
    # ========================================================

    user = await update_role(
        telegram_id=telegram_id,
        role=role,
    )

    if user is None:
        await callback.answer(
            "User not found",
            show_alert=True,
        )
        return

    # ========================================================
    # Получаем язык
    # ========================================================

    language = user.language or "ru"

    # ========================================================
    # Проверяем администратора
    # ========================================================

    admin = is_admin(
        telegram_id
    )

    # ========================================================
    # Формируем текст и клавиатуру
    # ========================================================

    if role == "freelancer":

        text = (
            t(
                language,
                "freelancer_mode",
            )
            + "\n\n"
            + t(
                language,
                "choose_action",
            )
        )

        keyboard = freelancer_menu(
            language=language,
            is_admin=admin,
        )

    else:

        text = (
            t(
                language,
                "client_mode",
            )
            + "\n\n"
            + t(
                language,
                "choose_action",
            )
        )

        keyboard = client_menu(
            language=language,
            is_admin=admin,
        )

    # ========================================================
    # Закрываем callback
    # ========================================================

    await callback.answer()

    # ========================================================
    # РЕДАКТИРУЕМ ТЕКУЩЕЕ СООБЩЕНИЕ
    # ========================================================

    if callback.message:

        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


# ============================================================
# INITIAL ROLE SELECTION
# ============================================================

@router.callback_query(
    F.data.startswith("role:")
)
async def select_role(
    callback: CallbackQuery,
):
    """
    Первоначальный выбор режима.
    """

    role = callback.data.split(
        ":",
        1,
    )[1]

    await show_mode(
        callback=callback,
        role=role,
    )


# ============================================================
# SWITCH MODE
# ============================================================

@router.callback_query(
    F.data.startswith("switch:")
)
async def switch_mode(
    callback: CallbackQuery,
):
    """
    Переключение между режимами.

    freelancer → client
    client → freelancer
    """

    role = callback.data.split(
        ":",
        1,
    )[1]

    await show_mode(
        callback=callback,
        role=role,
    )