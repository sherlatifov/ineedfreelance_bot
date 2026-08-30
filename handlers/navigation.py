from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.database import SessionLocal
from database.repositories import get_user

from keyboards.freelancer import freelancer_menu
from keyboards.client import client_menu

from locales import t


router = Router()


# ============================================================
# НАЗАД → МЕНЮ ФРИЛАНСЕРА
# ============================================================

@router.callback_query(F.data == "nav:freelancer")
async def back_to_freelancer(
    callback: CallbackQuery,
):

    async with SessionLocal() as session:

        user = await get_user(
            session,
            callback.from_user.id,
        )

        if user is None:

            await callback.answer(
                "User not found",
                show_alert=True,
            )

            return

        language = user.language or "ru"

    await callback.answer()

    await callback.message.edit_text(
        t(language, "freelancer_mode")
        + "\n\n"
        + t(language, "choose_action"),
        parse_mode="HTML",
        reply_markup=freelancer_menu(language),
    )


# ============================================================
# НАЗАД → МЕНЮ ЗАКАЗЧИКА
# ============================================================

@router.callback_query(F.data == "nav:client")
async def back_to_client(
    callback: CallbackQuery,
):

    async with SessionLocal() as session:

        user = await get_user(
            session,
            callback.from_user.id,
        )

        if user is None:

            await callback.answer(
                "User not found",
                show_alert=True,
            )

            return

        language = user.language or "ru"

    await callback.answer()

    await callback.message.edit_text(
        t(language, "client_mode")
        + "\n\n"
        + t(language, "choose_action"),
        parse_mode="HTML",
        reply_markup=client_menu(language),
    )