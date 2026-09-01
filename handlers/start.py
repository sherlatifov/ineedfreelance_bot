from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.repositories.user import (
    create_user,
    get_user,
    update_display_name,
    update_language,
    update_username,
)

from keyboards.start import (
    language_keyboard, 
    role_keyboard,
)
from locales import t


router = Router()


# ============================================================
# REGISTRATION STATES
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
    telegram_id = message.from_user.id

    # --------------------------------------------------------
    # Получаем пользователя
    # --------------------------------------------------------

    user = await get_user(
        telegram_id
    )

    # ========================================================
    # НОВЫЙ ПОЛЬЗОВАТЕЛЬ
    # ========================================================

    if user is None:

        # На всякий случай очищаем старое состояние FSM
        await state.clear()

        # Пока язык неизвестен.
        # Поэтому используем русский по умолчанию.
        await message.answer(
            t("ru", "choose_language"),
            parse_mode="HTML",
            reply_markup=language_keyboard(),
        )

        return

    # ========================================================
    # ОБНОВЛЯЕМ USERNAME
    # ========================================================
    
    current_username = (
        message.from_user.username
    )
    
    if user.username != current_username:

        await update_username(
            telegram_id=telegram_id,
            username=current_username,
        )
    
    # ========================================================
    # ЯЗЫК ПОЛЬЗОВАТЕЛЯ
    # ========================================================

    language = user.language or "ru"

    # ========================================================
    # ИМЯ НЕ УКАЗАНО
    # ========================================================

    if not user.display_name:
        
        await state.clear()

        # Просим пользователя ввести имя
        await message.answer(
            t(language, "enter_display_name"),
            parse_mode="HTML",
        )

        # Переводим пользователя в состояние
        # ожидания имени.
        await state.set_state(
            RegistrationState.waiting_for_display_name
        )

        return

    # ========================================================
    # ПОЛЬЗОВАТЕЛЬ УЖЕ ЗАРЕГИСТРИРОВАН
    # ========================================================
    
    await state.clear()

    # Здесь НЕ запускаем freelancer/client mode.
    #
    # Только показываем выбор режима.
    #
    # Дальше callback:
    #
    # role:freelancer
    #
    # или:
    #
    # role:client
    #
    # обработает mode.py.

    await message.answer(
        t(language, "choose_role"),
        parse_mode="HTML",
        reply_markup=role_keyboard(language),
    )

# ============================================================
# LANGUAGE SELECTION
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

    # ========================================================
    # Проверяем существование пользователя
    # ========================================================

    user = await get_user(
        telegram_id
    )

    # ========================================================
    # СОЗДАЁМ НОВОГО ПОЛЬЗОВАТЕЛЯ
    # ========================================================

    if user is None:

        user = await create_user(
            telegram_id=telegram_id,
            username=callback.from_user.username,
            language=language,
        )
        # ========================================================
        # ПОЛЬЗОВАТЕЛЬ УЖЕ СУЩЕСТВУЕТ
        # ========================================================

        else:
            user = await update_language(
                telegram_id=telegram_id,
                language=language,
            )
    
        # ========================================================
        # Закрываем callback
        # ========================================================

        await callback.answer()

        # ========================================================
        # Сообщаем о выбранном языке
        # ========================================================
        
        await callback.message.answer(
            t(language, "language_selected"),
            parse_mode="HTML",
        )

        # ========================================================
        # Просим имя
        # ========================================================

        await callback.message.answer(
            t(language, "enter_display_name"),
            parse_mode="HTML",
        )

        # ========================================================
        # FSM:
        # ждём текст с именем
        # ========================================================

        await state.set_state(
            RegistrationState.waiting_for_display_name
        )

# ============================================================
# DISPLAY NAME
# ============================================================

@router.message(
    RegistrationState.waiting_for_display_name
)
async def process_display_name(
    message: Message,
    state: FSMContext,
):
    """
        Получаем имя пользователя.

        После успешного сохранения:

        имя
         ↓
        PostgreSQL
         ↓
        выбор режима
    """

    # ========================================================
    # Проверяем наличие текста
    # ========================================================

    if not message.text:
        
        await message.answer(
            t("ru", "display_name_invalid")
        )

        return

    # ========================================================
    # Очищаем пробелы
    # ========================================================

    display_name = message.text.strip()

    # ========================================================
    # Проверка минимальной длины
    # ========================================================

    if len(display_name) < 2:

        user = await get_user(
            message.from_user.id
        )

        language = (
            user.language
            if user and user.language
            else "ru"
        )

        await message.answer(
            t(language, "display_name_too_short")
        )

        return

    # ========================================================
    # Проверка максимальной длины
    # ========================================================

    if len(display_name) > 255:

        user = await get_user(
            message.from_user.id
        )

        language = (
            user.language
            if user and user.language
            else "ru"
        )

        await message.answer(
            t(language, "display_name_too_long")
        )

        return

    telegram_id = message.from_user.id

    # ========================================================
    # СОХРАНЯЕМ ИМЯ
    # ========================================================

    user = await update_display_name(
        telegram_id=telegram_id,
        display_name=display_name,
    )

    # ========================================================
    # Пользователь не найден
    # ========================================================

    if user is None:

        await state.clear()

        await message.answer(
            "Please use /start"
        )

        return

    # ========================================================
    # Получаем язык
    # ========================================================

    language = user.language or "ru"

    # ========================================================
    # Регистрация закончена
    # ========================================================

    await state.clear()

    # --------------------------------------------------------
    # Сообщение об успешном сохранении
    # --------------------------------------------------------

    await message.answer(
        t(
            language,
            "display_name_saved",
        ),
        parse_mode="HTML",
    )

    # --------------------------------------------------------
    # Теперь выбираем первый режим
    # --------------------------------------------------------

    await message.answer(
        t(
            language,
            "choose_role",
        ),
        parse_mode="HTML",
        reply_markup=role_keyboard(language),
    )