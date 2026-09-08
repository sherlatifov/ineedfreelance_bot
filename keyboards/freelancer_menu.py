from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t

def freelancer_menu(
    language: str,
    is_admin: bool = False,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    # ========================================================
    # АДМИН-ПАНЕЛЬ
    # ========================================================
    
    if is_admin:
        builder.button(
            text="👑 Админ-панель",
            callback_data="admin:panel",
        )


    # ========================================================
    # ПРОЕКТЫ
    # ========================================================

    builder.button(
        text=t(language, "find_projects"),
        callback_data="freelancer:projects",
    )

    # ========================================================
    # НАЙТИ ВАКАНСИИ
    # ========================================================

    builder.button(
        text=t(language, "find_vacancies"),
        callback_data="freelancer:projects",
    )

    # ========================================================
    # МОИ ПРЕДЛОЖЕНИЯ
    # ========================================================

    builder.button(
        text=t(language, "my_proposals"),
        callback_data="freelancer:proposals",
    )

    # ========================================================
    # МОИ КОНТРАКТЫ
    # ========================================================

    builder.button(
        text=t(language, "my_contracts"),
        callback_data="freelancer:contracts",
    )

    # ========================================================
    # ПРОФИЛЬ
    # ========================================================

    builder.button(
        text=t(language, "profile"),
        callback_data="freelancer:profile",
    )

    # ========================================================
    # ПЕРЕКЛЮЧЕНИЕ НА КЛИЕНТА
    # ========================================================

    builder.button(
        text=t(language, "switch_client"),
        callback_data="switch:client",
    )

    builder.adjust(1)

    return builder.as_markup()