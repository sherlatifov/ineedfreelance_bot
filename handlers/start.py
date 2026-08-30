from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from database.database import SessionLocal
from database.models import User

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

    # Новый пользователь
    if user is None:

        await message.answer(
            "👋 <b>Добро пожаловать в FreelanceHub!</b>\n\n"
            "На нашей платформе вы можете одновременно "
            "быть фрилансером и заказчиком.\n\n"
            "Сейчас выберите режим, с которого хотите начать:",
            parse_mode="HTML",
            reply_markup=role_keyboard(),
        )

        return

    # Пользователь уже существует

    if user.role == "freelancer":

        await message.answer(
            "👨‍💻 <b>Режим фрилансера</b>\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=freelancer_menu(),
        )

    else:

        await message.answer(
            "💼 <b>Режим заказчика</b>\n\n"
            "Выберите действие:",
            parse_mode="HTML",
            reply_markup=client_menu(),
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

        if user is None:

            user = User(
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
                role=role,
            )

            session.add(user)

        else:

            user.role = role

        await session.commit()

    await callback.answer()

    if role == "freelancer":

        await callback.message.edit_text(
            "👨‍💻 <b>Режим фрилансера</b>\n\n"
            "Теперь вы можете искать работу, "
            "отправлять отклики и работать над заказами.",
            parse_mode="HTML",
        )

        await callback.message.answer(
            "Выберите действие:",
            reply_markup=freelancer_menu(),
        )

    else:

        await callback.message.edit_text(
            "💼 <b>Режим заказчика</b>\n\n"
            "Теперь вы можете создавать заказы "
            "и находить исполнителей.",
            parse_mode="HTML",
        )

        await callback.message.answer(
            "Выберите действие:",
            reply_markup=client_menu(),
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
                "Сначала выполните /start",
                show_alert=True,
            )

            return

        user.role = "freelancer"

        await session.commit()

    await callback.answer(
        "Переключились на режим фрилансера"
    )

    await callback.message.edit_text(
        "👨‍💻 <b>Режим фрилансера</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=freelancer_menu(),
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
                "Сначала выполните /start",
                show_alert=True,
            )

            return

        user.role = "client"

        await session.commit()

    await callback.answer(
        "Переключились на режим заказчика"
    )

    await callback.message.edit_text(
        "💼 <b>Режим заказчика</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=client_menu(),
    )