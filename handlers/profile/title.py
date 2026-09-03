import logging

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
from utils.message import delete_message_safely


router = Router()

logger = logging.getLogger(__name__)


# ============================================================
# FSM СОСТОЯНИЯ
# ============================================================

class TitleStates(StatesGroup):
    """
    FSM-состояния для редактирования Title.
    """

    waiting_for_title = State()


# ============================================================
# НАЖАТИЕ «ИЗМЕНИТЬ TITLE»
# ============================================================

@router.callback_query(F.data == "profile:edit_title")
async def edit_profile_title(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Открывает экран изменения Title.

    Мы НЕ отправляем новое сообщение.

    Вместо этого редактируем существующее сообщение
    профиля.

    После этого пользователь вводит новый Title.
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
    # Проверяем сообщение
    # --------------------------------------------------------

    if callback.message is None:
        await callback.answer(
            "Не удалось открыть редактирование.",
            show_alert=True,
        )
        return

    # --------------------------------------------------------
    # СОХРАНЯЕМ ID СООБЩЕНИЯ ПРОФИЛЯ
    # --------------------------------------------------------
    #
    # Например:
    #
    # profile_message_id = 157
    #
    # После ввода Title именно сообщение №157
    # мы вернём обратно в профиль.
    #

    await state.update_data(
        profile_message_id=callback.message.message_id
    )

    # --------------------------------------------------------
    # Переводим пользователя в состояние ожидания Title
    # --------------------------------------------------------

    await state.set_state(
        TitleStates.waiting_for_title
    )

    await callback.answer()

    # --------------------------------------------------------
    # Редактируем существующее сообщение профиля
    # --------------------------------------------------------

    await callback.message.edit_text(
        "💻 <b>Изменение Title</b>\n\n"
        "Введите ваш профессиональный Title.\n\n"
        "Например:\n"
        "<code>Python Backend Developer</code>\n\n"
        "Максимум — 255 символов.",
        parse_mode="HTML",
    )


# ============================================================
# ПОЛЬЗОВАТЕЛЬ ВВОДИТ TITLE
# ============================================================

@router.message(
    TitleStates.waiting_for_title
)
async def process_profile_title(
    message: Message,
    state: FSMContext,
):
    """
    Получает новый Title пользователя.

    После успешного сохранения:

        PostgreSQL
             ↓
        удаляем сообщение пользователя
             ↓
        обновляем сообщение профиля
             ↓
        показываем профиль
    """

    logger.info(
        "Получен новый Title от пользователя %s",
        message.from_user.id,
    )

    # ========================================================
    # 1. ПРОВЕРЯЕМ, ЧТО ПРИШЁЛ ТЕКСТ
    # ========================================================

    if not message.text:

        await message.answer(
            "❌ Пожалуйста, отправьте Title "
            "обычным текстовым сообщением."
        )

        return

    title = message.text.strip()

    # ========================================================
    # 2. ПРОВЕРЯЕМ ДЛИНУ TITLE
    # ========================================================

    if len(title) < 2:

        await message.answer(
            "❌ Title слишком короткий.\n\n"
            "Минимум — 2 символа."
        )

        return

    if len(title) > 255:

        await message.answer(
            "❌ Title слишком длинный.\n\n"
            "Максимум — 255 символов."
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
    # 4. ПОЛУЧАЕМ FREELANCER PROFILE
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

    logger.info(
        "Title успешно сохранён: user_id=%s title=%r",
        user.id,
        title,
    )

    # ========================================================
    # 6. ПОЛУЧАЕМ ID СООБЩЕНИЯ ПРОФИЛЯ
    # ========================================================

    data = await state.get_data()

    profile_message_id = data.get(
        "profile_message_id"
    )

    logger.info(
        "profile_message_id=%s",
        profile_message_id,
    )

    # ========================================================
    # 7. ОЧИЩАЕМ FSM
    # ========================================================

    await state.clear()

    # ========================================================
    # 8. УДАЛЯЕМ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ
    # ========================================================
    #
    # Пользователь отправил:
    #
    # Python Backend Developer
    #
    # После сохранения это сообщение нам больше
    # не нужно.
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

        logger.error(
            "Не удалось построить профиль: user_id=%s",
            user.id,
        )

        return

    profile_text, keyboard = result

    # ========================================================
    # 10. ДОБАВЛЯЕМ УВЕДОМЛЕНИЕ ОБ УСПЕШНОМ ИЗМЕНЕНИИ
    # ========================================================
    #
    # Не отправляем отдельное сообщение.
    #
    # Просто добавляем уведомление в начало
    # того же сообщения, которое сейчас находится
    # на экране пользователя.
    #

    final_text = (
        "✅ <b>Title успешно изменён!</b>\n\n"
        + profile_text
    )

    # ========================================================
    # 11. ВОЗВРАЩАЕМ ПОЛЬЗОВАТЕЛЯ НА ПРОФИЛЬ
    # ========================================================

    if profile_message_id is not None:

        try:

            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=profile_message_id,
                text=final_text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

            logger.info(
                "Профиль успешно обновлён после изменения Title. "
                "user_id=%s message_id=%s",
                user.id,
                profile_message_id,
            )

            return

        except Exception:
            # ------------------------------------------------
            # Очень важно:
            #
            # здесь мы НЕ скрываем ошибку.
            #
            # Если Telegram не смог изменить сообщение,
            # полный traceback попадёт в лог BotHost.
            # ------------------------------------------------

            logger.exception(
                "ОШИБКА при возврате на профиль. "
                "user_id=%s message_id=%s",
                user.id,
                profile_message_id,
            )

    # ========================================================
    # 12. FALLBACK
    # ========================================================
    #
    # Если старое сообщение невозможно изменить,
    # отправляем новый профиль.
    #

    await message.answer(
        text=final_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )