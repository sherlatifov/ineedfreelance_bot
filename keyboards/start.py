from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t


def language_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора языка.
    """

    builder = InlineKeyboardBuilder()

    builder.button(
        text="🇷🇺 Русский",
        callback_data="language:ru",
    )

    builder.button(
        text="🇬🇧 English",
        callback_data="language:en",
    )

    builder.adjust(1)

    return builder.as_markup()


def role_keyboard(
    language: str,
) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора текущего режима.
    """

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