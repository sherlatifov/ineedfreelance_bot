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
    Показывает меню выбранного режима.

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
    # Закрываем callback
    # ========================================================

    await callback.answer()

    # ========================================================
    # FREELANCER
    # ========================================================

    if role == "freelancer":

        await callback.message.answer(
            t(
                language,
                "freelancer_mode",
            ),
            parse_mode="HTML",
        )

        await callback.message.answer(
            t(
                language,
                "choose_action",
            ),
            reply_markup=freelancer_menu(
                language=language,
                is_admin=admin,
            ),
        )

        return
    
    # ========================================================
    # CLIENT
    # ========================================================

    await callback.message.answer(
        t(
            language,
            "client_mode",
        ),
        parse_mode="HTML",
    )

    await callback.message.answer(
        t(
            language,
            "choose_action",
        ),
        reply_markup=client_menu(
            language=language,
            is_admin=admin,
        ),
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
    Переключение режима.

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




        # Главный источник истины — Telegram ID.
        #
        # Даже если is_admin в БД почему-то False,
        # пользователь с ADMIN_TELEGRAM_ID всё равно
        # считается администратором.

        is_admin = (
            telegram_id == ADMIN_TELEGRAM_ID
        )

        # Синхронизируем значение в БД
        if user.is_admin != is_admin:

            user.is_admin = is_admin

        # Сохраняем роль и статус администратора
        await session.commit()

    # ========================================================
    # Закрываем callback
    # ========================================================

    await callback.answer()

    # ========================================================
    # FREELANCER
    # ========================================================

    if role == "freelancer":

        # ----------------------------------------------------
        # Текст режима
        # ----------------------------------------------------

        await callback.message.answer(
            t(
                language,
                "freelancer_mode",
            ),
            parse_mode="HTML",
        )

        # ----------------------------------------------------
        # Главное меню
        # ----------------------------------------------------

        await callback.message.answer(
            t(
                language,
                "choose_action",
            ),
            reply_markup=freelancer_menu(
                language=language,
                is_admin=is_admin,
            ),
        )

        return

    # ========================================================
    # CLIENT
    # ========================================================

    await callback.message.answer(
        t(
            language,
            "client_mode",
        ),
        parse_mode="HTML",
    )

    await callback.message.answer(
        t(
            language,
            "choose_action",
        ),
        reply_markup=client_menu(
            language=language,
            is_admin=is_admin,
        ),
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
    Первоначальный выбор:

        👨‍💻 Я фрилансер
        💼 Я клиент
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

    Freelancer:

        switch:client

    Client:

        switch:freelancer
    """

    role = callback.data.split(
        ":",
        1,
    )[1]

    await show_mode(
        callback=callback,
        role=role,
    )