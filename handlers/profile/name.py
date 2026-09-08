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
from handlers.client.profile.main import build_client_profile_text

logger = logging.getLogger(__name__)

router = Router()


class NameStates(StatesGroup):
    waiting_for_name = State()


@router.callback_query(
    F.data.in_({
        "profile:edit_name",
        "freelancer:profile:name",
        "client:profile:name",
    })
)
async def edit_profile_name(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Начинает изменение общего display_name."""

    user = await get_user(callback.from_user.id)

    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    if callback.message is None:
        await callback.answer(
            "Не удалось открыть редактирование.",
            show_alert=True,
        )
        return

    # Определяем, откуда пользователь пришёл.
    source = (
        "client"
        if callback.data == "client:profile:name"
        else "freelancer"
    )

    await state.update_data(
        profile_message_id=callback.message.message_id,
        profile_source=source,
    )

    await state.set_state(NameStates.waiting_for_name)

    await callback.answer()

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
    """Сохраняет новый display_name."""

    if not message.text:
        await message.answer(
            "❌ Пожалуйста, отправьте имя текстом."
        )
        return

    name = message.text.strip()

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

    data = await state.get_data()

    profile_message_id = data.get(
        "profile_message_id"
    )

    profile_source = data.get(
        "profile_source",
        "freelancer",
    )

    await state.clear()

    try:
        await message.delete()
    except Exception:
        logger.warning(
            "Не удалось удалить сообщение с новым именем"
        )

    # ---------------------------------------------------------
    # ВОЗВРАЩАЕМ НУЖНЫЙ ПРОФИЛЬ
    # ---------------------------------------------------------

    if profile_source == "client":
        result = await build_client_profile_text(
            telegram_id=message.from_user.id,
        )
    else:
        result = await build_freelancer_profile_text(
            telegram_id=message.from_user.id,
        )

    if result is None:
        await message.answer(
            "✅ Имя успешно изменено."
        )
        return

    profile_text, keyboard = result

    final_text = (
        "✅ <b>Имя успешно изменено!</b>\n\n"
        f"{profile_text}"
    )

    if profile_message_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=profile_message_id,
                text=final_text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            return

        except Exception:
            logger.warning(
                "Не удалось обновить сообщение профиля"
            )

    await message.answer(
        text=final_text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )