from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from database.database import SessionLocal
from database.models import User

from locales import t

from keyboards.start import (
    language_keyboard,
    role_keyboard,
)

from keyboards.freelancer import freelancer_menu
from keyboards.client import client_menu


router = Router()


# ============================================================
# /START
# ============================================================

@router.message(CommandStart())
async def start_handler(message: Message):

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )

        user = result.scalar_one_or_none()

        # ====================================================
        # НОВЫЙ ПОЛЬЗОВАТЕЛЬ
        # ====================================================

        if user is None:

            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                role=None,
                language="ru",
            )

            session.add(user)

            await session.commit()

            await message.answer(
                t("ru", "choose_language"),
                parse_mode="HTML",
                reply_markup=language_keyboard(),
            )

            return

        # ====================================================
        # СУЩЕСТВУЮЩИЙ ПОЛЬЗОВАТЕЛЬ
        # ====================================================

        language = user.language or "ru"

        # Язык есть, но роль ещё не выбрана
        if user.role is None:

            await message.answer(
                t(language, "choose_role"),
                reply_markup=role_keyboard(language),
            )

            return

        # ====================================================
        # ФРИЛАНСЕР
        # ====================================================

        if user.role == "freelancer":

            await message.answer(
                t(language, "freelancer_mode")
                + "\n\n"
                + t(language, "choose_action"),
                parse_mode="HTML",
                reply_markup=freelancer_menu(language),
            )

            return

        # ====================================================
        # ЗАКАЗЧИК
        # ====================================================

        if user.role == "client":

            await message.answer(
                t(language, "client_mode")
                + "\n\n"
                + t(language, "choose_action"),
                parse_mode="HTML",
                reply_markup=client_menu(language),
            )

            return


# ============================================================
# ВЫБОР ЯЗЫКА
# ============================================================

@router.callback_query(
    F.data.startswith("language:")
)
async def select_language(
    callback: CallbackQuery,
):

    language = callback.data.split(":")[1]

    # Защита от неизвестного языка
    if language not in ("ru", "en"):

        await callback.answer(
            "Unknown language",
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

        # На всякий случай создаём пользователя,
        # если он каким-то образом отсутствует.

        if user is None:

            user = User(
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
                role=None,
                language=language,
            )

            session.add(user)

        else:

            user.language = language

        await session.commit()

    await callback.answer()

    # Показываем выбор режима
    await callback.message.edit_text(
        t(language, "language_selected")
        + "\n\n"
        + t(language, "choose_role"),
        parse_mode="HTML",
        reply_markup=role_keyboard(language),
    )


# ============================================================
# ВЫБОР РЕЖИМА
# ============================================================

@router.callback_query(
    F.data.startswith("role:")
)
async def select_role(
    callback: CallbackQuery,
):

    role = callback.data.split(":")[1]

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

        user.role = role

        language = user.language or "ru"

        await session.commit()

    await callback.answer()

    # ========================================================
    # ФРИЛАНСЕР
    # ========================================================

    if role == "freelancer":

        await callback.message.edit_text(
            t(language, "freelancer_mode")
            + "\n\n"
            + t(language, "freelancer_description"),
            parse_mode="HTML",
        )

        await callback.message.answer(
            t(language, "choose_action"),
            reply_markup=freelancer_menu(language),
        )

        return

    # ========================================================
    # ЗАКАЗЧИК
    # ========================================================

    await callback.message.edit_text(
        t(language, "client_mode")
        + "\n\n"
        + t(language, "client_description"),
        parse_mode="HTML",
    )

    await callback.message.answer(
        t(language, "choose_action"),
        reply_markup=client_menu(language),
    )


# ============================================================
# ПЕРЕКЛЮЧЕНИЕ НА ФРИЛАНСЕРА
# ============================================================

@router.callback_query(
    F.data == "switch:freelancer"
)
async def switch_to_freelancer(
    callback: CallbackQuery,
):

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

        user.role = "freelancer"

        language = user.language or "ru"

        await session.commit()

    await callback.answer(
        t(language, "switched_to_freelancer")
    )

    await callback.message.edit_text(
        t(language, "freelancer_mode")
        + "\n\n"
        + t(language, "choose_action"),
        parse_mode="HTML",
        reply_markup=freelancer_menu(language),
    )


# ============================================================
# ПЕРЕКЛЮЧЕНИЕ НА ЗАКАЗЧИКА
# ============================================================

@router.callback_query(
    F.data == "switch:client"
)
async def switch_to_client(
    callback: CallbackQuery,
):

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

        user.role = "client"

        language = user.language or "ru"

        await session.commit()

    await callback.answer(
        t(language, "switched_to_client")
    )

    await callback.message.edit_text(
        t(language, "client_mode")
        + "\n\n"
        + t(language, "choose_action"),
        parse_mode="HTML",
        reply_markup=client_menu(language),
    )