from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t


def role_keyboard(language: str) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text=t(language, "freelancer"),
        callback_data="role:freelancer",
    )

    builder.button(
        text=t(language, "client"),
        callback_data="role:client",
    )

    builder.adjust(1)

    return builder.as_markup()