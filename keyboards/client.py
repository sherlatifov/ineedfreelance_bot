from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t


def client_menu(language: str) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text=t(language, "create_project"),
        callback_data="client:create_project",
    )

    builder.button(
        text=t(language, "my_projects"),
        callback_data="client:projects",
    )

    builder.button(
        text=t(language, "client_proposals"),
        callback_data="client:proposals",
    )

    builder.button(
        text=t(language, "profile"),
        callback_data="profile",
    )

    builder.button(
        text=t(language, "switch_freelancer"),
        callback_data="switch:freelancer",
    )

    builder.button(
        text="Админ-панель",
    )

    builder.adjust(1)

    return builder.as_markup()