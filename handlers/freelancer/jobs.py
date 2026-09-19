from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import select

from database.database import SessionLocal
from database.models.category import Category
from database.models.job import Job
from keyboards.freelancer_jobs import (
    freelancer_categories_keyboard,
    freelancer_job_details_keyboard,
    freelancer_jobs_keyboard,
)

router = Router()


# ============================================================
# НАЙТИ РАБОТУ
# ============================================================

@router.callback_query(F.data == "freelancer:projects")
async def find_jobs(
    callback: CallbackQuery,
):
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
# ВЫБОР КАТЕГОРИИ
# ============================================================

@router.callback_query(
    F.data.startswith("freelancer_category:")
)
async def choose_category(
    callback: CallbackQuery,
):
    category_id = int(
        callback.data.split(":", 1)[1]
    )

    async with SessionLocal() as session:

        category_result = await session.execute(
            select(Category)
            .where(
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

        jobs_result = await session.execute(
            select(Job)
            .where(
                Job.category_id == category_id,
                Job.status == "open",
            )
            .order_by(
                Job.created_at.desc()
            )
        )

        jobs = jobs_result.scalars().all()

    if not jobs:
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

    text = (
        f"📂 <b>{category.name_ru}</b>\n\n"
        f"🔎 Найдено работ: <b>{len(jobs)}</b>\n\n"
        "Выберите работу:"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=freelancer_jobs_keyboard(jobs),
    )

    await callback.answer()


# ============================================================
# ОТКРЫТЬ РАБОТУ
# ============================================================

@router.callback_query(
    F.data.startswith("freelancer_job:")
)
async def open_job(
    callback: CallbackQuery,
):
    job_id = int(
        callback.data.split(":", 1)[1]
    )

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

        budget = f"{job.budget} {currency}"

    text = (
        f"📝 <b>{job.title}</b>\n\n"
        f"📂 Категория: <b>{category.name_ru}</b>\n\n"
        f"📄 <b>Описание:</b>\n"
        f"{job.description}\n\n"
        f"💰 <b>Бюджет:</b> {budget}\n"
        f"⏳ <b>Срок:</b> {job.deadline or 'Не указан'}\n\n"
        f"🆔 Работа №{job.id}"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=freelancer_job_details_keyboard(
            job.id
        ),
    )

    await callback.answer()


# ============================================================
# НАЗАД К КАТЕГОРИЯМ
# ============================================================

@router.callback_query(
    F.data == "freelancer_jobs:back"
)
async def back_to_categories(
    callback: CallbackQuery,
):
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