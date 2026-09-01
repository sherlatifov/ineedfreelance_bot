from aiogram import F, Router
from aiogram.types import CallbackQuery

from sqlalchemy import select

from database.database import SessionLocal
from database.models import User

from locales import t

from keyboards.freelancer import freelancer_menu
from keyboards.client import client_menu


router = Router()


@router.callback_query(F.data.startswith("role:"))
async def select_role(callback: CallbackQuery):

    role = callback.data.split(":", 1)[1]

    if role not in ("freelancer", "client"):
        await callback.answer(
            "Unknown role",
            show_alert=True,
        )
        return

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == callback.from_user.id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            await callback.answer(
                "User not found",
                show_alert=True,
            )
            return

        if not user.display_name:
            await callback.answer(
                "Profile name is required",
                show_alert=True,
            )
            return

        user.role = role

        language = user.language or "ru"
        is_admin = user.is_admin

        await session.commit()

    await callback.answer()

    # ========================================================
    # FREELANCER
    # ========================================================

    if role == "freelancer":

        await callback.message.edit_text(
            t(language, "freelancer_mode"),
            parse_mode="HTML",
        )

        await callback.message.answer(
            t(language, "choose_action"),
            reply_markup=freelancer_menu(
                language,
                is_admin=is_admin,
            ),
        )

        return

    # ========================================================
    # CLIENT
    # ========================================================

    await callback.message.edit_text(
        t(language, "client_mode"),
        parse_mode="HTML",
    )

    await callback.message.answer(
        t(language, "choose_action"),
        reply_markup=client_menu(language),
    )