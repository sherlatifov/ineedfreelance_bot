from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def budget_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🤝 Договорной",
        callback_data="job_budget:negotiable",
    )

    builder.adjust(1)

    return builder.as_markup()


def currency_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🇺🇸 USD",
        callback_data="job_currency:USD",
    )

    builder.button(
        text="🇪🇺 EUR",
        callback_data="job_currency:EUR",
    )

    builder.button(
        text="🇷🇺 RUB",
        callback_data="job_currency:RUB",
    )

    builder.button(
        text="⭐ Telegram Stars",
        callback_data="job_currency:STARS",
    )

    builder.adjust(2)

    return builder.as_markup()


def deadline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🤝 Договорной",
        callback_data="job_deadline:negotiable",
    )

    builder.button(
        text="📅 Указать срок",
        callback_data="job_deadline:custom",
    )

    builder.button(
        text="❌ Отменить",
        callback_data="job_create:cancel",
    )

    builder.adjust(1)

    return builder.as_markup()


def files_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⏭ Пропустить",
        callback_data="job_files:skip",
    )

    builder.button(
        text="❌ Отменить",
        callback_data="job_create:cancel",
    )

    builder.adjust(1)

    return builder.as_markup()


def preview_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🚀 Опубликовать",
        callback_data="job_preview:publish",
    )

    builder.button(
        text="✏️ Изменить",
        callback_data="job_preview:edit",
    )

    builder.button(
        text="❌ Отменить",
        callback_data="job_create:cancel",
    )

    builder.adjust(1)

    return builder.as_markup()