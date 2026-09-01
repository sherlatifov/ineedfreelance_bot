from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from database.repositories.freelancer_profile import (
    get_or_create_freelancer_profile,
)
from database.repositories.user import get_user
from keyboards.profile import freelancer_profile_keyboard


router = Router()


async def build_freelancer_profile_text(
    user_id: int,
) -> tuple[str, object] | None:
    """
    Собирает текст профиля фрилансера
    и клавиатуру.

    Возвращает:
        (text, keyboard)
    """

    user = await get_user(user_id)

    if user is None:
        return None

    profile = await get_or_create_freelancer_profile(
        user_id=user.id,
    )

    language = user.language or "ru"

    display_name = user.display_name or "Не указано"

    title = profile.title or "Пока не указан"

    bio = profile.bio or "Пока не указано"

    skills = profile.skills or "Пока не указаны"

    if profile.hourly_rate is not None:
        rate = f"{profile.hourly_rate} € / час"
    else:
        rate = "Пока не указана"

    text = (
        f"👨‍💻 <b>{display_name}</b>\n\n"
        f"💻 <b>{title}</b>\n\n"
        f"⭐ Рейтинг: —\n"
        f"💬 Отзывы: 0\n"
        f"✅ Заказов выполнено: 0\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>О себе</b>\n"
        f"{bio}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🛠 <b>Навыки</b>\n"
        f"{skills}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 <b>Ставка</b>\n"
        f"{rate}"
    )

    keyboard = freelancer_profile_keyboard(
        language=language,
    )

    return text, keyboard


async def show_freelancer_profile(
    callback: CallbackQuery,
) -> None:
    """
    Показывает профиль после callback-запроса.
    """

    result = await build_freelancer_profile_text(
        user_id=callback.from_user.id,
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


async def show_freelancer_profile_from_message(
    message: Message,
) -> None:
    """
    Показывает профиль после обычного Message.

    Используется после сохранения данных через FSM.
    """

    result = await build_freelancer_profile_text(
        user_id=message.from_user.id,
    )

    if result is None:
        await message.answer(
            "❌ Пользователь не найден."
        )
        return

    text, keyboard = result

    await message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(F.data == "freelancer:profile")
async def freelancer_profile(
    callback: CallbackQuery,
):
    await show_freelancer_profile(callback)