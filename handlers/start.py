from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from database.database import SessionLocal
from database.models import User

from locales import get_language, t

from keyboards.start import role_keyboard
from keyboards.freelancer import freelancer_menu
from keyboards.client import client_menu


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )

        user = result.scalar_one_or_none()

    # ==========================================
    # НОВЫЙ ПОЛЬЗОВАТЕЛЬ
    # ==========================================

    if user is None:

        language = get_language(
            message.from_user.language_code
        )

        await message.answer(
            t(language, "welcome"),
            parse_mode="HTML",
            reply_markup=role_keyboard(language),
        )

        return

    # ==========================================
    # СУЩЕСТВУЮЩИЙ ПОЛЬЗОВАТЕЛЬ
    # ==========================================

    language = user.language or "ru"

    if user.role == "freelancer":

        await message.answer(
            t(language, "freelancer_mode")
            + "\n\n"
            + t(language, "choose_action"),
            parse_mode="HTML",
            reply_markup=freelancer_menu(language),
        )

    elif user.role == "client":

        await message.answer(
            t(language, "client_mode")
            + "\n\n"
            + t(language, "choose_action"),
            parse_mode="HTML",
            reply_markup=client_menu(language),
        )

    else:

        await message.answer(
            t(language, "welcome"),
            parse_mode="HTML",
            reply_markup=role_keyboard(language),
        )


@router.callback_query(F.data.startswith("role:"))
async def select_role(callback: CallbackQuery):

    role = callback.data.split(":")[1]

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == callback.from_user.id
            )
        )

        user = result.scalar_one_or_none()

        # Новый пользователь
        if user is None:

            language = get_language(
                callback.from_user.language_code
            )

            user = User(
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
                role=role,
                language=language,
            )

            session.add(user)

        else:

            language = user.language or "ru"

            user.role = role

        await session.commit()

    await callback.answer()

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

    else:

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


@router.callback_query(F.data == "switch:freelancer")
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


@router.callback_query(F.data == "switch:client")
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