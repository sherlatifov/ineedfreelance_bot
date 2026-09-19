from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.repositories.category import get_categories, get_category
from database.repositories.job import create_job
from database.repositories.user import get_user

from handlers.client.jobs.states import CreateJobStates

from keyboards.categories import categories_keyboard
from keyboards.job import (
    budget_keyboard,
    currency_keyboard,
    deadline_keyboard,
    files_keyboard,
    preview_keyboard,
)


router = Router()


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
        await message.answer(
            "❌ Категории пока не настроены."
        )
        return

    await state.clear()

    await state.set_state(
        CreateJobStates.choosing_category
    )

    await callback.message.edit_text(
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

    await callback.message.edit_text(
        f"📂 Категория: <b>{category.name_ru}</b>\n\n"
        "📝 Теперь введите <b>название работы</b>.\n\n"
        "Например:\n"
        "<i>Разработать Telegram-бота на Python</i>"
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
        await message.answer(
            "❌ Пожалуйста, отправьте название текстом."
        )
        return

    title = message.text.strip()

    if len(title) < 5:
        await message.answer(
            "❌ Название слишком короткое.\n\n"
            "Введите название минимум из 5 символов."
        )
        return

    if len(title) > 200:
        await message.answer(
            "❌ Название слишком длинное.\n\n"
            "Максимум — 200 символов."
        )
        return

    await state.update_data(
        title=title
    )

    await state.set_state(
        CreateJobStates.entering_description
    )

    await message.answer(
        "📄 Теперь подробно опишите работу.\n\n"
        "Расскажите, что нужно сделать, "
        "какой результат вы ожидаете и есть ли "
        "особые требования."
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
        await message.answer(
            "❌ Пожалуйста, отправьте описание текстом."
        )
        return

    description = message.text.strip()

    if len(description) < 20:
        await message.answer(
            "❌ Описание слишком короткое.\n\n"
            "Опишите работу подробнее — минимум 20 символов."
        )
        return

    await state.update_data(
        description=description
    )

    await state.set_state(
        CreateJobStates.entering_budget
    )

    await message.answer(
        "💰 Введите бюджет работы.\n\n"
        "Например:\n"
        "<code>500</code>\n\n"
        "Или выберите «Договорной».",
        reply_markup=budget_keyboard(),
    )


# =========================================================
# БЮДЖЕТ
# =========================================================

@router.message(CreateJobStates.entering_budget)
async def enter_budget(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer(
            "❌ Введите бюджет числом."
        )
        return

    text = message.text.strip().replace(",", ".")

    try:
        budget = float(text)
    except ValueError:
        await message.answer(
            "❌ Введите бюджет числом.\n\n"
            "Например: <code>500</code>\n\n"
            "Или выберите «Договорной».",
            reply_markup=budget_keyboard(),
        )
        return

    if budget <= 0:
        await message.answer(
            "❌ Бюджет должен быть больше нуля."
        )
        return

    await state.update_data(
        budget=budget
    )

    await state.set_state(
        CreateJobStates.choosing_currency
    )

    await message.answer(
        "💵 Выберите валюту:",
        reply_markup=currency_keyboard(),
    )


# =========================================================
# ДОГОВОРНОЙ БЮДЖЕТ
# =========================================================

@router.callback_query(
    CreateJobStates.entering_budget,
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

    await callback.message.edit_text(
        "💰 Бюджет: <b>Договорной</b>\n\n"
        "⏳ Теперь выберите срок выполнения:",
        reply_markup=deadline_keyboard(),
    )

    await callback.answer()


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

    await state.update_data(
        currency=currency
    )

    await state.set_state(
        CreateJobStates.choosing_deadline
    )

    await callback.message.edit_text(
        "⏳ <b>Какой срок выполнения?</b>",
        reply_markup=deadline_keyboard(),
    )

    await callback.answer()


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

    await callback.message.edit_text(
        "📎 <b>Добавьте файлы</b>, если они нужны "
        "для работы.\n\n"
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
    await callback.message.edit_text(
        "📅 Введите срок выполнения.\n\n"
        "Например:\n"
        "<code>7 дней</code>\n"
        "<code>до 15 октября</code>\n"
        "<code>30 сентября</code>"
    )

    await callback.answer()


@router.message(CreateJobStates.choosing_deadline)
async def enter_deadline(
    message: Message,
    state: FSMContext,
):
    if not message.text:
        await message.answer(
            "❌ Укажите срок текстом."
        )
        return

    deadline = message.text.strip()

    if len(deadline) < 2:
        await message.answer(
            "❌ Укажите срок подробнее."
        )
        return

    await state.update_data(
        deadline=deadline
    )

    await state.set_state(
        CreateJobStates.uploading_files
    )

    await message.answer(
        "📎 <b>Добавьте файлы</b>, если они нужны.\n\n"
        "Или нажмите «Пропустить».",
        reply_markup=files_keyboard(),
    )


# =========================================================
# ФАЙЛЫ — ПОКА ПРОПУСТИТЬ
# =========================================================

@router.callback_query(
    CreateJobStates.uploading_files,
    F.data == "job_files:skip"
)
async def skip_files(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(
        CreateJobStates.preview
    )

    await show_preview(
        callback.message,
        state,
        edit=True,
    )

    await callback.answer()


# =========================================================
# ПРЕДПРОСМОТР
# =========================================================

async def show_preview(
    message: Message,
    state: FSMContext,
    edit: bool = False,
):
    data = await state.get_data()

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

    text = (
        "📋 <b>Предпросмотр работы</b>\n\n"

        f"📂 <b>Категория:</b>\n"
        f"{data.get('category_name')}\n\n"

        f"📝 <b>Название:</b>\n"
        f"{data.get('title')}\n\n"

        f"📄 <b>Описание:</b>\n"
        f"{data.get('description')}\n\n"

        f"💰 <b>Бюджет:</b>\n"
        f"{budget_text}\n\n"

        f"⏳ <b>Срок:</b>\n"
        f"{data.get('deadline')}\n\n"

        "📎 <b>Файлы:</b> отсутствуют"
    )

    if edit:
        await message.edit_text(
            text,
            reply_markup=preview_keyboard(),
        )
    else:
        await message.answer(
            text,
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

    # Получаем нашего пользователя по Telegram ID
    user = await get_user(callback.from_user.id)

    if user is None:
        await callback.answer(
            "❌ Пользователь не найден.",
            show_alert=True,
        )
        return

    # В jobs.client_id должен записываться
    # внутренний users.id, а не Telegram ID
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
        f"🆔 Номер работы: <code>#{job.id}</code>\n"
        f"📝 {job.title}\n\n"
        "Теперь её смогут найти фрилансеры."
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
        "❌ Создание работы отменено."
    )

    await callback.answer()