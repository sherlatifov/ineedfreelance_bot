from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.repositories.user import get_user
from keyboards.profile import freelancer_profile_keyboard


# Router этого конкретного раздела.
router = Router()


async def show_freelancer_profile(
    callback: CallbackQuery,
) -> None:
    """
    Показывает профиль текущего пользователя.

    Эта функция является общей функцией отображения профиля.

    Её смогут использовать:
        - кнопка "Мой профиль";
        - сохранение Title;
        - сохранение Bio;
        - сохранение навыков;
        - сохранение ставки;
        - и т.д.
    """

    # Получаем Telegram ID пользователя.
    telegram_id = callback.from_user.id

    # Получаем пользователя из базы данных.
    user = await get_user(telegram_id)

    # Если пользователь не найден,
    # показываем сообщение об ошибке.
    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    # Получаем язык пользователя.
    language = user.language or "ru"

    # ---------------------------------------------------------
    # ОСНОВНАЯ ИНФОРМАЦИЯ
    # ---------------------------------------------------------

    # Имя берём из таблицы users.
    display_name = user.display_name or "Не указано"

    # ---------------------------------------------------------
    # ВРЕМЕННЫЕ ЗНАЧЕНИЯ
    # ---------------------------------------------------------
    #
    # Сейчас системы отзывов и заказов ещё нет.
    #
    # Поэтому временно показываем:
    #
    # рейтинг     → —
    # отзывы      → 0
    # заказов     → 0
    #
    # Позже эти данные будут приходить из БД.

    rating = "—"
    reviews_count = 0
    completed_orders = 0

    # ---------------------------------------------------------
    # ФОРМИРУЕМ ПРОФИЛЬ
    # ---------------------------------------------------------

    text = (
        f"👨‍💻 <b>Мой профиль</b>\n\n"
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

    # Создаём клавиатуру профиля.
    keyboard = freelancer_profile_keyboard(
        language=language,
    )

    # Убираем индикатор загрузки Telegram.
    await callback.answer()

    # Если сообщение доступно,
    # редактируем его вместо отправки нового.
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