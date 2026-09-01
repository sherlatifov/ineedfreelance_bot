from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from sqlalchemy import select

from locales import t
from keyboards.start import language_keyboard, role_keyboard

from database.database import SessionLocal
from database.models import User
from database.repositories.user import (
    create_user,
    get_user,
    update_username,
)


router = Router()


# ============================================================
# СОСТОЯНИЯ РЕГИСТРАЦИИ
# ============================================================

class RegistrationState(StatesGroup):
    waiting_for_display_name = State()


# ============================================================
# /start
# ============================================================

@router.message(CommandStart())
async def start_handler(
    message: Message,
    state: FSMContext,
):
    telegram_id = message.from_user.id

    user = await get_user(telegram_id)

    # Новый пользователь
    if user is None:
        await state.clear()

        await message.answer(
            t("ru", "choose_language"),
            parse_mode="HTML",
            reply_markup=language_keyboard(),
        )

        return

    # Обновляем Telegram username
    await update_username(
        telegram_id,
        message.from_user.username,
    )

    language = user.language or "ru"

    # Имя ещё не указано
    if not user.display_name:
        await state.clear()

        await message.answer(
            t(language, "enter_display_name"),
            parse_mode="HTML",
        )

        await state.set_state(
            RegistrationState.waiting_for_display_name
        )

        return

    # Пользователь уже зарегистрирован.
    await message.answer(
        t(language, "choose_role"),
        parse_mode="HTML",
        reply_markup=role_keyboard(language),
    )


# ============================================================
# ВЫБОР ЯЗЫКА
# ============================================================

@router.callback_query(F.data.startswith("language:"))
async def select_language(
    callback: CallbackQuery,
    state: FSMContext,
):
    language = callback.data.split(":", 1)[1]

    if language not in ("ru", "en"):
        await callback.answer(
            "Unknown language",
            show_alert=True,
        )
        return

    telegram_id = callback.from_user.id

    user = await get_user(telegram_id)

    # Создаём пользователя
    if user is None:
        await create_user(
            telegram_id=telegram_id,
            username=callback.from_user.username,
            language=language,
        )

    # Пользователь уже существует — обновляем язык
    else:
        async with SessionLocal() as session:
            result = await session.execute(
                select(User).where(
                    User.telegram_id == telegram_id
                )
            )

            user = result.scalar_one_or_none()

            if user is not None:
                user.language = language
                user.username = callback.from_user.username

                await session.commit()

    await callback.answer()

    await callback.message.edit_text(
        t(language, "language_selected"),
        parse_mode="HTML",
    )

    await callback.message.answer(
        t(language, "enter_display_name"),
        parse_mode="HTML",
    )

    await state.set_state(
        RegistrationState.waiting_for_display_name
    )


# ============================================================
# ВВОД ИМЕНИ
# ============================================================

@router.message(
    RegistrationState.waiting_for_display_name
)
async def process_display_name(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer(
            t("ru", "display_name_invalid")
        )
        return

    display_name = message.text.strip()

    if len(display_name) < 2:
        user = await get_user(message.from_user.id)
        language = user.language if user and user.language else "ru"

        await message.answer(
            t(language, "display_name_too_short")
        )
        return

    if len(display_name) > 255:
        user = await get_user(message.from_user.id)
        language = user.language if user and user.language else "ru"

        await message.answer(
            t(language, "display_name_too_long")
        )
        return

    telegram_id = message.from_user.id

    # ВАЖНО:
    # получаем User и изменяем его
    # в ОДНОЙ И ТОЙ ЖЕ сессии.
    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            await state.clear()

            await message.answer(
                "Please use /start"
            )

            return

        language = user.language or "ru"

        user.display_name = display_name
        user.username = message.from_user.username

        await session.commit()

    await state.clear()

    await message.answer(
        t(language, "display_name_saved")
        + "\n\n"
        + t(language, "choose_role"),
        parse_mode="HTML",
        reply_markup=role_keyboard(language),
    )