from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup

from database.repositories.freelancer_profile import (
    get_or_create_freelancer_profile,
    update_freelancer_title,
)

from database.repositories.user import get_user
from handlers.profile.main import show_freelancer_profile

# Router раздела Title.
router = Router()


class TitleStates(StatesGroup):
    """
    Состояния, связанные только с редактированием Title.
    """

    waiting_for_title = State()

# =============================================================
# ИЗМЕНЕНИЕ TITLE
# =============================================================

@router.callback_query(F.data == "profile:edit_title")
async def edit_profile_title(
    callback: CallbackQuery,
    state: FSMContext,
):
        """
        Начало изменения профессионального Title.

        Следующим этапом сюда добавим FSM.

        Сценарий будет:

        💻 Изменить Title
                ↓
        FSM
                ↓
        Введите Title
                ↓
        Python Backend Developer
                ↓
        PostgreSQL
                ↓
        профиль
        """
user = await get_user(callback.from_user.id)
    
        if user is None:
                await callback.answer(
                "Пользователь не найден.",
                show_alert=True,
                )
                return
        
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
    Получаем Title от пользователя,
    проверяем и сохраняем его в БД.
    """

    if not message.text:
        await message.answer(
            "❌ Пожалуйста, отправьте Title "
            "обычным текстовым сообщением."
        )
        return

    title = message.text.strip()

    # Минимальная длина Title.
    if len(title) < 2:
        await message.answer(
            "❌ Title слишком короткий.\n\n"
            "Введите минимум 2 символа."
        )
        return

    # Максимальная длина соответствует
    # String(255) в модели FreelancerProfile.
    if len(title) > 255:
        await message.answer(
            "❌ Title слишком длинный.\n\n"
            "Максимальная длина — 255 символов."
        )
        return

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

    # Проверяем, что профиль фрилансера существует.
    await get_or_create_freelancer_profile(
        user_id=user.id,
    )

    # Сохраняем Title.
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

    # Закончили редактирование Title.
    await state.clear()

    await message.answer(
        "✅ <b>Title успешно сохранён!</b>",
        parse_mode="HTML",
    )

    # Показываем обновлённый профиль.
    await show_freelancer_profile_from_message(
        message
    )