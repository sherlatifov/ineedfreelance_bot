from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


def freelancer_menu():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔎 Найти работу",
        callback_data="freelancer:projects",
    )

    builder.button(
        text="📋 Мои отклики",
        callback_data="freelancer:proposals",
    )

    builder.button(
        text="💼 Мои проекты",
        callback_data="freelancer:contracts",
    )

    builder.button(
        text="👤 Мой профиль",
        callback_data="freelancer:profile",
    )

    builder.adjust(1)

    return builder.as_markup()


async def show_freelancer_menu(message):
    await message.answer(
        "👨‍💻 <b>Главное меню фрилансера</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=freelancer_menu(),
    )