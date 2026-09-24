from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def client_projects_keyboard(
    jobs,
    language: str,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    for job, category in jobs:
        category_name = (
            category.name_en
            if language == "en"
            else category.name_ru
        )

        if job.budget is None:
            budget = "Договорная" if language == "ru" else "Negotiable"
        else:
            budget = f"{job.budget} {job.currency or ''}".strip()

        button_text = (
            f"📌 {job.title}\n"
            f"📂 {category_name}\n"
            f"💰 {budget}"
        )

        builder.button(
            text=button_text,
            callback_data=f"client:project:{job.id}",
        )

    if total_pages > 1:

        if page > 1:
            builder.button(
                text="⬅️",
                callback_data=f"client:projects:{page - 1}",
            )

        builder.button(
            text=f"{page}/{total_pages}",
            callback_data="client:projects:current",
        )

        if page < total_pages:
            builder.button(
                text="➡️",
                callback_data=f"client:projects:{page + 1}",
            )

    builder.button(
        text="🔙 Назад",
        callback_data="client:back",
    )

    if total_pages > 1:
        builder.adjust(1, 3, 1)
    else:
        builder.adjust(1)

    return builder.as_markup()