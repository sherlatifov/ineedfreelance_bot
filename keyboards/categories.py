from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.category import Category


def categories_keyboard(
    categories: list[Category],
    language: str = "ru",
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    for category in categories:

        if language == "en":
            name = category.name_en
        else:
            name = category.name_ru

        builder.button(
            text=name,
            callback_data=f"category:{category.id}"
        )

    builder.adjust(2)

    return builder.as_markup()