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
from utils.message import (
    delete_message_safely,
    edit_message_safely,
)

router = Router()


class TitleStates(StatesGroup):
    """
    FSM-состояния для редактирования Title.
    """

    waiting_for_title = State()


@router.callback_query(F.data == "profile:edit_title")
async def edit_profile_title(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Начинает редактирование Title.

    Пользователь нажимает:
    💻 Изменить Title

    После этого бот ждёт текстовое сообщение.
    """

    user = await get_user(
        callback.from_user.id
    )

    if user is None:
        await callback.answer(
            "Пользователь не найден.",
            show_alert=True,
        )
        return

    # Сохраняем ID текущего сообщения профиля.
    #
    # Это нужно для того, чтобы после ввода Title
    # мы могли отредактировать именно это сообщение,
    # а не отправлять новое сообщение в чат.
    if callback.message:
        await state.update_data(
            profile_message_id=callback.message.message_id,
        )

    # Переводим пользователя в состояние
    # ожидания нового Title.
    #
    # Пока пользователь находится в этом состоянии,
    # его следующее текстовое сообщение будет
    # обрабатываться функцией process_profile_title().
    await state.set_state(
        TitleStates.waiting_for_title
    )

    await callback.answer()

    if callback.message:
        # Вместо отправки нового сообщения
        # редактируем существующее сообщение профиля.
        #
        # Благодаря этому в чате остаётся только
        # один актуальный экран.
        await callback.message.edit_text(
            "💻 <b>Изменение Title</b>\n\n"
            "Введите ваш профессиональный Title.\n\n"
            "Например:\n"
            "<code>Python Backend Developer</code>\n\n"
            "Максимум — 255 символов.",
            parse_mode="HTML",
        )


@router.message(TitleStates.waiting_for_title)
async def process_profile_title(
    message: Message,
    state: FSMContext,
):
    """
    Получает новый Title от пользователя,
    проверяет его и сохраняет в PostgreSQL.
    """

    # Проверяем, что пользователь отправил текст.
    #
    # Например, пользователь может отправить фотографию,
    # стикер или другой тип сообщения.
    # Для Title нам нужен именно обычный текст.
    if not message.text:
        await message.answer(
            "❌ Пожалуйста, отправьте Title "
            "обычным текстовым сообщением."
        )
        return

    # Убираем пробелы в начале и конце.
    #
    # Например:
    # "  Python Developer  "
    #
    # превратится в:
    # "Python Developer"
    title = message.text.strip()

    # Проверяем минимальную длину.
    if len(title) < 2:
        await message.answer(
            "❌ Title слишком короткий.\n\n"
            "Введите минимум 2 символа."
        )
        return

    # Проверяем максимальную длину.
    #
    # В модели FreelancerProfile поле title
    # имеет String(255), поэтому больше 255 символов
    # в базу записывать нельзя.
    if len(title) > 255:
        await message.answer(
            "❌ Title слишком длинный.\n\n"
            "Максимальная длина — 255 символов."
        )
        return

    # Получаем пользователя.
    #
    # Здесь используется message.from_user,
    # потому что сейчас мы обрабатываем обычное
    # сообщение пользователя, а не CallbackQuery.
    user = await get_user(
        message.from_user.id
    )

    if user is None:
        # Если пользователя больше нет в базе,
        # завершаем FSM, чтобы состояние
        # ожидания Title не осталось активным.
        await state.clear()

        await message.answer(
            "❌ Пользователь не найден.\n\n"
            "Пожалуйста, выполните /start."
        )
        return

    # Проверяем наличие FreelancerProfile.
    #
    # Если профиль ещё не существует,
    # repository создаст его.
    #
    # Если профиль уже существует,
    # существующий профиль просто будет возвращён.
    await get_or_create_freelancer_profile(
        user_id=user.id,
    )

    # Сохраняем Title в PostgreSQL.
    #
    # Repository самостоятельно открывает
    # database session, изменяет profile.title
    # и выполняет commit().
    profile = await update_freelancer_title(
        user_id=user.id,
        title=title,
    )

    if profile is None:
        # Если профиль почему-то не удалось получить,
        # прекращаем редактирование.
        await state.clear()

        await message.answer(
            "❌ Не удалось сохранить Title."
        )
        return

    # Получаем данные, которые мы сохранили
    # при нажатии кнопки «Изменить Title».
    #
    # Нас интересует profile_message_id —
    # ID старого сообщения профиля.
    data = await state.get_data()

    profile_message_id = data.get(
        "profile_message_id"
    )

    # Title успешно сохранён.
    # Выходим из FSM.
    #
    # После этого обычные сообщения пользователя
    # больше не будут восприниматься как Title.
    await state.clear()

    # Удаляем сообщение пользователя,
    # в котором он отправил новый Title.
    #
    # Благодаря этому в чате не останется:
    #
    # Пользователь:
    # Python Backend Developer
    #
    # Сообщение удаляется после успешного сохранения.
    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    # Строим обновлённый профиль.
    #
    # Здесь main.py заново получает данные
    # из PostgreSQL и формирует актуальный текст
    # и клавиатуру профиля.
    result = await build_freelancer_profile_text(
        user_id=user.id,
    )

    if result is None:
        return

    text, keyboard = result

    # Если у нас есть ID старого сообщения профиля,
    # редактируем именно его.
    #
    # В результате пользователь не получает
    # новое сообщение — старый экран просто
    # превращается обратно в обновлённый профиль.
    if profile_message_id is not None:
        updated = await edit_message_safely(
            bot=message.bot,
            chat_id=message.chat.id,
            message_id=profile_message_id,
            text=text,
            reply_markup=keyboard,
        )

        # Если сообщение успешно отредактировано,
        # больше ничего делать не нужно.
        return

    # Это запасной вариант.
    #
    # Если по какой-то причине profile_message_id
    # отсутствует или сообщение невозможно изменить,
    # создаём новый экран профиля.
    await message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard,
    )