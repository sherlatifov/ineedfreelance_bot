from sqlalchemy import select

from database.database import SessionLocal
from database.models.category import Category


CATEGORIES = [
    {
        "name_ru": "Разработка",
        "name_en": "Development",
        "slug": "development",
        "sort_order": 1,
    },
    {
        "name_ru": "Дизайн",
        "name_en": "Design",
        "slug": "design",
        "sort_order": 2,
    },
    {
        "name_ru": "Мобильная разработка",
        "name_en": "Mobile Development",
        "slug": "mobile-development",
        "sort_order": 3,
    },
    {
        "name_ru": "Копирайтинг",
        "name_en": "Copywriting",
        "slug": "copywriting",
        "sort_order": 4,
    },
    {
        "name_ru": "Маркетинг",
        "name_en": "Marketing",
        "slug": "marketing",
        "sort_order": 5,
    },
    {
        "name_ru": "Видео",
        "name_en": "Video",
        "slug": "video",
        "sort_order": 6,
    },
    {
        "name_ru": "Переводы",
        "name_en": "Translation",
        "slug": "translation",
        "sort_order": 7,
    },
    {
        "name_ru": "Другое",
        "name_en": "Other",
        "slug": "other",
        "sort_order": 8,
    },
]


async def seed_categories():
    async with SessionLocal() as session:

        for data in CATEGORIES:

            result = await session.execute(
                select(Category)
                .where(Category.slug == data["slug"])
            )

            existing = result.scalar_one_or_none()

            if existing:
                continue

            category = Category(
                name_ru=data["name_ru"],
                name_en=data["name_en"],
                slug=data["slug"],
                sort_order=data["sort_order"],
                is_active=True,
            )

            session.add(category)

        await session.commit()