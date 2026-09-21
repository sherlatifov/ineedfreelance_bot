import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.repositories.user import (
    get_user,
    update_display_name,
)
from handlers.profile.main import build_freelancer_profile_text


router = Router()

logger = logging.getLogger(__name__)


class NameStates(StatesGroup):
    """
    Состояния для изменения имени пользователя.
    """

    waiting_for_name = State()


@router.callback_query(F.data == "profile:edit_name")
async def edit_profile_name(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Начинает процесс изменения имени.
    """

    # Получаем пользователя по Telegram ID.
    user = await get_user(
        callback.from_user.id,
    )

    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    # Проверяем, что исходное сообщение существует.
    if callback.message is None:
        await callback.answer(
            "Не удалось открыть редактирование.",
            show_alert=True,
        )
        return

    # Сохраняем ID сообщения профиля.
    #
    # После ввода имени именно это сообщение
    # мы снова обновим.
    await state.update_data(
        profile_message_id=callback.message.message_id,
    )

    # Переводим пользователя в состояние
    # ожидания нового имени.
    await state.set_state(
        NameStates.waiting_for_name,
    )

    await callback.answer()

    # Меняем текущее сообщение профиля
    # на сообщение с инструкцией.
    await callback.message.edit_text(
        text=(
            "✏️ <b>Изменение имени</b>\n\n"
            "Введите новое отображаемое имя.\n\n"
            "Например:\n"
            "<code>Шерзод Латифов</code>\n\n"
            "Минимум — 2 символа.\n"
            "Максимум — 100 символов."
        ),
        parse_mode="HTML",
    )


@router.message(NameStates.waiting_for_name)
async def process_profile_name(
    message: Message,
    state: FSMContext,
):
    """
    Получает новое имя пользователя
    и сохраняет его в users.display_name.
    """

    logger.info(
        "Получено новое имя от пользователя %s",
        message.from_user.id,
    )

    # ---------------------------------------------------------
    # ПРОВЕРЯЕМ ТЕКСТ
    # ---------------------------------------------------------

    if not message.text:
        await message.answer(
            "❌ Пожалуйста, отправьте имя текстом."
        )
        return

    name = message.text.strip()

    # ---------------------------------------------------------
    # ПРОВЕРЯЕМ ДЛИНУ
    # ---------------------------------------------------------

    if len(name) < 2:
        await message.answer(
            "❌ Имя должно содержать минимум 2 символа."
        )
        return

    if len(name) > 100:
        await message.answer(
            "❌ Имя не должно превышать 100 символов."
        )
        return

    # ---------------------------------------------------------
    # ПОЛУЧАЕМ ПОЛЬЗОВАТЕЛЯ
    # ---------------------------------------------------------

    # Здесь message.from_user.id —
    # именно Telegram ID.
    user = await get_user(
        message.from_user.id,
    )

    if user is None:
        await state.clear()

        await message.answer(
            "❌ Пользователь не найден."
        )
        return

    # ---------------------------------------------------------
    # СОХРАНЯЕМ ИМЯ
    # ---------------------------------------------------------

    updated_user = await update_display_name(
        telegram_id=message.from_user.id,
        display_name=name,
    )

    if updated_user is None:
        await state.clear()

        await message.answer(
            "❌ Не удалось изменить имя."
        )
        return

    logger.info(
        "Имя успешно изменено: user_id=%s display_name=%r",
        user.id,
        name,
    )

    # ---------------------------------------------------------
    # ПОЛУЧАЕМ ID СТАРОГО СООБЩЕНИЯ
    # ---------------------------------------------------------

    data = await state.get_data()

    profile_message_id = data.get(
        "profile_message_id"
    )

    # FSM больше не нужен.
    await state.clear()

    # ---------------------------------------------------------
    # УДАЛЯЕМ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ
    # ---------------------------------------------------------

    try:
        await message.delete()
    except Exception:
        logger.exception(
            "Не удалось удалить сообщение с новым именем"
        )

    # ---------------------------------------------------------
    # СТРОИМ ОБНОВЛЁННЫЙ ПРОФИЛЬ
    # ---------------------------------------------------------

    result = await build_freelancer_profile_text(
        telegram_id=message.from_user.id,
    )

    if result is None:
        await message.answer(
            "✅ Имя успешно изменено.\n\n"
            "Но не удалось обновить отображение профиля."
        )
        return

    profile_text, keyboard = result

    # Добавляем уведомление непосредственно
    # в сообщение профиля.
    final_text = (
        "✅ <b>Имя успешно изменено!</b>\n\n"
        + profile_text
    )

    # ---------------------------------------------------------
    # ОБНОВЛЯЕМ СТАРОЕ СООБЩЕНИЕ ПРОФИЛЯ
    # ---------------------------------------------------------

    if profile_message_id:

        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=profile_message_id,
                text=final_text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

            logger.info(
                "Профиль успешно обновлён после изменения имени"
            )

            return

        except Exception:
            logger.exception(
                "Не удалось обновить сообщение профиля "
                "после изменения имени"
            )

    # ---------------------------------------------------------
    # FALLBACK
    # ---------------------------------------------------------

    await message.answer(
        text=final_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )