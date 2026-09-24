from math import ceil

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.repositories.job import get_jobs_by_client
from database.repositories.user import get_user
from keyboards.client_jobs import client_projects_keyboard
from locales import t


router = Router()

PROJECTS_PER_PAGE = 5


def build_projects_text(
    language: str,
    page: int,
    total_pages: int,
) -> str:

    if language == "en":
        return (
            "<b>📋 My projects</b>\n\n"
            f"Page {page} of {total_pages}"
        )

    return (
        "<b>📋 Мои проекты</b>\n\n"
        f"Страница {page} из {total_pages}"
    )


async def show_projects(
    callback: CallbackQuery,
    page: int = 1,
):
    user = await get_user(callback.from_user.id)

    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    language = user.language or "ru"

    projects = await get_jobs_by_client(user.id)

    if not projects:
        text = (
            "<b>📋 Мои проекты</b>\n\n"
            "У вас пока нет созданных проектов."
            if language == "ru"
            else
            "<b>📋 My projects</b>\n\n"
            "You don't have any projects yet."
        )

        await callback.answer()

        if callback.message:
            await callback.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=None,
            )

        return

    total_pages = ceil(
        len(projects) / PROJECTS_PER_PAGE
    )

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * PROJECTS_PER_PAGE
    end = start + PROJECTS_PER_PAGE

    page_projects = projects[start:end]

    text = build_projects_text(
        language=language,
        page=page,
        total_pages=total_pages,
    )

    keyboard = client_projects_keyboard(
        jobs=page_projects,
        language=language,
        page=page,
        total_pages=total_pages,
    )

    await callback.answer()

    if callback.message:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


@router.callback_query(F.data == "client:projects")
async def open_projects(callback: CallbackQuery):
    await show_projects(
        callback=callback,
        page=1,
    )


@router.callback_query(
    F.data.startswith("client:projects:")
)
async def paginate_projects(callback: CallbackQuery):

    try:
        page = int(
            callback.data.split(":")[-1]
        )
    except (ValueError, AttributeError):
        await callback.answer(
            "Некорректная страница.",
            show_alert=True,
        )
        return

    await show_projects(
        callback=callback,
        page=page,
    )