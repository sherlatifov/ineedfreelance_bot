from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.repositories.freelancer_profile import (
    get_or_create_freelancer_profile,
    update_freelancer_title,
)
from database.repositories.user import get_user
from handlers.profile.main import build_freelancer_profile_text
from utils.message import (
    delete_message_safely,
    edit_message_safely,
)


router = Router()


class TitleStates(StatesGroup):
    """
    FSM-состояния для редактирования Title.
    """

    waiting_for_title = State()


# ============================================================
# НАЖАТИЕ КНОПКИ «ИЗМЕНИТЬ TITLE»
# ============================================================

@router.callback_query(F.data == "profile:edit_title")
async def edit_profile_title(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Начинает редактирование Title.

    Пользователь нажимает:

        💻 Изменить Title

    После этого бот переводит пользователя
    в состояние ожидания текста.
    """

    # --------------------------------------------------------
    # Получаем пользователя
    # --------------------------------------------------------

    user = await get_user(
        callback.from_user.id
    )

    if user is None:

        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )

        return

    # --------------------------------------------------------
    # Проверяем, что сообщение профиля существует
    # --------------------------------------------------------

    if callback.message is None:

        await callback.answer(
            "Не удалось открыть редактирование.",
            show_alert=True,
        )

        return

    # --------------------------------------------------------
    # Сохраняем ID сообщения профиля
    # --------------------------------------------------------
    #
    # Например:
    #
    # сообщение №125
    #
    # Именно его потом будем превращать
    # обратно в обновлённый профиль.
    #

    await state.update_data(
        profile_message_id=callback.message.message_id
    )

    # --------------------------------------------------------
    # Переводим пользователя в FSM
    # --------------------------------------------------------

    await state.set_state(
        TitleStates.waiting_for_title
    )

    # Закрываем "часики" у inline-кнопки.
    await callback.answer()

    # --------------------------------------------------------
    # Вместо нового сообщения редактируем
    # существующее сообщение профиля.
    # --------------------------------------------------------

    await callback.message.edit_text(
        "💻 <b>Изменение Title</b>\n\n"
        "Введите ваш профессиональный Title.\n\n"
        "Например:\n"
        "<code>Python Backend Developer</code>\n\n"
        "Максимум — 255 символов.\n\n"
        "После отправки Title профиль "
        "обновится автоматически.",
        parse_mode="HTML",
    )


# ============================================================
# ПОЛУЧЕНИЕ НОВОГО TITLE
# ============================================================

@router.message(
    TitleStates.waiting_for_title
)
async def process_profile_title(
    message: Message,
    state: FSMContext,
):
    """
    Получает новый Title от пользователя.

    Последовательность:

        сообщение пользователя
                ↓
        проверка
                ↓
        PostgreSQL
                ↓
        удаление сообщения пользователя
                ↓
        обновление профиля
    """

    # ========================================================
    # 1. ПРОВЕРЯЕМ ТЕКСТ
    # ========================================================

    if not message.text:

        await message.answer(
            "❌ Пожалуйста, отправьте Title "
            "обычным текстовым сообщением."
        )

        return

    # Убираем пробелы по краям.

    title = message.text.strip()

    # ========================================================
    # 2. ПРОВЕРЯЕМ ДЛИНУ
    # ========================================================

    if len(title) < 2:

        await message.answer(
            "❌ Title слишком короткий.\n\n"
            "Введите минимум 2 символа."
        )

        return

    if len(title) > 255:

        await message.answer(
            "❌ Title слишком длинный.\n\n"
            "Максимальная длина — 255 символов."
        )

        return

    # ========================================================
    # 3. ПОЛУЧАЕМ ПОЛЬЗОВАТЕЛЯ
    # ========================================================

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

    # ========================================================
    # 4. ПОЛУЧАЕМ ИЛИ СОЗДАЁМ FREELANCER PROFILE
    # ========================================================

    await get_or_create_freelancer_profile(
        user_id=user.id
    )

    # ========================================================
    # 5. СОХРАНЯЕМ TITLE В POSTGRESQL
    # ========================================================

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

    # ========================================================
    # 6. ПОЛУЧАЕМ ID СТАРОГО СООБЩЕНИЯ ПРОФИЛЯ
    # ========================================================

    data = await state.get_data()

    profile_message_id = data.get(
        "profile_message_id"
    )

    # Для диагностики записываем информацию в лог.

    print(
        f"TITLE SAVED: "
        f"user_id={user.id}, "
        f"title={title!r}, "
        f"profile_message_id={profile_message_id}"
    )

    # ========================================================
    # 7. ОЧИЩАЕМ FSM
    # ========================================================
    #
    # После этого следующее сообщение пользователя
    # уже не будет считаться Title.
    #

    await state.clear()

    # ========================================================
    # 8. УДАЛЯЕМ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ
    # ========================================================
    #
    # Например:
    #
    # Пользователь:
    # Python Backend Developer
    #
    # Это сообщение удаляем.
    #

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    # ========================================================
    # 9. СТРОИМ ОБНОВЛЁННЫЙ ПРОФИЛЬ
    # ========================================================

    result = await build_freelancer_profile_text(
        user_id=user.id
    )

    if result is None:

        return

    text, keyboard = result

    # ========================================================
    # 10. ПЫТАЕМСЯ ИЗМЕНИТЬ СТАРОЕ СООБЩЕНИЕ
    # ========================================================

    if profile_message_id is not None:

        updated = await edit_message_safely(
            bot=message.bot,
            chat_id=message.chat.id,
            message_id=profile_message_id,
            text=text,
            reply_markup=keyboard,
        )

        # ====================================================
        # ВОТ ЗДЕСЬ БЫЛА ОСНОВНАЯ ОШИБКА
        # ====================================================
        #
        # Раньше было:
        #
        #     updated = ...
        #     return
        #
        # Поэтому если Telegram возвращал ошибку,
        # обработчик всё равно завершался.
        #
        # Теперь проверяем результат.
        #

        if updated:

            return

    # ========================================================
    # 11. FALLBACK
    # ========================================================
    #
    # Если старое сообщение невозможно изменить,
    # создаём новое сообщение профиля.
    #
    # Благодаря этому пользователь в любом случае
    # увидит результат.
    #

    await message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )