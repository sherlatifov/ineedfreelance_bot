from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t
from keyboards.common import back_button


def freelancer_profile_menu(
    language: str,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.button(
        text=t(language, "edit_profile"),
        callback_data="profile:edit",
    )

    builder.button(
        text=t(language, "skills"),
        callback_data="profile:skills",
    )

    builder.button(
        text=t(language, "hourly_rate"),
        callback_data="profile:rate",
    )

    builder.button(
        text=t(language, "switch_mode"),
        callback_data="profile:switch",
    )

    back_button(
        builder,
        language,
        "nav:freelancer",
    )
    
    builder.adjust(1)

    return builder.as_markup()