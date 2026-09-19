from sqlalchemy import select

from database.models.category import Category
from database.database import SessionLocal


async def get_categories():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.sort_order, Category.id)
        )

        return result.scalars().all()


async def get_category(category_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Category)
            .where(
                Category.id == category_id,
                Category.is_active == True
            )
        )

        return result.scalar_one_or_none()


async def get_category_by_slug(slug: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Category)
            .where(
                Category.slug == slug,
                Category.is_active == True
            )
        )

        return result.scalar_one_or_none()