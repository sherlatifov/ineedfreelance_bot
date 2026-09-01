from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t
from keyboards.common import back_button


def freelancer_profile_keyboard(
    language: str,
) -> InlineKeyboardMarkup:

    """
    Клавиатура профиля фрилансера.

    Здесь мы только создаём кнопки.
    Логика того, что произойдёт после нажатия,
    находится в handlers/profile.py.
    """

    # Создаём конструктор Inline-клавиатуры.
    builder = InlineKeyboardBuilder()

    # ---------------------------------------------------------
    # РЕДАКТИРОВАНИЕ ПРОФИЛЯ
    # ---------------------------------------------------------

    # Изменение имени.
    #
    # Важно:
    # имя уже хранится в таблице users в поле display_name.
    # Поэтому отдельное поле для имени фрилансера
    # нам создавать НЕ нужно.

    builder.button(
        text=t(language, "edit_name"),
        callback_data="profile:edit_name",
    )

    # Изменение профессионального заголовка.
    builder.button(
        text=t(language, "edit_title"),
        callback_data="profile:edit_title",
    )

    # Изменение информации "О себе".
    builder.button(
        text=t(language, "edit_bio"),
        callback_data="profile:edit_bio",
    )

    # Изменение специализаций".
    builder.button(
        text=t(language, "edit_specializations"),
        callback_data="profile:edit_specials",
    )

    # Управление навыками.
    builder.button(
        text=t(language, "edit_skills"),
        callback_data="profile:edit_skills",
    )

    # Изменение данных об опыте
    builder.button(
        text=t(language, "edit_experience"),
        callback_data="profile:edit_experience",
    )

    # Изменение почасовой ставки.
    builder.button(
        text=t(language, "edit_rate"),
        callback_data="profile:edit_rate",
    )

    # ---------------------------------------------------------
    # ОТЗЫВЫ
    # ---------------------------------------------------------

    # Пока система отзывов ещё не реализована.
    #
    # Но кнопку создаём уже сейчас.
    # Когда мы дойдём до отзывов, этот callback
    # будет открывать список отзывов.
    builder.button(
        text="💬 Читать отзывы",
        callback_data="profile:reviews",
    )

    # ---------------------------------------------------------
    # НАЗАД
    # ---------------------------------------------------------

    # Очень важная кнопка.
    #
    # Пока она возвращает пользователя
    # в режим фрилансера.
    #
    # Позже мы сделаем полноценную систему навигации,
    # и эта кнопка сможет возвращать именно
    # на предыдущий экран.
    builder.button(
        text="⬅️ Назад",
        callback_data="profile:back",
    )
    
    builder.adjust(1)

    return builder.as_markup()