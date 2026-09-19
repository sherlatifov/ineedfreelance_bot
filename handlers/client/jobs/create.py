import html

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest

from database.repositories.category import get_categories, get_category
from database.repositories.job import create_job
from database.repositories.user import get_user

from handlers.client.jobs.states import CreateJobStates

from keyboards.categories import categories_keyboard
from keyboards.client_menu import client_menu
from keyboards.job import (
    budget_keyboard,
    deadline_keyboard,
    files_keyboard,
    preview_keyboard,
    main_menu_keyboard,
)


router = Router()


# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================================================

async def delete_user_message(message: Message):
    """
    Удаляем сообщение пользователя после обработки.
    Если удалить нельзя — просто продолжаем работу.
    """
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def edit_form(
    message: Message,
    state: FSMContext,
    prompt: str,
    reply_markup=None,
):
    """
    Редактирует одно и то же сообщение формы.
    """

    data = await state.get_data()

    category = data.get("category_name")
    title = data.get("title")
    description = data.get("description")

    budget = data.get("budget")
    currency = data.get("currency")
    deadline = data.get("deadline")

    # -----------------------------------------------------
    # Категория
    # -----------------------------------------------------

    category_text = (
        html.escape(str(category))
        if category
        else "—"
    )

    # -----------------------------------------------------
    # Название
    # -----------------------------------------------------

    title_text = (
        html.escape(str(title))
        if title
        else "—"
    )

    # -----------------------------------------------------
    # Описание
    # -----------------------------------------------------

    description_text = (
        html.escape(str(description))
        if description
        else "—"
    )

    # -----------------------------------------------------
    # Бюджет
    # -----------------------------------------------------

    if budget is None:
        if currency == "NEGOTIABLE":
            budget_text = "Договорной"
        else:
            budget_text = "—"
    else:
        currency_names = {
            "USD": "🇺🇸 USD",
            "EUR": "🇪🇺 EUR",
            "RUB": "🇷🇺 RUB",
            "STARS": "⭐ Telegram Stars",
        }

        currency_name = currency_names.get(
            currency,
            currency or "",
        )

        budget_text = (
            f"{html.escape(str(budget))} "
            f"{currency_name}"
        )

    # -----------------------------------------------------
    # Срок
    # -----------------------------------------------------

    deadline_text = (
        html.escape(str(deadline))
        if deadline
        else "—"
    )

    # -----------------------------------------------------
    # Файлы
    # -----------------------------------------------------

    files = data.get("files", [])

    if files:
        files_text = f"{len(files)} файл(ов)"
    else:
        files_text = "—"

    # -----------------------------------------------------
    # ФОРМА
    # -----------------------------------------------------

    text = (
        "📝 <b>Создание работы</b>\n\n"

        f"📂 <b>Категория:</b> {category_text}\n"
        f"📝 <b>Название:</b> {title_text}\n"
        f"📄 <b>Описание:</b> {description_text}\n"
        f"💰 <b>Бюджет:</b> {budget_text}\n"
        f"⏱ <b>Срок:</b> {deadline_text}\n"
        f"📎 <b>Файлы:</b> {files_text}\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n\n"

        f"{prompt}"
    )

    try:
        await message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as e:
        # Например, если текст фактически не изменился
        if "message is not modified" not in str(e):
            raise


async def edit_form_by_id(
    message: Message,
    state: FSMContext,
    prompt: str,
    reply_markup=None,
):
    """
    Редактирует сохранённое сообщение формы.
    """

    data = await state.get_data()

    form_message_id = data.get("form_message_id")

    if not form_message_id:
        return

    # Используем bot напрямую, потому что здесь
    # message — это уже сообщение пользователя.
    await edit_form(
        message=message.bot.get_message
        if False
        else message,
        state=state,
        prompt=prompt,
        reply_markup=reply_markup,
    )


# =========================================================
# НАЧАЛО СОЗДАНИЯ РАБОТЫ
# =========================================================

@router.callback_query(F.data == "client:create_project")
async def start_create_job(
    callback: CallbackQuery,
    state: FSMContext,
):
    categories = await get_categories()

    if not categories:
        await callback.answer(
            "❌ Категории пока не настроены.",
            show_alert=True,
        )
        return

    await state.clear()

    # Запоминаем ID одного сообщения,
    # которое будем использовать как форму.
    await state.update_data(
        form_message_id=callback.message.message_id,
        files=[],
    )

    await state.set_state(
        CreateJobStates.choosing_category
    )

    await callback.message.edit_text(
        "📝 <b>Создание работы</b>\n\n"

        "📂 <b>Категория:</b> —\n"
        "📝 <b>Название:</b> —\n"
        "📄 <b>Описание:</b> —\n"
        "💰 <b>Бюджет:</b> —\n"
        "⏱ <b>Срок:</b> —\n"
        "📎 <b>Файлы:</b> —\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n\n"

        "📂 <b>Выберите категорию работы:</b>",
        parse_mode="HTML",
        reply_markup=categories_keyboard(
            categories,
            language="ru",
        ),
    )

    await callback.answer()


# =========================================================
# ВЫБОР КАТЕГОРИИ
# =========================================================

@router.callback_query(
    CreateJobStates.choosing_category,
    F.data.startswith("category:")
)
async def choose_category(
    callback: CallbackQuery,
    state: FSMContext,
):
    category_id = int(
        callback.data.split(":")[1]
    )

    category = await get_category(category_id)

    if not category:
        await callback.answer(
            "Категория не найдена.",
            show_alert=True,
        )
        return

    await state.update_data(
        category_id=category.id,
        category_name=category.name_ru,
    )

    await state.set_state(
        CreateJobStates.entering_title
    )

    await edit_form(
        callback.message,
        state,
        "📝 <b>Введите название работы:</b>\n\n"
        "Например:\n"
        "<i>Разработать Telegram-бота на Python</i>",
    )

    await callback.answer()


# =========================================================
# НАЗВАНИЕ
# =========================================================

@router.message(CreateJobStates.entering_title)
async def enter_title(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await delete_user_message(message)

        data = await state.get_data()
        form_message_id = data.get("form_message_id")

        if form_message_id:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=form_message_id,
                text=(
                    "📝 <b>Создание работы</b>\n\n"
                    "❌ Название нужно отправить текстом."
                ),
                parse_mode="HTML",
            )

        return

    title = message.text.strip()

    if len(title) < 5:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Название слишком короткое.</b>\n\n"
            "Введите минимум 5 символов.",
        )
        return

    if len(title) > 200:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Название слишком длинное.</b>\n\n"
            "Максимум — 200 символов.",
        )
        return

    await state.update_data(
        title=title
    )

    await state.set_state(
        CreateJobStates.entering_description
    )

    await delete_user_message(message)

    await edit_form(
        message,
        state,
        "📄 <b>Введите описание работы:</b>\n\n"
        "Расскажите, что нужно сделать, "
        "какой результат вы ожидаете и есть ли "
        "особые требования.",
    )


# =========================================================
# ОПИСАНИЕ
# =========================================================

@router.message(CreateJobStates.entering_description)
async def enter_description(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Описание нужно отправить текстом.</b>",
        )
        return

    description = message.text.strip()

    if len(description) < 20:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Описание слишком короткое.</b>\n\n"
            "Опишите работу подробнее — минимум 20 символов.",
        )
        return

    await state.update_data(
        description=description
    )

    await state.set_state(
        CreateJobStates.choosing_currency
    )

    await delete_user_message(message)

    await edit_form(
        message,
        state,
        "💰 <b>Выберите валюту бюджета:</b>\n\n"
        "После выбора валюты бот попросит указать сумму.",
        reply_markup=budget_keyboard(),
    )


# =========================================================
# ВЫБОР ВАЛЮТЫ
# =========================================================

@router.callback_query(
    CreateJobStates.choosing_currency,
    F.data.startswith("job_currency:")
)
async def choose_currency(
    callback: CallbackQuery,
    state: FSMContext,
):
    currency = callback.data.split(":")[1]

    currency_names = {
        "USD": "🇺🇸 USD",
        "EUR": "🇪🇺 EUR",
        "RUB": "🇷🇺 RUB",
        "STARS": "⭐ Telegram Stars",
    }

    currency_name = currency_names.get(
        currency,
        currency,
    )

    await state.update_data(
        currency=currency
    )

    await state.set_state(
        CreateJobStates.entering_budget
    )

    await edit_form(
        callback.message,
        state,
        f"💰 <b>Введите бюджет в {currency_name}:</b>\n\n"
        "Например: <code>500</code>",
    )

    await callback.answer()


# =========================================================
# ДОГОВОРНОЙ БЮДЖЕТ
# =========================================================

@router.callback_query(
    CreateJobStates.choosing_currency,
    F.data == "job_budget:negotiable"
)
async def budget_negotiable(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.update_data(
        budget=None,
        currency="NEGOTIABLE",
    )

    await state.set_state(
        CreateJobStates.choosing_deadline
    )

    await edit_form(
        callback.message,
        state,
        "⏱ <b>Выберите срок выполнения:</b>",
        reply_markup=deadline_keyboard(),
    )

    await callback.answer()


# =========================================================
# БЮДЖЕТ
# =========================================================

@router.message(CreateJobStates.entering_budget)
async def enter_budget(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Введите сумму числом.</b>\n\n"
            "Например: <code>500</code>",
        )
        return

    text = message.text.strip().replace(",", ".")

    try:
        budget = float(text)
    except ValueError:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Неверная сумма.</b>\n\n"
            "Введите число, например:\n"
            "<code>500</code>",
        )
        return

    if budget <= 0:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Сумма должна быть больше нуля.</b>",
        )
        return

    await state.update_data(
        budget=budget
    )

    await state.set_state(
        CreateJobStates.choosing_deadline
    )

    await delete_user_message(message)

    await edit_form(
        message,
        state,
        "⏱ <b>Какой срок выполнения?</b>",
        reply_markup=deadline_keyboard(),
    )


# =========================================================
# СРОК — ДОГОВОРНОЙ
# =========================================================

@router.callback_query(
    CreateJobStates.choosing_deadline,
    F.data == "job_deadline:negotiable"
)
async def deadline_negotiable(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.update_data(
        deadline="Договорной"
    )

    await state.set_state(
        CreateJobStates.uploading_files
    )

    await edit_form(
        callback.message,
        state,
        "📎 <b>Добавьте файлы</b>, если они нужны.\n\n"
        "Например: ТЗ, изображения, документы.\n\n"
        "Если файлы не нужны — нажмите "
        "«Пропустить».",
        reply_markup=files_keyboard(),
    )

    await callback.answer()


# =========================================================
# СРОК — УКАЗАТЬ ВРУЧНУЮ
# =========================================================

@router.callback_query(
    CreateJobStates.choosing_deadline,
    F.data == "job_deadline:custom"
)
async def deadline_custom(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(
        CreateJobStates.choosing_deadline
    )

    await edit_form(
        callback.message,
        state,
        "📅 <b>Введите срок выполнения:</b>\n\n"
        "Например:\n"
        "<code>7 дней</code>\n"
        "<code>до 15 октября</code>\n"
        "<code>30 сентября</code>",
    )

    await callback.answer()


# =========================================================
# СРОК — ТЕКСТ
# =========================================================

@router.message(CreateJobStates.choosing_deadline)
async def enter_deadline(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Укажите срок текстом.</b>\n\n"
            "Например: <code>7 дней</code>",
        )
        return

    deadline = message.text.strip()

    if len(deadline) < 2:
        await delete_user_message(message)

        await edit_form(
            message,
            state,
            "❌ <b>Укажите срок подробнее.</b>",
        )
        return

    await state.update_data(
        deadline=deadline
    )

    await state.set_state(
        CreateJobStates.uploading_files
    )

    await delete_user_message(message)

    await edit_form(
        message,
        state,
        "📎 <b>Добавьте файлы</b>, если они нужны.\n\n"
        "Например: ТЗ, изображения, документы.\n\n"
        "Если файлы не нужны — нажмите "
        "«Пропустить».",
        reply_markup=files_keyboard(),
    )


# =========================================================
# ФАЙЛЫ — ПРОПУСТИТЬ
# =========================================================

@router.callback_query(
    CreateJobStates.uploading_files,
    F.data == "job_files:skip"
)
async def skip_files(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.update_data(
        files=[]
    )

    await state.set_state(
        CreateJobStates.preview
    )

    await show_preview(
        callback.message,
        state,
    )

    await callback.answer()


# =========================================================
# ПРЕДПРОСМОТР
# =========================================================

async def show_preview(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()

    # -----------------------------------------------------
    # БЮДЖЕТ
    # -----------------------------------------------------

    if data.get("budget") is None:
        budget_text = "Договорной"
    else:
        currency_names = {
            "USD": "USD",
            "EUR": "EUR",
            "RUB": "RUB",
            "STARS": "⭐ Stars",
        }

        currency = currency_names.get(
            data.get("currency"),
            data.get("currency", ""),
        )

        budget_text = (
            f"{data['budget']} {currency}"
        )

    # -----------------------------------------------------
    # ФАЙЛЫ
    # -----------------------------------------------------

    files = data.get("files", [])

    if files:
        files_text = f"{len(files)} файл(ов)"
    else:
        files_text = "отсутствуют"

    # -----------------------------------------------------
    # ТЕКСТ
    # -----------------------------------------------------

    text = (
        "📋 <b>Предпросмотр работы</b>\n\n"

        f"📂 <b>Категория:</b>\n"
        f"{html.escape(str(data.get('category_name', '—')))}\n\n"

        f"📝 <b>Название:</b>\n"
        f"{html.escape(str(data.get('title', '—')))}\n\n"

        f"📄 <b>Описание:</b>\n"
        f"{html.escape(str(data.get('description', '—')))}\n\n"

        f"💰 <b>Бюджет:</b>\n"
        f"{html.escape(str(budget_text))}\n\n"

        f"⏳ <b>Срок:</b>\n"
        f"{html.escape(str(data.get('deadline', '—')))}\n\n"

        f"📎 <b>Файлы:</b> {files_text}"
    )

    await message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=preview_keyboard(),
    )


# =========================================================
# ОПУБЛИКОВАТЬ
# =========================================================

@router.callback_query(
    CreateJobStates.preview,
    F.data == "job_preview:publish"
)
async def publish_job(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()

    user = await get_user(
        callback.from_user.id
    )

    if user is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    job = await create_job(
        client_id=user.id,
        category_id=data["category_id"],
        title=data["title"],
        description=data["description"],
        budget=data.get("budget"),
        currency=data.get("currency"),
        deadline=data.get("deadline"),
    )

    await state.clear()

    await callback.message.edit_text(
        "✅ <b>Работа опубликована!</b>\n\n"

        f"📝 {html.escape(job.title)}\n\n"

        "Теперь её смогут найти фрилансеры.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )

    await callback.answer()


# =========================================================
# ОТМЕНА
# =========================================================

@router.callback_query(
    F.data == "job_create:cancel"
)
async def cancel_create_job(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.clear()

    await callback.message.edit_text(
        "❌ <b>Создание работы отменено.</b>",
        parse_mode="HTML",
    )

    await callback.answer()


# =========================================================
# ВОЗВРАЩЕНИЕ В ГЛАВНОЕ МЕНЮ
# =========================================================

@router.callback_query(
    F.data == "client:main_menu"
)
async def client_main_menu(
    callback: CallbackQuery,
):
    user = await get_user(
        callback.from_user.id
    )

    if user is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    language = user.language or "ru"
    admin = user.is_admin

    await callback.message.edit_text(
        "👤 <b>Меню заказчика</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=client_menu(
            language=language,
            is_admin=admin,
        ),
    )

    await callback.answer()