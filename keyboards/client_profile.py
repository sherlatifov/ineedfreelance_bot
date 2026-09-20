from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t


def client_profile_keyboard(
    language: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=t(
            language,
            "profile_edit_name",
        ),
        callback_data="client:profile:name",
    )

    builder.button(
        text=t(
            language,
            "client_profile_edit_company",
        ),
        callback_data="client:profile:company",
    )

    builder.button(
        text=t(
            language,
            "client_profile_edit_description",
        ),
        callback_data="client:profile:description",
    )

    builder.button(
        text=t(
            language,
            "client_profile_edit_website",
        ),
        callback_data="client:profile:website",
    )

    builder.button(
        text=t(
            language,
            "back",
        ),
        callback_data="client:profile:back",
    )

    builder.adjust(1)

    return builder.as_markup()