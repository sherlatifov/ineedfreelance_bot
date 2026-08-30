from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t


def freelancer_menu(
    language: str,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text=t(language, "find_projects"),
        callback_data="freelancer:projects",
    )

    builder.button(
        text=t(language, "my_proposals"),
        callback_data="freelancer:proposals",
    )

    builder.button(
        text=t(language, "my_contracts"),
        callback_data="freelancer:contracts",
    )

    builder.button(
        text=t(language, "profile"),
        callback_data="freelancer:profile",
    )

    builder.button(
        text=t(language, "switch_client"),
        callback_data="switch:client",
    )

    builder.adjust(1)

    return builder.as_markup()