from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.repositories.client_profile import (
    get_or_create_client_profile,
)
from database.repositories.user import get_user
from keyboards.client_profile import client_profile_keyboard


router = Router()


async def build_client_profile_text(
    telegram_id: int,
) -> tuple[str, object] | None:
    """
    Собирает профиль клиента.

    telegram_id — Telegram ID пользователя.
    """

    # Получаем пользователя по Telegram ID.
    user = await get_user(telegram_id)

    if user is None:
        return None

    # Получаем внутренний users.id.
    profile = await get_or_create_client_profile(
        user_id=user.id,
    )

    language = user.language or "ru"

    display_name = (
        user.display_name
        or "Не указано"
    )

    company_name = (
        profile.company_name
        or "Пока не указана"
    )

    description = (
        profile.description
        or "Пока не указано"
    )

    website = (
        profile.website
        or "Пока не указан"
    )

    text = (
        "💼 <b>Мой профиль заказчика</b>\n\n"
        f"👤 <b>{display_name}</b>\n\n"
        f"🏢 <b>Компания</b>\n"
        f"{company_name}\n\n"
        f"📝 <b>О себе</b>\n"
        f"{description}\n\n"
        f"🌐 <b>Сайт</b>\n"
        f"{website}"
    )

    keyboard = client_profile_keyboard(
        language=language,
    )

    return text, keyboard


async def show_client_profile(
    callback: CallbackQuery,
) -> None:
    """
    Показывает профиль клиента.
    """

    result = await build_client_profile_text(
        telegram_id=callback.from_user.id,
    )

    if result is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    text, keyboard = result

    await callback.answer()

    if callback.message:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


@router.callback_query(
    F.data == "client:profile"
)
async def client_profile(
    callback: CallbackQuery,
):
    await show_client_profile(callback)