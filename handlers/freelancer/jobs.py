import html

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import func, select

from database.database import SessionLocal
from database.models.category import Category
from database.models.job import Job
from keyboards.freelancer_jobs import (
    freelancer_categories_keyboard,
    freelancer_job_details_keyboard,
    freelancer_jobs_keyboard,
)

router = Router()

JOBS_PER_PAGE = 5


def _budget_text(job: Job) -> str:
    if job.budget is None:
        return "Договорной"

    currency_names = {
        "USD": "USD",
        "EUR": "EUR",
        "RUB": "RUB",
        "STARS": "⭐ Stars",
    }

    currency = currency_names.get(job.currency, job.currency or "")
    return f"{job.budget:g} {currency}".strip()


def _short_description(description: str | None, limit: int = 120) -> str:
    text = " ".join((description or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


async def _get_categories():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Category)
            .where(Category.is_active.is_(True))
            .order_by(Category.sort_order, Category.id)
        )
        return result.scalars().all()


async def _get_category(category_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Category).where(
                Category.id == category_id,
                Category.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()


async def _render_jobs_page(
    callback: CallbackQuery,
    category_id: int,
    page: int,
):
    async with SessionLocal() as session:
        category_result = await session.execute(
            select(Category).where(
                Category.id == category_id,
                Category.is_active.is_(True),
            )
        )
        category = category_result.scalar_one_or_none()

        if category is None:
            await callback.answer(
                "Категория не найдена.",
                show_alert=True,
            )
            return

        total_result = await session.execute(
            select(func.count(Job.id)).where(
                Job.category_id == category_id,
                Job.status == "open",
            )
        )
        total = total_result.scalar_one()

        total_pages = max(1, (total + JOBS_PER_PAGE - 1) // JOBS_PER_PAGE)
        page = max(1, min(page, total_pages))

        jobs_result = await session.execute(
            select(Job)
            .where(
                Job.category_id == category_id,
                Job.status == "open",
            )
            .order_by(Job.created_at.desc(), Job.id.desc())
            .offset((page - 1) * JOBS_PER_PAGE)
            .limit(JOBS_PER_PAGE)
        )
        jobs = jobs_result.scalars().all()

    if not jobs:
        await callback.message.edit_text(
            f"📂 <b>{html.escape(category.name_ru)}</b>\n\n"
            "😔 В этой категории пока нет открытых работ.",
            parse_mode="HTML",
            reply_markup=freelancer_categories_keyboard(
                [category],
                language="ru",
            ),
        )
        return

    text_parts = [
        f"📂 <b>{html.escape(category.name_ru)}</b>",
        f"🔎 Найдено: <b>{total}</b>",
        f"📄 Страница <b>{page}/{total_pages}</b>",
        "",
        "Выберите подходящую работу:",
    ]

    for job in jobs:
        title = html.escape(job.title)
        description = html.escape(_short_description(job.description))
        deadline = html.escape(job.deadline or "Не указан")

        text_parts.extend(
            [
                "",
                "━━━━━━━━━━━━━━━━━━",
                f"📝 <b>{title}</b>",
                f"💰 {_budget_text(job)}   •   ⏳ {deadline}",
                description,
            ]
        )

    await callback.message.edit_text(
        "\n".join(text_parts),
        parse_mode="HTML",
        reply_markup=freelancer_jobs_keyboard(
            jobs,
            category_id=category_id,
            page=page,
            total_pages=total_pages,
        ),
    )


# ============================================================
# НАЙТИ РАБОТУ
# ============================================================

@router.callback_query(F.data == "freelancer:projects")
async def find_jobs(callback: CallbackQuery):
    categories = await _get_categories()

    if not categories:
        await callback.answer(
            "Категории пока не настроены.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "🔎 <b>Найти работу</b>\n\n"
        "Выберите категорию:",
        parse_mode="HTML",
        reply_markup=freelancer_categories_keyboard(
            categories,
            language="ru",
        ),
    )
    await callback.answer()


# ============================================================
# ВЫБОР КАТЕГОРИИ
# ============================================================

@router.callback_query(F.data.startswith("freelancer_category:"))
async def choose_category(callback: CallbackQuery):
    category_id = int(callback.data.split(":", 1)[1])
    await _render_jobs_page(callback, category_id, 1)
    await callback.answer()


# ============================================================
# ИНДИКАТОР СТРАНИЦЫ
# ============================================================

@router.callback_query(F.data == "freelancer_jobs:noop")
async def jobs_page_indicator(callback: CallbackQuery):
    await callback.answer()


# ============================================================
# ПАГИНАЦИЯ РАБОТ
# ============================================================

@router.callback_query(F.data.startswith("freelancer_jobs_page:"))
async def paginate_jobs(callback: CallbackQuery):
    _, category_id, page = callback.data.split(":")
    await _render_jobs_page(
        callback,
        int(category_id),
        int(page),
    )
    await callback.answer()


# ============================================================
# ОТКРЫТЬ РАБОТУ
# ============================================================

@router.callback_query(F.data.startswith("freelancer_job:"))
async def open_job(callback: CallbackQuery):
    _, job_id, category_id, page = callback.data.split(":")

    async with SessionLocal() as session:
        result = await session.execute(
            select(Job, Category)
            .join(Category, Job.category_id == Category.id)
            .where(
                Job.id == int(job_id),
                Job.status == "open",
            )
        )
        row = result.first()

    if row is None:
        await callback.answer(
            "Эта работа больше недоступна.",
            show_alert=True,
        )
        return

    job, category = row

    text = (
        f"📝 <b>{html.escape(job.title)}</b>\n\n"
        f"📂 Категория: <b>{html.escape(category.name_ru)}</b>\n\n"
        f"📄 <b>Описание:</b>\n"
        f"{html.escape(job.description)}\n\n"
        f"💰 <b>Бюджет:</b> {html.escape(_budget_text(job))}\n"
        f"⏳ <b>Срок:</b> {html.escape(job.deadline or 'Не указан')}"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=freelancer_job_details_keyboard(
            job.id,
            category_id=int(category_id),
            page=int(page),
        ),
    )
    await callback.answer()


# ============================================================
# НАЗАД К РАБОТАМ
# ============================================================

@router.callback_query(F.data.startswith("freelancer_jobs:back:"))
async def back_to_jobs(callback: CallbackQuery):
    _, category_id, page = callback.data.split(":")
    await _render_jobs_page(
        callback,
        int(category_id),
        int(page),
    )
    await callback.answer()


# ============================================================
# НАЗАД К КАТЕГОРИЯМ
# ============================================================

@router.callback_query(F.data == "freelancer_jobs:back")
async def back_to_categories(callback: CallbackQuery):
    categories = await _get_categories()

    await callback.message.edit_text(
        "🔎 <b>Найти работу</b>\n\n"
        "Выберите категорию:",
        parse_mode="HTML",
        reply_markup=freelancer_categories_keyboard(
            categories,
            language="ru",
        ),
    )
    await callback.answer()
