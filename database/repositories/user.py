from sqlalchemy import select

from config import ADMIN_TELEGRAM_ID
from database.database import SessionLocal
from database.models import User


async def get_user(telegram_id: int) -> User | None:

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()

async def create_user(
    telegram_id: int,
    username: str | None,
    language: str = "ru",
) -> User:

    async with SessionLocal() as session:

        user = User(
            telegram_id=telegram_id,
            username=username,
            language=language,
            is_admin=(
                telegram_id == ADMIN_TELEGRAM_ID
            ),
        )

        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user

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

        user.username = username

        await session.commit()

        return user