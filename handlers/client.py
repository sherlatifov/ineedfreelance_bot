from aiogram import Router
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


def client_menu():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="➕ Создать заказ",
        callback_data="client:create_project",
    )

    builder.button(
        text="📋 Мои заказы",
        callback_data="client:projects",
    )

    builder.button(
        text="📩 Отклики",
        callback_data="client:proposals",
    )

    builder.button(
        text="👤 Мой профиль",
        callback_data="client:profile",
    )

    builder.adjust(1)

    return builder.as_markup()


async def show_client_menu(message):

    await message.answer(
        "💼 <b>Главное меню заказчика</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=client_menu(),
    )