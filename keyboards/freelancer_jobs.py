from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.category import Category


def freelancer_categories_keyboard(
    categories: list[Category],
    language: str = "ru",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for category in categories:
        name = category.name_en if language == "en" else category.name_ru
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


def _job_button_text(job) -> str:
    budget = "Договорной" if job.budget is None else f"{job.budget:g} {job.currency or ''}".strip()
    deadline = job.deadline or "Без срока"

    # Telegram ограничивает текст inline-кнопки, поэтому показываем
    # максимум полезной информации: название + бюджет + срок.
    suffix = f" • 💰 {budget} • ⏳ {deadline}"
    available = max(12, 64 - len(suffix))
    title = job.title.strip()
    if len(title) > available:
        title = title[: available - 1].rstrip() + "…"

    return f"📝 {title}{suffix}"[:64]


def freelancer_jobs_keyboard(
    jobs,
    category_id: int,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for job in jobs:
        builder.button(
            text=_job_button_text(job),
            callback_data=f"freelancer_job:{job.id}:{category_id}:{page}",
        )

    navigation = []
    if page > 1:
        navigation.append(
            ("⬅️", f"freelancer_jobs_page:{category_id}:{page - 1}")
        )

    navigation.append(
        (f"{page}/{total_pages}", "freelancer_jobs:noop")
    )

    if page < total_pages:
        navigation.append(
            ("➡️", f"freelancer_jobs_page:{category_id}:{page + 1}")
        )

    for text, callback_data in navigation:
        builder.button(text=text, callback_data=callback_data)

    builder.button(
        text="📂 Категории",
        callback_data="freelancer:projects",
    )

    builder.adjust(1)
    return builder.as_markup()


def freelancer_job_details_keyboard(
    job_id: int,
    category_id: int,
    page: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="📩 Откликнуться",
        callback_data=f"job_apply:{job_id}",
    )
    builder.button(
        text="◀️ Назад к работам",
        callback_data=f"freelancer_jobs:back:{category_id}:{page}",
    )
    builder.adjust(1)
    return builder.as_markup()
