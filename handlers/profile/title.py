from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.repositories.freelancer_profile import (
    get_or_create_freelancer_profile,
    update_freelancer_title,
)
from database.repositories.user import get_user
from handlers.profile.main import show_freelancer_profile_from_message


router = Router()


class TitleStates(StatesGroup):
    """
    FSM-состояния для редактирования Title.
    """

    waiting_for_title = State()


@router.callback_query(F.data == "profile:edit_title")
async def edit_profile_title(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Начинает редактирование Title.

    Пользователь нажимает:
    💻 Изменить Title

    После этого бот ждёт текстовое сообщение.
    """

    user = await get_user(
        callback.from_user.id
    )

    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    # Переводим пользователя в состояние
    # ожидания нового Title.
    await state.set_state(
        TitleStates.waiting_for_title
    )

    await callback.answer()

    if callback.message:
        await callback.message.edit_text(
            "💻 <b>Изменение Title</b>\n\n"
            "Введите ваш профессиональный Title.\n\n"
            "Например:\n"
            "<code>Python Backend Developer</code>\n\n"
            "Максимум — 255 символов.",
            parse_mode="HTML",
        )


@router.message(TitleStates.waiting_for_title)
async def process_profile_title(
    message: Message,
    state: FSMContext,
):
    """
    Получает новый Title от пользователя,
    проверяет его и сохраняет в PostgreSQL.
    """

    # Проверяем, что пользователь отправил текст.
    if not message.text:
        await message.answer(
            "❌ Пожалуйста, отправьте Title "
            "обычным текстовым сообщением."
        )
        return

    # Убираем пробелы в начале и конце.
    title = message.text.strip()

    # Проверяем минимальную длину.
    if len(title) < 2:
        await message.answer(
            "❌ Title слишком короткий.\n\n"
            "Введите минимум 2 символа."
        )
        return

    # Проверяем максимальную длину.
    if len(title) > 255:
        await message.answer(
            "❌ Title слишком длинный.\n\n"
            "Максимальная длина — 255 символов."
        )
        return

    # Получаем пользователя.
    user = await get_user(
        message.from_user.id
    )

    if user is None:
        await state.clear()

        await message.answer(
            "❌ Пользователь не найден.\n\n"
            "Пожалуйста, выполните /start."
        )
        return

    # Проверяем наличие FreelancerProfile.
    # Если его ещё нет — создаём.
    await get_or_create_freelancer_profile(
        user_id=user.id,
    )

    # Сохраняем Title в PostgreSQL.
    profile = await update_freelancer_title(
        user_id=user.id,
        title=title,
    )

    if profile is None:
        await state.clear()

        await message.answer(
            "❌ Не удалось сохранить Title."
        )
        return

    # Title успешно сохранён.
    # Выходим из FSM.
    await state.clear()

    await callback.answer(
        "✅ <b>Title успешно сохранён!</b>",
        show_alert=True,
    )

    # Показываем обновлённый профиль.
    await show_freelancer_profile_from_message(
        message
    )