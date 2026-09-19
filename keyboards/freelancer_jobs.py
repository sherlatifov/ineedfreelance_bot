from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.category import Category


def freelancer_categories_keyboard(
    categories: list[Category],
    language: str = "ru",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for category in categories:
        name = (
            category.name_en
            if language == "en"
            else category.name_ru
        )

        builder.button(
            text=name,
            callback_data=f"freelancer_category:{category.id}",
        )

    builder.button(
        text="◀️ Назад",
        callback_data="freelancer_jobs:back",
    )

    builder.adjust(2)

    return builder.as_markup()


def freelancer_jobs_keyboard(
    jobs,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for job in jobs:
        builder.button(
            text=f"📝 {job.title}",
            callback_data=f"freelancer_job:{job.id}",
        )

    builder.button(
        text="◀️ Категории",
        callback_data="freelancer:projects",
    )

    builder.adjust(1)

    return builder.as_markup()


def freelancer_job_details_keyboard(
    job_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="📩 Откликнуться",
        callback_data=f"job_apply:{job_id}",
    )

    builder.button(
        text="◀️ Назад к работам",
        callback_data="freelancer_jobs:back",
    )

    builder.adjust(1)

    return builder.as_markup()