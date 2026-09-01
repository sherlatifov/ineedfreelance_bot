from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t

def client_menu(
    language: str,
    is_admin: bool = False,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    # ========================================================
    # СОЗДАТЬ ПРОЕКТ
    # ========================================================

    builder.button(
        text=t(language, "create_project"),
        callback_data="client:create_project",
    )

    # ========================================================
    # МОИ ПРОЕКТЫ
    # ========================================================

    builder.button(
        text=t(language, "my_projects"),
        callback_data="client:projects",
    )

    # ========================================================
    # ПРЕДЛОЖЕНИЯ
    # ========================================================

    builder.button(
        text=t(language, "client_proposals"),
        callback_data="client:proposals",
    )

    # ========================================================
    # ПРОФИЛЬ
    # ========================================================

    builder.button(
        text=t(language, "profile"),
        callback_data="profile",
    )

    # ========================================================
    # ПЕРЕКЛЮЧЕНИЕ НА ФРИЛАНСЕРА
    # ========================================================

    builder.button(
        text=t(language, "switch_freelancer"),
        callback_data="switch:freelancer",
    )

    # ========================================================
    # АДМИН-ПАНЕЛЬ
    # ========================================================

    if is_admin:
        builder.button(
            text="👑 Админ-панель",
            callback_data="admin:panel",
        )

    builder.adjust(1)

    return builder.as_markup()