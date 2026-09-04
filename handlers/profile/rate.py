import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.repositories.freelancer_profile import (
    get_or_create_freelancer_profile,
    update_freelancer_rate,
)
from database.repositories.user import get_user
from handlers.profile.main import build_freelancer_profile_text


router = Router()

logger = logging.getLogger(__name__)


class RateStates(StatesGroup):
    """
    Состояния изменения почасовой ставки.
    """

    # Ожидаем стоимость.
    waiting_for_rate = State()

    # После стоимости ожидаем валюту.
    waiting_for_currency = State()


def currency_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора валюты.
    """

    builder = InlineKeyboardBuilder()

    builder.button(
        text="€ EUR",
        callback_data="profile:currency:EUR",
    )

    builder.button(
        text="$ USD",
        callback_data="profile:currency:USD",
    )

    builder.button(
        text="£ GBP",
        callback_data="profile:currency:GBP",
    )

    builder.button(
        text="⬅️ Отмена",
        callback_data="profile:rate_cancel",
    )

    builder.adjust(3, 1)

    return builder.as_markup()


@router.callback_query(F.data == "profile:edit_rate")
async def edit_profile_rate(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Начинает изменение почасовой ставки.
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

    # Проверяем наличие сообщения профиля.
    if callback.message is None:
        await callback.answer(
            "Не удалось открыть редактирование.",
            show_alert=True,
        )
        return

    # Запоминаем ID сообщения профиля.
    await state.update_data(
        profile_message_id=callback.message.message_id,
    )

    # Переходим в состояние ожидания стоимости.
    await state.set_state(
        RateStates.waiting_for_rate,
    )

    await callback.answer()

    # Меняем сообщение профиля.
    await callback.message.edit_text(
        text=(
            "💰 <b>Изменение ставки</b>\n\n"
            "Введите стоимость вашей работы за один час.\n\n"
            "Например:\n"
            "<code>50</code>\n\n"
            "Укажите целое число от 1 до 100000."
        ),
        parse_mode="HTML",
    )


@router.message(RateStates.waiting_for_rate)
async def process_profile_rate(
    message: Message,
    state: FSMContext,
):
    """
    Получает стоимость работы за час.
    """

    logger.info(
        "Получена новая ставка от пользователя %s",
        message.from_user.id,
    )

    # Проверяем, что пользователь отправил текст.
    if not message.text:
        await message.answer(
            "❌ Пожалуйста, отправьте стоимость числом."
        )
        return

    value = message.text.strip()

    # Проверяем, что введены только цифры.
    if not value.isdigit():
        await message.answer(
            "❌ Стоимость должна быть целым числом.\n\n"
            "Например: 50"
        )
        return

    hourly_rate = int(value)

    # Проверяем диапазон.
    if hourly_rate < 1:
        await message.answer(
            "❌ Минимальная ставка — 1."
        )
        return

    if hourly_rate > 100000:
        await message.answer(
            "❌ Максимальная ставка — 100000."
        )
        return

    # Сохраняем стоимость во временном состоянии FSM.
    await state.update_data(
        hourly_rate=hourly_rate,
    )

    # Переходим к выбору валюты.
    await state.set_state(
        RateStates.waiting_for_currency,
    )

    # Удаляем сообщение пользователя.
    try:
        await message.delete()
    except Exception:
        logger.exception(
            "Не удалось удалить сообщение со ставкой"
        )

    # Показываем выбор валюты.
    data = await state.get_data()

    profile_message_id = data.get(
        "profile_message_id"
    )

    if profile_message_id:

        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=profile_message_id,
                text=(
                    "💰 <b>Выберите валюту</b>\n\n"
                    f"Стоимость: <b>{hourly_rate}</b>\n\n"
                    "В какой валюте указывать стоимость?"
                ),
                parse_mode="HTML",
                reply_markup=currency_keyboard(),
            )

            return

        except Exception:
            logger.exception(
                "Не удалось показать выбор валюты"
            )

    # Если старое сообщение не удалось изменить.
    await message.answer(
        text=(
            "💰 <b>Выберите валюту</b>\n\n"
            f"Стоимость: <b>{hourly_rate}</b>\n\n"
            "В какой валюте указывать стоимость?"
        ),
        parse_mode="HTML",
        reply_markup=currency_keyboard(),
    )


@router.callback_query(
    RateStates.waiting_for_currency,
    F.data.startswith("profile:currency:"),
)
async def process_profile_currency(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Получает выбранную валюту
    и сохраняет ставку в БД.
    """

    # Получаем валюту из callback_data.
    currency = callback.data.split(":")[-1]

    # Разрешённые валюты.
    allowed_currencies = {
        "EUR",
        "USD",
        "GBP",
    }

    if currency not in allowed_currencies:
        await callback.answer(
            "❌ Недопустимая валюта.",
            show_alert=True,
        )
        return

    # Получаем сохранённую стоимость.
    data = await state.get_data()

    hourly_rate = data.get(
        "hourly_rate"
    )

    profile_message_id = data.get(
        "profile_message_id"
    )

    if hourly_rate is None:
        await state.clear()

        await callback.answer(
            "❌ Ставка не найдена. Попробуйте ещё раз.",
            show_alert=True,
        )
        return

    # Получаем пользователя.
    user = await get_user(
        callback.from_user.id,
    )

    if user is None:
        await state.clear()

        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    # Убеждаемся, что профиль существует.
    await get_or_create_freelancer_profile(
        user_id=user.id,
    )

    # Сохраняем ставку и валюту.
    updated_profile = await update_freelancer_rate(
        user_id=user.id,
        hourly_rate=hourly_rate,
        currency=currency,
    )

    if updated_profile is None:
        await state.clear()

        await callback.answer(
            "❌ Не удалось сохранить ставку.",
            show_alert=True,
        )
        return

    logger.info(
        "Ставка успешно изменена: "
        "user_id=%s rate=%s currency=%s",
        user.id,
        hourly_rate,
        currency,
    )

    # FSM больше не нужен.
    await state.clear()

    await callback.answer()

    # ---------------------------------------------------------
    # СТРОИМ ОБНОВЛЁННЫЙ ПРОФИЛЬ
    # ---------------------------------------------------------

    result = await build_freelancer_profile_text(
        telegram_id=callback.from_user.id,
    )

    if result is None:
        await callback.message.answer(
            "✅ Ставка успешно изменена.\n\n"
            "Но не удалось обновить профиль."
        )
        return

    profile_text, keyboard = result

    final_text = (
        "✅ <b>Ставка успешно изменена!</b>\n\n"
        + profile_text
    )

    # ---------------------------------------------------------
    # ОБНОВЛЯЕМ СТАРОЕ СООБЩЕНИЕ ПРОФИЛЯ
    # ---------------------------------------------------------

    if (
        callback.message is not None
        and profile_message_id
    ):
        try:
            await callback.message.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=profile_message_id,
                text=final_text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )

            logger.info(
                "Профиль успешно обновлён после изменения ставки"
            )

            return

        except Exception:
            logger.exception(
                "Не удалось обновить профиль "
                "после изменения ставки"
            )

    # Fallback.
    if callback.message:
        await callback.message.answer(
            text=final_text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


@router.callback_query(
    RateStates.waiting_for_currency,
    F.data == "profile:rate_cancel",
)
async def cancel_profile_rate(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Отменяет изменение ставки.
    """

    data = await state.get_data()

    profile_message_id = data.get(
        "profile_message_id"
    )

    await state.clear()

    await callback.answer(
        "Изменение ставки отменено."
    )

    # Возвращаем профиль.
    result = await build_freelancer_profile_text(
        telegram_id=callback.from_user.id,
    )

    if result is None:
        return

    profile_text, keyboard = result

    if (
        callback.message is not None
        and profile_message_id
    ):
        try:
            await callback.message.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=profile_message_id,
                text=profile_text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            return

        except Exception:
            logger.exception(
                "Не удалось вернуть профиль после отмены"
            )