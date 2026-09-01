from sqlalchemy import select

from config import ADMIN_TELEGRAM_ID
from database.database import SessionLocal
from database.models import User


# ============================================================
# GET USER
# ============================================================

async def get_user(
    telegram_id: int,
) -> User | None:

    async with SessionLocal() as session:

        # ----------------------------------------------------
        # Ищем пользователя
        # ----------------------------------------------------

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        # ----------------------------------------------------
        # Пользователь не найден
        # ----------------------------------------------------

        if user is None:
            return None

        # ====================================================
        # Проверяем администратора по Telegram ID
        # ====================================================

        should_be_admin = (
            telegram_id == ADMIN_TELEGRAM_ID
        )

        # ----------------------------------------------------
        # Если статус изменился — сохраняем его
        # ----------------------------------------------------

        if user.is_admin != should_be_admin:

            user.is_admin = should_be_admin

            await session.commit()

            await session.refresh(user)

        return user


# ============================================================
# CREATE USER
# ============================================================

async def create_user(
    telegram_id: int,
    username: str | None,
    language: str = "ru",
) -> User:

    async with SessionLocal() as session:

        # ----------------------------------------------------
        # Определяем администратора
        # ----------------------------------------------------

        is_admin = (
            telegram_id == ADMIN_TELEGRAM_ID
        )

        # ----------------------------------------------------
        # Создаём пользователя
        # ----------------------------------------------------

        user = User(
            telegram_id=telegram_id,
            username=username,
            language=language,
            display_name=None,
            role=None,
            is_admin=is_admin,
        )

        session.add(user)

        # ----------------------------------------------------
        # Сохраняем в PostgreSQL
        # ----------------------------------------------------

        await session.commit()

        # ----------------------------------------------------
        # Получаем актуальные данные из БД
        # ----------------------------------------------------

        await session.refresh(user)

        return user


# ============================================================
# UPDATE USERNAME
# ============================================================

async def update_username(
    telegram_id: int,
    username: str | None,
) -> User | None:

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return None
        
        # ----------------------------------------------------
        # Обновляем username
        # ----------------------------------------------------

        user.username = username

        await session.commit()
        await session.refresh(user)

        return user

# ============================================================
# UPDATE LANGUAGE
# ============================================================

async def update_language(
    telegram_id: int,
    language: str,
) -> User | None:

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return None

        # ----------------------------------------------------
        # Сохраняем язык
        # ----------------------------------------------------

        user.language = language

        await session.commit()
        await session.refresh(user)

        return user

# ============================================================
# UPDATE DISPLAY NAME
# ============================================================

async def update_display_name(
    telegram_id: int,
    display_name: str,
) -> User | None:

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return None

        # ----------------------------------------------------
        # Сохраняем имя
        # ----------------------------------------------------

        user.display_name = display_name

        await session.commit()
        await session.refresh(user)

        return user

# ============================================================
# UPDATE ROLE
# ============================================================

async def update_role(
    telegram_id: int,
    role: str,
) -> User | None:
    """
    Изменяет текущий режим пользователя.

    Допустимые значения:

        freelancer
        client
    """

    if role not in (
        "freelancer",
        "client",
    ):
        raise ValueError(
            f"Invalid role: {role}"
        )

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return None

        user.role = role

        await session.commit()

        await session.refresh(user)

        return user

# ============================================================
# IS ADMIN
# ============================================================

def is_admin(
    telegram_id: int,
) -> bool:
    """
    Проверяет администратора напрямую по Telegram ID.

    Это не зависит от значения is_admin в PostgreSQL.

    Главный администратор определяется через:

        ADMIN_TELEGRAM_ID
    """

    return telegram_id == ADMIN_TELEGRAM_ID

# ============================================================
# GET ADMIN STATUS
# ============================================================

async def get_admin_status(
    telegram_id: int,
) -> bool:
    """
    Возвращает актуальный статус администратора.

    Проверка выполняется по Telegram ID.
    """

    return is_admin(telegram_id)