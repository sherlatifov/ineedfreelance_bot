from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def client_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="➕ Создать заказ",
        callback_data="client:create_project",
    )

    builder.button(
        text="📋 Мои заказы",
        callback_data="client:projects",
    )

    builder.button(
        text="📩 Отклики",
        callback_data="client:proposals",
    )

    builder.button(
        text="👤 Мой профиль",
        callback_data="profile",
    )

    builder.button(
        text="🔄 Переключиться на фрилансера",
        callback_data="switch:freelancer",
    )

    builder.adjust(1)

    return builder.as_markup()