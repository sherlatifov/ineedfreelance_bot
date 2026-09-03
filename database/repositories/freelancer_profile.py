from sqlalchemy import select

from database.database import SessionLocal
from database.models import FreelancerProfile


async def get_freelancer_profile(
    user_id: int,
) -> FreelancerProfile | None:
    """
    Получает профиль фрилансера по ID пользователя.

    Важно:
    user_id — это ID из таблицы users,
    а НЕ telegram_id.

    Например:

        users.id = 15
        users.telegram_id = 123456789

    Тогда сюда передаём:

        user_id=15
    """

    async with SessionLocal() as session:

        # Ищем FreelancerProfile,
        # у которого user_id совпадает с переданным ID.
        result = await session.execute(
            select(FreelancerProfile).where(
                FreelancerProfile.user_id == user_id
            )
        )

        # Получаем объект профиля.
        profile = result.scalar_one_or_none()

        return profile


async def get_or_create_freelancer_profile(
    user_id: int,
) -> FreelancerProfile:
    """
    Получает профиль фрилансера.

    Если профиля ещё нет —
    создаёт его.

    user_id — это users.id,
    а не Telegram ID.
    """

    async with SessionLocal() as session:

        # Сначала ищем существующий профиль.
        result = await session.execute(
            select(FreelancerProfile).where(
                FreelancerProfile.user_id == user_id
            )
        )

        profile = result.scalar_one_or_none()

        # Если профиль уже существует —
        # возвращаем его.
        if profile is not None:
            return profile

        # -----------------------------------------------------
        # ПРОФИЛЯ НЕТ
        # -----------------------------------------------------

        # Создаём новый FreelancerProfile.
        profile = FreelancerProfile(
            user_id=user_id,
        )

        # Добавляем объект в текущую сессию.
        session.add(profile)

        # Сохраняем в PostgreSQL.
        await session.commit()

        # Обновляем объект данными из БД.
        await session.refresh(profile)

        return profile


async def update_freelancer_title(
    user_id: int,
    title: str,
) -> FreelancerProfile | None:
    """
    Изменяет Title фрилансера.

    user_id:
        ID пользователя из users.id.

    title:
        новый профессиональный заголовок.

    Возвращает:
        FreelancerProfile
        или None, если профиль не найден.
    """

    async with SessionLocal() as session:

        # Ищем профиль.
        result = await session.execute(
            select(FreelancerProfile).where(
                FreelancerProfile.user_id == user_id
            )
        )

        profile = result.scalar_one_or_none()

        # Если профиля нет —
        # ничего обновлять.
        if profile is None:
            return None

        # Обновляем Title.
        profile.title = title

        # Сохраняем изменение.
        await session.commit()

        # Получаем актуальное состояние объекта.
        await session.refresh(profile)

        return profile


async def update_freelancer_bio(
    user_id: int,
    bio: str,
) -> FreelancerProfile | None:
    """
    Изменяет информацию «О себе» у фрилансера.

    user_id:
        ID пользователя из users.id.

    bio:
        новый текст «О себе».

    Возвращает:
        FreelancerProfile
        или None, если профиль не найден.
    """

    async with SessionLocal() as session:

        # -----------------------------------------------------
        # ИЩЕМ ПРОФИЛЬ
        # -----------------------------------------------------

        result = await session.execute(
            select(FreelancerProfile).where(
                FreelancerProfile.user_id == user_id
            )
        )

        profile = result.scalar_one_or_none()

        # Если профиль не найден —
        # возвращаем None.
        if profile is None:
            return None

        # -----------------------------------------------------
        # ОБНОВЛЯЕМ BIO
        # -----------------------------------------------------

        profile.bio = bio

        # Сохраняем изменение в PostgreSQL.
        await session.commit()

        # Обновляем объект актуальными данными из БД.
        await session.refresh(profile)

        return profile