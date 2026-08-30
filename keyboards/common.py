from aiogram.utils.keyboard import InlineKeyboardBuilder
from locales import t


def back_button(
    builder: InlineKeyboardBuilder,
    language: str,
    callback_data: str,
):
    builder.button(
        text=t(language, "back"),
        callback_data=callback_data,
    )