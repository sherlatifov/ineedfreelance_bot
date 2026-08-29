from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select

from database.database import SessionLocal
from database.models import User


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    telegram_user = message.from_user

    async with SessionLocal() as session:

        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_user.id
            )
        )

        user = result.scalar_one_or_none()

        if user is None:

            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
            )

            session.add(user)

            await session.commit()

            await message.answer(
                "👋 Добро пожаловать в IneedFreelance!\n\n"
                "Ваш аккаунт успешно создан."
            )

        else:

            await message.answer(
                "👋 С возвращением!"
            )