from math import ceil

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

# Сколько работ показываем на одной странице.
JOBS_PER_PAGE = 3


# ============================================================
# ВСПОМОГАТЕЛЬНОЕ
# ============================================================


async def show_category_jobs(
    callback: CallbackQuery,
    category_id: int,
    page: int = 1,
) -> None:
    """Показывает страницу работ выбранной категории."""

    if page < 1:
        page = 1

    async with SessionLocal() as session:
        category_result = await session.execute(
            select(Category).where(
                Category.id == category_id,
                Category.is_active == True,
            )
        )

        category = category_result.scalar_one_or_none()

        if category is None:
            await callback.answer(
                "Категория не найдена.",
                show_alert=True,
            )
            return

        # Сначала узнаём общее количество открытых работ.
        total_result = await session.execute(
            select(func.count(Job.id)).where(
                Job.category_id == category_id,
                Job.status == "open",
            )
        )
        total_jobs = total_result.scalar_one() or 0

        if total_jobs == 0:
            await callback.message.edit_text(
                f"📂 <b>{category.name_ru}</b>\n\n"
                "😔 В этой категории пока нет открытых работ.",
                parse_mode="HTML",
                reply_markup=freelancer_categories_keyboard(
                    [category],
                    language="ru",
                ),
            )
            await callback.answer()
            return

        total_pages = ceil(total_jobs / JOBS_PER_PAGE)

        # Если работа была удалена/закрыта и старая страница стала пустой,
        # автоматически возвращаемся на последнюю существующую страницу.
        if page > total_pages:
            page = total_pages

        offset = (page - 1) * JOBS_PER_PAGE

        jobs_result = await session.execute(
            select(Job)
            .where(
                Job.category_id == category_id,
                Job.status == "open",
            )
            .order_by(Job.created_at.desc())
            .offset(offset)
            .limit(JOBS_PER_PAGE)
        )

        jobs = jobs_result.scalars().all()

    text = (
        f"📂 <b>{category.name_ru}</b>\n\n"
        f"🔎 Найдено: <b>{total_jobs}</b>\n"
        f"📄 Страница <b>{page}</b> из <b>{total_pages}</b>\n\n"
        "Выберите интересующую работу:"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=freelancer_jobs_keyboard(
            jobs,
            category_id=category_id,
            page=page,
            total_pages=total_pages,
        ),
    )

    await callback.answer()


async def show_categories(callback: CallbackQuery) -> None:
    """Показывает список категорий."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(
                Category.sort_order,
                Category.id,
            )
        )

        categories = result.scalars().all()

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
# НАЙТИ РАБОТУ
# ============================================================


@router.callback_query(F.data == "freelancer:projects")
async def find_jobs(callback: CallbackQuery):
    await show_categories(callback)


# ============================================================
# ВЫБОР КАТЕГОРИИ
# ============================================================


@router.callback_query(F.data.startswith("freelancer_category:"))
async def choose_category(callback: CallbackQuery):
    category_id = int(callback.data.split(":", 1)[1])
    await show_category_jobs(callback, category_id, page=1)


# ============================================================
# ПАГИНАЦИЯ
# ============================================================


@router.callback_query(F.data.startswith("freelancer_jobs:page:"))
async def jobs_page(callback: CallbackQuery):
    _, _, category_id, page = callback.data.split(":")

    await show_category_jobs(
        callback,
        category_id=int(category_id),
        page=int(page),
    )


@router.callback_query(F.data == "freelancer_jobs:current")
async def current_jobs_page(callback: CallbackQuery):
    # Кнопка "1 / 5" ничего не делает — просто убираем часики Telegram.
    await callback.answer()


# ============================================================
# ОТКРЫТЬ РАБОТУ
# ============================================================


@router.callback_query(F.data.startswith("freelancer_job:"))
async def open_job(callback: CallbackQuery):
    parts = callback.data.split(":")

    job_id = int(parts[1])
    category_id = int(parts[2])
    page = int(parts[3])

    async with SessionLocal() as session:
        result = await session.execute(
            select(Job, Category)
            .join(
                Category,
                Job.category_id == Category.id,
            )
            .where(
                Job.id == job_id,
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

    if job.budget is None:
        budget = "Договорной"
    else:
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

        budget = f"{job.budget:g} {currency}".strip()

    text = (
        f"📝 <b>{job.title}</b>\n\n"
        f"📂 Категория: <b>{category.name_ru}</b>\n\n"
        f"📄 <b>Описание:</b>\n"
        f"{job.description}\n\n"
        f"💰 <b>Бюджет:</b> {budget}\n"
        f"⏳ <b>Срок:</b> {job.deadline or 'Договорной'}"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=freelancer_job_details_keyboard(
            job.id,
            category_id=category_id,
            page=page,
        ),
    )

    await callback.answer()


# ============================================================
# НАЗАД К КАТЕГОРИЯМ
# ============================================================


@router.callback_query(F.data == "freelancer_jobs:back")
async def back_to_categories(callback: CallbackQuery):
    await show_categories(callback)
