from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def freelancer_profile_menu(
    language: str,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    if language == "en":

        builder.button(
            text="✏️ Edit profile",
            callback_data="profile:edit",
        )

        builder.button(
            text="🛠 Skills",
            callback_data="profile:skills",
        )

        builder.button(
            text="💰 Hourly rate",
            callback_data="profile:rate",
        )

        builder.button(
            text="🔄 Switch mode",
            callback_data="profile:switch",
        )

    else:

        builder.button(
            text="✏️ Редактировать профиль",
            callback_data="profile:edit",
        )

        builder.button(
            text="🛠 Навыки",
            callback_data="profile:skills",
        )

        builder.button(
            text="💰 Почасовая ставка",
            callback_data="profile:rate",
        )

        builder.button(
            text="🔄 Сменить режим",
            callback_data="profile:switch",
        )

    builder.adjust(1)

    return builder.as_markup()