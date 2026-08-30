from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from sqlalchemy import select

from database.database import SessionLocal
from database.models import User, FreelancerProfile

from keyboards.profile import freelancer_profile_menu

from locales import t


router = Router()


# ============================================================
# СОСТОЯНИЯ
# ============================================================


class FreelancerProfileState(StatesGroup):

    waiting_for_title = State()

    waiting_for_bio = State()

    waiting_for_skills = State()

    waiting_for_rate = State()

    waiting_for_experience = State()


# ============================================================
# МОЙ ПРОФИЛЬ
# ============================================================


@router.callback_query(
    F.data == "freelancer:profile"
)
async def show_freelancer_profile(
    callback: CallbackQuery,
):

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id
                == callback.from_user.id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:

            await callback.answer(
                "User not found",
                show_alert=True,
            )

            return

        language = user.language or "ru"

        result = await session.execute(
            select(FreelancerProfile).where(
                FreelancerProfile.user_id
                == user.id
            )
        )

        profile = result.scalar_one_or_none()

    # --------------------------------------------------------
    # Профиль отсутствует
    # --------------------------------------------------------

    if profile is None:

        if language == "en":

            text = (
                "👤 <b>My profile</b>\n\n"
                f"<b>{user.display_name}</b>\n"
                f"@{user.username or '—'}\n\n"
                "Your freelancer profile is not "
                "filled in yet."
            )

        else:

            text = (
                "👤 <b>Мой профиль</b>\n\n"
                f"<b>{user.display_name}</b>\n"
                f"@{user.username or '—'}\n\n"
                "Ваш профиль фрилансера "
                "ещё не заполнен."
            )

        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=freelancer_profile_menu(
                language
            ),
        )

        await callback.answer()

        return

    # --------------------------------------------------------
    # Профиль существует
    # --------------------------------------------------------

    if language == "en":

        text = (
            "👤 <b>My freelancer profile</b>\n\n"
            f"<b>{user.display_name}</b>\n"
            f"@{user.username or '—'}\n\n"
            f"💻 <b>{profile.title or 'Not specified'}</b>\n\n"
            f"📝 {profile.bio or 'No description'}\n\n"
            f"🛠 <b>Skills:</b>\n"
            f"{profile.skills or 'Not specified'}\n\n"
            f"💰 <b>Rate:</b> "
            f"{profile.hourly_rate or '—'} €/hour\n\n"
            f"📈 <b>Experience:</b> "
            f"{profile.experience or 'Not specified'}"
        )

    else:

        text = (
            "👤 <b>Мой профиль фрилансера</b>\n\n"
            f"<b>{user.display_name}</b>\n"
            f"@{user.username or '—'}\n\n"
            f"💻 <b>{profile.title or 'Не указано'}</b>\n\n"
            f"📝 {profile.bio or 'Описание отсутствует'}\n\n"
            f"🛠 <b>Навыки:</b>\n"
            f"{profile.skills or 'Не указаны'}\n\n"
            f"💰 <b>Ставка:</b> "
            f"{profile.hourly_rate or '—'} €/час\n\n"
            f"📈 <b>Опыт:</b> "
            f"{profile.experience or 'Не указан'}"
        )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=freelancer_profile_menu(
            language
        ),
    )

    await callback.answer()


# ============================================================
# НАЧАЛО ЗАПОЛНЕНИЯ ПРОФИЛЯ
# ============================================================


@router.callback_query(
    F.data == "profile:edit"
)
async def start_profile_edit(
    callback: CallbackQuery,
    state: FSMContext,
):

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id
                == callback.from_user.id
            )
        )

        user = result.scalar_one_or_none()

    if user is None:

        await callback.answer(
            "User not found",
            show_alert=True,
        )

        return

    language = user.language or "ru"

    if language == "en":

        text = (
            "💻 <b>Your specialization</b>\n\n"
            "For example:\n"
            "Frontend Developer\n"
            "Telegram Bot Developer\n"
            "UI/UX Designer\n"
            "Video Editor"
        )

    else:

        text = (
            "💻 <b>Ваша специализация</b>\n\n"
            "Например:\n"
            "Frontend Developer\n"
            "Telegram Bot Developer\n"
            "UI/UX Designer\n"
            "Video Editor"
        )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
    )

    await state.set_state(
        FreelancerProfileState.waiting_for_title
    )

    await callback.answer()


# ============================================================
# СПЕЦИАЛИЗАЦИЯ
# ============================================================


@router.message(
    FreelancerProfileState.waiting_for_title
)
async def process_title(
    message: Message,
    state: FSMContext,
):

    title = message.text.strip()

    if len(title) < 2:

        await message.answer(
            "Слишком короткое название."
        )

        return

    await state.update_data(
        title=title
    )

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id
                == message.from_user.id
            )
        )

        user = result.scalar_one()

        language = user.language or "ru"

    if language == "en":

        text = (
            "📝 <b>Tell us about yourself</b>\n\n"
            "Describe your experience and "
            "what you can do for clients."
        )

    else:

        text = (
            "📝 <b>Расскажите о себе</b>\n\n"
            "Опишите ваш опыт и то, "
            "что вы можете предложить заказчикам."
        )

    await message.answer(
        text,
        parse_mode="HTML",
    )

    await state.set_state(
        FreelancerProfileState.waiting_for_bio
    )


# ============================================================
# BIO
# ============================================================


@router.message(
    FreelancerProfileState.waiting_for_bio
)
async def process_bio(
    message: Message,
    state: FSMContext,
):

    bio = message.text.strip()

    if len(bio) < 10:

        await message.answer(
            "Описание слишком короткое."
        )

        return

    await state.update_data(
        bio=bio
    )

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id
                == message.from_user.id
            )
        )

        user = result.scalar_one()

        language = user.language or "ru"

    if language == "en":

        text = (
            "🛠 <b>Your skills</b>\n\n"
            "Write your main skills separated "
            "by commas.\n\n"
            "Example:\n"
            "Python, Aiogram, PostgreSQL, Docker"
        )

    else:

        text = (
            "🛠 <b>Ваши навыки</b>\n\n"
            "Напишите основные навыки через запятую.\n\n"
            "Например:\n"
            "Python, Aiogram, PostgreSQL, Docker"
        )

    await message.answer(
        text,
        parse_mode="HTML",
    )

    await state.set_state(
        FreelancerProfileState.waiting_for_skills
    )


# ============================================================
# SKILLS
# ============================================================


@router.message(
    FreelancerProfileState.waiting_for_skills
)
async def process_skills(
    message: Message,
    state: FSMContext,
):

    skills = message.text.strip()

    if len(skills) < 2:

        await message.answer(
            "Укажите хотя бы один навык."
        )

        return

    await state.update_data(
        skills=skills
    )

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id
                == message.from_user.id
            )
        )

        user = result.scalar_one()

        language = user.language or "ru"

    if language == "en":

        text = (
            "💰 <b>Your hourly rate</b>\n\n"
            "Enter your rate in euros.\n\n"
            "Example: 20"
        )

    else:

        text = (
            "💰 <b>Ваша почасовая ставка</b>\n\n"
            "Укажите стоимость в евро.\n\n"
            "Например: 20"
        )

    await message.answer(
        text,
        parse_mode="HTML",
    )

    await state.set_state(
        FreelancerProfileState.waiting_for_rate
    )


# ============================================================
# RATE
# ============================================================


@router.message(
    FreelancerProfileState.waiting_for_rate
)
async def process_rate(
    message: Message,
    state: FSMContext,
):

    try:

        rate = int(message.text.strip())

    except ValueError:

        await message.answer(
            "Введите число. Например: 20"
        )

        return

    if rate <= 0:

        await message.answer(
            "Ставка должна быть больше 0."
        )

        return

    if rate > 10000:

        await message.answer(
            "Слишком большая ставка."
        )

        return

    await state.update_data(
        hourly_rate=rate
    )

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id
                == message.from_user.id
            )
        )

        user = result.scalar_one()

        language = user.language or "ru"

    if language == "en":

        text = (
            "📈 <b>Your experience</b>\n\n"
            "How many years of experience "
            "do you have?"
        )

    else:

        text = (
            "📈 <b>Ваш опыт</b>\n\n"
            "Сколько лет опыта у вас?"
        )

    await message.answer(
        text,
        parse_mode="HTML",
    )

    await state.set_state(
        FreelancerProfileState.waiting_for_experience
    )


# ============================================================
# EXPERIENCE
# ============================================================


@router.message(
    FreelancerProfileState.waiting_for_experience
)
async def process_experience(
    message: Message,
    state: FSMContext,
):

    experience = message.text.strip()

    if len(experience) < 1:

        await message.answer(
            "Укажите ваш опыт."
        )

        return

    data = await state.get_data()

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id
                == message.from_user.id
            )
        )

        user = result.scalar_one()

        language = user.language or "ru"

        # ----------------------------------------------------
        # Ищем существующий профиль
        # ----------------------------------------------------

        result = await session.execute(
            select(FreelancerProfile).where(
                FreelancerProfile.user_id
                == user.id
            )
        )

        profile = result.scalar_one_or_none()

        # ----------------------------------------------------
        # Если профиля нет — создаём
        # ----------------------------------------------------

        if profile is None:

            profile = FreelancerProfile(
                user_id=user.id,
            )

            session.add(profile)

        # ----------------------------------------------------
        # Сохраняем данные
        # ----------------------------------------------------

        profile.title = data["title"]

        profile.bio = data["bio"]

        profile.skills = data["skills"]

        profile.hourly_rate = data["hourly_rate"]

        profile.experience = experience

        await session.commit()

    await state.clear()

    # --------------------------------------------------------
    # Готово
    # --------------------------------------------------------

    if language == "en":

        text = (
            "🎉 <b>Your profile is ready!</b>\n\n"
            "Clients can now see your freelancer "
            "profile and contact you through "
            "FreelanceHub."
        )

    else:

        text = (
            "🎉 <b>Ваш профиль готов!</b>\n\n"
            "Теперь заказчики смогут видеть ваш "
            "профиль фрилансера и находить вас "
            "через FreelanceHub."
        )

    await message.answer(
        text,
        parse_mode="HTML",
    )

    # --------------------------------------------------------
    # Показываем профиль
    # --------------------------------------------------------

    if language == "en":

        profile_text = (
            "👤 <b>My freelancer profile</b>\n\n"
            f"<b>{user.display_name}</b>\n"
            f"@{user.username or '—'}\n\n"
            f"💻 <b>{data['title']}</b>\n\n"
            f"📝 {data['bio']}\n\n"
            f"🛠 <b>Skills:</b>\n"
            f"{data['skills']}\n\n"
            f"💰 <b>Rate:</b> "
            f"{data['hourly_rate']} €/hour\n\n"
            f"📈 <b>Experience:</b> "
            f"{experience}"
        )

    else:

        profile_text = (
            "👤 <b>Мой профиль фрилансера</b>\n\n"
            f"<b>{user.display_name}</b>\n"
            f"@{user.username or '—'}\n\n"
            f"💻 <b>{data['title']}</b>\n\n"
            f"📝 {data['bio']}\n\n"
            f"🛠 <b>Навыки:</b>\n"
            f"{data['skills']}\n\n"
            f"💰 <b>Ставка:</b> "
            f"{data['hourly_rate']} €/час\n\n"
            f"📈 <b>Опыт:</b> "
            f"{experience}"
        )

    await message.answer(
        profile_text,
        parse_mode="HTML",
        reply_markup=freelancer_profile_menu(
            language
        ),
    )