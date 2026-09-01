from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.repositories.user import get_user
from keyboards.client import client_menu
from keyboards.freelancer import freelancer_menu
from keyboards.profile import freelancer_profile_keyboard
from locales import t

# Создаём Router.
#
# Все обработчики, связанные с профилем,
# будут находиться здесь.
router = Router()

async def show_freelancer_profile(
    callback: CallbackQuery,
) -> None:
    """
    Показывает профиль текущего пользователя
    в режиме фрилансера.

    Эта функция НЕ является callback handler'ом.
    Это обычная вспомогательная функция,
    которую смогут использовать разные обработчики.
    """

    # Получаем Telegram ID пользователя,
    # который нажал кнопку.
    telegram_id = callback.from_user.id

    # Получаем пользователя из базы данных.
    user = await get_user(telegram_id)

    # Если пользователя нет в БД,
    # показываем ошибку.
    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return
    
    # Получаем язык пользователя.
    #
    # Если язык по какой-то причине не установлен,
    # используем русский.
    language = user.language or "ru"

    # ---------------------------------------------------------
    # ДАННЫЕ ПРОФИЛЯ
    # ---------------------------------------------------------

    # Имя берём непосредственно из users.display_name.
    display_name = user.display_name or "Не указано"

    # ---------------------------------------------------------
    # ВРЕМЕННЫЕ ЗНАЧЕНИЯ
    # ---------------------------------------------------------
    #
    # Сейчас система рейтинга, отзывов и заказов
    # ещё не реализована.
    #
    # Поэтому временно показываем нули.
    #
    # Позже эти значения будут получаться
    # непосредственно из базы данных.
    rating = "—"
    reviews_count = 0
    completed_orders = 0

    # ---------------------------------------------------------
    # ФОРМИРУЕМ ТЕКСТ ПРОФИЛЯ
    # ---------------------------------------------------------

    text = (
        f"👨‍💻 <b>{display_name}</b>\n\n"
        f"⭐ Рейтинг: {rating}\n"
        f"💬 Отзывы: {reviews_count}\n"
        f"✅ Заказов выполнено: {completed_orders}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💻 <b>Title</b>\n"
        f"Пока не указан\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>О себе</b>\n"
        f"Пока не указано\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"🛠 <b>Навыки</b>\n"
        f"Пока не указаны\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 <b>Ставка</b>\n"
        f"Пока не указана"
    )

    # Получаем клавиатуру профиля.
    keyboard = freelancer_profile_keyboard(
        language=language,
    )

    # Отвечаем на callback.
    #
    # Без этого Telegram будет продолжать показывать
    # индикатор загрузки на кнопке.
    await callback.answer()

    # callback.message может отсутствовать
    # или быть недоступным.
    #
    # Поэтому сначала проверяем его.
    if callback.message:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

# =============================================================
# ОТКРЫТИЕ ПРОФИЛЯ
# =============================================================

@router.callback_query(F.data == "freelancer:profile")
async def freelancer_profile(
    callback: CallbackQuery,
):
    """
    Обработчик кнопки:

        👤 Мой профиль

    из меню фрилансера.
    """

    await show_freelancer_profile(callback)

# =============================================================
# КНОПКА "НАЗАД"
# =============================================================

@router.callback_query(F.data == "profile:back")
async def profile_back(
    callback: CallbackQuery,
):
    """
    Возвращает пользователя из профиля
    обратно в меню фрилансера.

    Пока делаем простой вариант.

    Позже здесь можно будет подключить
    полноценную систему навигации.
    """

    # Получаем пользователя.
    user = await get_user(callback.from_user.id)

    # Если пользователь не найден —
    # показываем ошибку.
    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    # Определяем язык.
    language = user.language or "ru"

    # Проверяем права администратора.
    #
    # Это нужно для того, чтобы администратор
    # продолжал видеть кнопку админ-панели.
    is_admin = user.is_admin

    # Получаем меню фрилансера.
    keyboard = freelancer_menu(
        language=language,
        is_admin=is_admin,
    )

    # Текст главного меню.
    text = (
        t(language, "freelancer_mode")
        + "\n\n"
        + t(language, "choose_action")
    )

    # Убираем индикатор загрузки Telegram.
    await callback.answer()

    # Возвращаемся на экран меню,
    # редактируя существующее сообщение.
    if callback.message:
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

# =============================================================
# ЗАГОТОВКИ ДЛЯ БУДУЩЕГО РЕДАКТИРОВАНИЯ
# =============================================================

@router.callback_query(F.data == "profile:edit_name")
async def edit_profile_name(
    callback: CallbackQuery,
):
    """
    Пока только заглушка.

    На следующем этапе здесь будет FSM:

        Нажал "Изменить имя"
                    ↓
        Бот просит новое имя
                    ↓
        Пользователь вводит имя
                    ↓
        Сохраняем users.display_name
                    ↓
        Возвращаем профиль
    """

    await callback.answer(
        "Редактирование имени сделаем следующим этапом 🙂",
        show_alert=True,
    )


@router.callback_query(F.data == "profile:edit_title")
async def edit_profile_title(
    callback: CallbackQuery,
):
    """
    Заглушка для будущего редактирования Title.
    """

    await callback.answer(
        "Редактирование Title сделаем следующим этапом 🙂",
        show_alert=True,
    )


@router.callback_query(F.data == "profile:edit_bio")
async def edit_profile_bio(
    callback: CallbackQuery,
):
    """
    Заглушка для будущего поля "О себе".
    """

    await callback.answer(
        "Поле «О себе» сделаем следующим этапом 🙂",
        show_alert=True,
    )


@router.callback_query(F.data == "profile:edit_skills")
async def edit_profile_skills(
    callback: CallbackQuery,
):
    """
    Заглушка для системы навыков.
    """

    await callback.answer(
        "Навыки сделаем отдельным этапом 🙂",
        show_alert=True,
    )


@router.callback_query(F.data == "profile:edit_rate")
async def edit_profile_rate(
    callback: CallbackQuery,
):
    """
    Заглушка для почасовой ставки.
    """

    await callback.answer(
        "Ставку сделаем отдельным этапом 🙂",
        show_alert=True,
    )


@router.callback_query(F.data == "profile:reviews")
async def profile_reviews(
    callback: CallbackQuery,
):
    """
    Заглушка для системы отзывов.

    Позже здесь появится:
        ⭐ рейтинг
        💬 список отзывов
        👤 автор отзыва
        📄 текст
        ◀️ ▶️ пагинация
    """

    await callback.answer(
        "Систему отзывов сделаем позже 🙂",
        show_alert=True,
    )
