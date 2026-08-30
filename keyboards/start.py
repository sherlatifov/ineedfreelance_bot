from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def role_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="👨‍💻 Я фрилансер",
        callback_data="role:freelancer",
    )

    builder.button(
        text="💼 Я заказчик",
        callback_data="role:client",
    )

    builder.adjust(1)

    return builder.as_markup()