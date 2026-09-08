from sqlalchemy import select

from database.database import SessionLocal
from database.models import ClientProfile


async def get_client_profile(
    user_id: int,
) -> ClientProfile | None:
    """Получает профиль клиента по users.id."""

    async with SessionLocal() as session:
        result = await session.execute(
            select(ClientProfile).where(
                ClientProfile.user_id == user_id
            )
        )

        return result.scalar_one_or_none()


async def get_or_create_client_profile(
    user_id: int,
) -> ClientProfile:
    """Получает профиль клиента или создаёт его."""

    async with SessionLocal() as session:
        result = await session.execute(
            select(ClientProfile).where(
                ClientProfile.user_id == user_id
            )
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            profile = ClientProfile(user_id=user_id)

            session.add(profile)

            await session.commit()
            await session.refresh(profile)

        return profile


async def update_client_profile(
    user_id: int,
    **fields,
) -> ClientProfile | None:
    """Обновляет любые поля профиля клиента."""

    if not fields:
        return await get_client_profile(user_id)

    async with SessionLocal() as session:
        result = await session.execute(
            select(ClientProfile).where(
                ClientProfile.user_id == user_id
            )
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            return None

        for field, value in fields.items():
            if not hasattr(profile, field):
                raise ValueError(
                    f"Unknown ClientProfile field: {field}"
                )

            setattr(profile, field, value)

        await session.commit()
        await session.refresh(profile)

        return profile