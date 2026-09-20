from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.category import Category


# ============================================================
# КАТЕГОРИИ
# ============================================================


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


# ============================================================
# СПИСОК РАБОТ
# ============================================================


def _short_description(description: str, max_length: int = 150) -> str:
    """Обрезает описание для компактной карточки работы."""
    description = " ".join(description.split())

    if len(description) <= max_length:
        return description

    return description[:max_length].rstrip() + "…"


def _job_budget(job) -> str:
    if job.budget is None:
        return "💰 Договорной"

    currency_names = {
        "USD": "USD",
        "EUR": "EUR",
        "RUB": "RUB",
        "STARS": "⭐ Stars",
    }

    currency = currency_names.get(
        job.currency,
        job.currency or "",
    )

    return f"💰 {job.budget:g} {currency}".strip()


def job_card_text(job) -> str:
    """Текст одной работы. Вся карточка является одной кнопкой."""
    return (
        f"📝 {job.title}\n"
        f"{_job_budget(job)} • ⏳ {job.deadline or 'Договорной'}\n"
        f"{_short_description(job.description)}"
    )


def freelancer_jobs_keyboard(
    jobs,
    category_id: int,
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """
    Каждая работа — отдельная большая inline-кнопка.
    Никаких номеров работ в интерфейсе.
    """
    builder = InlineKeyboardBuilder()

    for job in jobs:
        builder.button(
            text=job_card_text(job),
            callback_data=f"freelancer_job:{job.id}:{category_id}:{page}",
        )

    # Пагинация показывается только если страниц больше одной.
    if total_pages > 1:
        if page > 1:
            builder.button(
                text="⬅️",
                callback_data=f"freelancer_jobs:page:{category_id}:{page - 1}",
            )

        builder.button(
            text=f"{page} / {total_pages}",
            callback_data="freelancer_jobs:current",
        )

        if page < total_pages:
            builder.button(
                text="➡️",
                callback_data=f"freelancer_jobs:page:{category_id}:{page + 1}",
            )

    builder.button(
        text="📂 Категории",
        callback_data="freelancer:projects",
    )

    builder.adjust(1)

    return builder.as_markup()


# ============================================================
# ПОЛНАЯ РАБОТА
# ============================================================


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
        callback_data=f"freelancer_jobs:page:{category_id}:{page}",
    )

    builder.adjust(1)

    return builder.as_markup()
