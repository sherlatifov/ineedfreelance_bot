from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from database.database import SessionLocal
from database.models import User

from locales import t

from keyboards.start import (
    language_keyboard,
    role_keyboard,
)

from keyboards.freelancer import freelancer_menu
from keyboards.client import client_menu


router = Router()


# ============================================================
# СОСТОЯНИЯ РЕГИСТРАЦИИ
# ============================================================


class RegistrationState(StatesGroup):
    waiting_for_display_name = State()


# ============================================================
# /START
# ============================================================


    @router.message(CommandStart())
    async def start_handler(
        message: Message,
        state: FSMContext,
    ):
    """
    Основная точка входа пользователя.

    Новый пользователь:
        /start
            ↓
        выбор языка
            ↓
        ввод имени
            ↓
        выбор роли
            ↓
        главное меню

    Существующий пользователь:
        сразу попадает в своё меню.
    """

    telegram_id = message.from_user.id

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

    # ========================================================
    # НОВЫЙ ПОЛЬЗОВАТЕЛЬ
    # ========================================================

    if user is None:

        # На всякий случай очищаем старое состояние
        await state.clear()

        # По умолчанию показываем русский.
        # Язык окончательно сохранится после выбора кнопки.
        await message.answer(
            t("ru", "choose_language"),
            parse_mode="HTML",
            reply_markup=language_keyboard(),
        )

        return

    # ========================================================
    # СУЩЕСТВУЮЩИЙ ПОЛЬЗОВАТЕЛЬ
    # ========================================================

    language = user.language or "ru"

    # --------------------------------------------------------
    # Пользователь ещё не указал имя профиля
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Пользователь ещё не выбрал режим
    # --------------------------------------------------------

    if user.role is None:

        await message.answer(
            t(language, "choose_role"),
            parse_mode="HTML",
            reply_markup=role_keyboard(language),
        )

        return

    # ========================================================
    # ФРИЛАНСЕР
    # ========================================================

    if user.role == "freelancer":

        await message.answer(
            t(language, "freelancer_mode")
            + "\n\n"
            + t(language, "choose_action"),
            parse_mode="HTML",
            reply_markup=freelancer_menu(language),
        )

        return

    # ========================================================
    # ЗАКАЗЧИК
    # ========================================================

    if user.role == "client":

        await message.answer(
            t(language, "client_mode")
            + "\n\n"
            + t(language, "choose_action"),
            parse_mode="HTML",
            reply_markup=client_menu(language),
        )

        return


# ============================================================
# ВЫБОР ЯЗЫКА
# ============================================================


@router.callback_query(
    F.data.startswith("language:")
)
async def select_language(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Сохраняем выбранный язык.

    После выбора языка:
        язык
          ↓
        ввод display_name
          ↓
        выбор роли
    """

    language = callback.data.split(":", 1)[1]

    # --------------------------------------------------------
    # Защита от неизвестного языка
    # --------------------------------------------------------

    if language not in ("ru", "en"):

        await callback.answer(
            "Unknown language",
            show_alert=True,
        )

        return

    telegram_id = callback.from_user.id
    username = callback.from_user.username

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        # ----------------------------------------------------
        # Если пользователя ещё нет — создаём.
        # Но имя и роль пока НЕ задаём.
        # ----------------------------------------------------

        if user is None:

            user = User(
                telegram_id=telegram_id,
                username=username,
                display_name=None,
                role=None,
                language=language,
            )

            session.add(user)

        else:

            # Username может измениться в Telegram,
            # поэтому обновляем его при каждом входе.
            user.username = username
            user.language = language

        await session.commit()

    await callback.answer()

    # --------------------------------------------------------
    # Просим имя для профиля FreelanceHub
    # --------------------------------------------------------

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
# ВВОД ИМЕНИ ПРОФИЛЯ
# ============================================================


@router.message(
    RegistrationState.waiting_for_display_name
)
async def process_display_name(
    message: Message,
    state: FSMContext,
):
    """
    Пользователь вводит имя,
    которое будет отображаться именно в FreelanceHub.

    Это НЕ Telegram first_name.
    """

    # --------------------------------------------------------
    # Проверяем, что пользователь отправил текст
    # --------------------------------------------------------

    if not message.text:

        await message.answer(
            t(
                "ru",
                "display_name_invalid",
            )
        )

        return

    display_name = message.text.strip()

    # --------------------------------------------------------
    # Определяем язык пользователя
    # --------------------------------------------------------

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
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

        # ----------------------------------------------------
        # Проверяем длину имени
        # ----------------------------------------------------

        if len(display_name) < 2:

            await message.answer(
                t(
                    language,
                    "display_name_too_short",
                )
            )

            return

        if len(display_name) > 255:

            await message.answer(
                t(
                    language,
                    "display_name_too_long",
                )
            )

            return

        # ----------------------------------------------------
        # Сохраняем имя
        # ----------------------------------------------------

        user.display_name = display_name

        # Заодно обновляем Telegram username
        user.username = message.from_user.username

        await session.commit()

    # --------------------------------------------------------
    # Регистрация имени закончена
    # --------------------------------------------------------

    await state.clear()

    await message.answer(
        t(language, "display_name_saved")
        + "\n\n"
        + t(language, "choose_role"),
        parse_mode="HTML",
        reply_markup=role_keyboard(language),
    )


# ============================================================
# ВЫБОР РЕЖИМА
# ============================================================


@router.callback_query(
    F.data.startswith("role:")
)
async def select_role(
    callback: CallbackQuery,
):
    """
    Первый выбор роли.

    role = freelancer
    или
    role = client

    Важно:
    это НЕ постоянная роль пользователя.

    Это текущий активный режим.
    """

    role = callback.data.split(":", 1)[1]

    if role not in (
        "freelancer",
        "client",
    ):

        await callback.answer(
            "Unknown role",
            show_alert=True,
        )

        return

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == callback.from_user.id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:

            await callback.answer(
                "User not found",
                show_alert=True,
            )

            return

        # ----------------------------------------------------
        # Защита: без display_name дальше не идём
        # ----------------------------------------------------

        if not user.display_name:

            await callback.answer(
                "Profile name is required",
                show_alert=True,
            )

            return

        user.role = role

        language = user.language or "ru"

        await session.commit()

    await callback.answer()

    # ========================================================
    # ФРИЛАНСЕР
    # ========================================================

    if role == "freelancer":

        await callback.message.edit_text(
            t(language, "freelancer_mode")
            + "\n\n"
            + t(language, "freelancer_description"),
            parse_mode="HTML",
        )

        await callback.message.answer(
            t(language, "choose_action"),
            reply_markup=freelancer_menu(language),
        )

        return

    # ========================================================
    # ЗАКАЗЧИК
    # ========================================================

    await callback.message.answer(
        t(language, "client_mode")
        + "\n\n"
        + t(language, "client_description"),
        parse_mode="HTML",
    )

    await callback.message.answer(
        t(language, "choose_action"),
        reply_markup=client_menu(language),
    )


# ============================================================
# ПЕРЕКЛЮЧЕНИЕ НА ФРИЛАНСЕРА
# ============================================================


@router.callback_query(
    F.data == "switch:freelancer"
)
async def switch_to_freelancer(
    callback: CallbackQuery,
):
    """
    Переключаем текущий режим пользователя
    на Freelancer.

    Пользователь остаётся тем же самым User.
    """

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == callback.from_user.id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:

            await callback.answer(
                "User not found",
                show_alert=True,
            )

            return

        user.role = "freelancer"

        language = user.language or "ru"

        await session.commit()

    await callback.answer(
        t(language, "switched_to_freelancer")
    )

    await callback.message.answer(
        t(language, "freelancer_mode")
        + "\n\n"
        + t(language, "choose_action"),
        parse_mode="HTML",
        reply_markup=freelancer_menu(language),
    )


# ============================================================
# ПЕРЕКЛЮЧЕНИЕ НА ЗАКАЗЧИКА
# ============================================================


@router.callback_query(
    F.data == "switch:client"
)
async def switch_to_client(
    callback: CallbackQuery,
):
    """
    Переключаем текущий режим пользователя
    на Client.
    """

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == callback.from_user.id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:

            await callback.answer(
                "User not found",
                show_alert=True,
            )

            return

        user.role = "client"

        language = user.language or "ru"

        await session.commit()

    await callback.answer(
        t(language, "switched_to_client")
    )

    await callback.message.answer(
        t(language, "client_mode")
        + "\n\n"
        + t(language, "choose_action"),
        parse_mode="HTML",
        reply_markup=client_menu(language),
    )