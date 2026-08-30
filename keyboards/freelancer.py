from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def freelancer_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔎 Найти работу",
        callback_data="freelancer:projects",
    )

    builder.button(
        text="📋 Мои отклики",
        callback_data="freelancer:proposals",
    )

    builder.button(
        text="🤝 Мои сделки",
        callback_data="freelancer:contracts",
    )

    builder.button(
        text="👤 Мой профиль",
        callback_data="profile",
    )

    builder.button(
        text="🔄 Переключиться на заказчика",
        callback_data="switch:client",
    )

    builder.adjust(1)

    return builder.as_markup()