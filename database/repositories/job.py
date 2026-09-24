from sqlalchemy import select

from database.database import SessionLocal
from database.models.job import Job
from database.models.category import Category

async def create_job(
    client_id: int,
    category_id: int,
    title: str,
    description: str,
    budget: float | None,
    currency: str | None,
    deadline: str | None,
) -> Job:

    async with SessionLocal() as session:

        job = Job(
            client_id=client_id,
            category_id=category_id,
            title=title,
            description=description,
            budget=budget,
            currency=currency,
            deadline=deadline,
            status="open",
        )

        session.add(job)

        await session.commit()
        await session.refresh(job)

        return job

async def get_jobs_by_client(
    client_id: int,
) -> list[tuple[Job, Category]]:

    async with SessionLocal() as session:

        result = await session.execute(
            select(Job, Category)
            .join(
                Category,
                Job.category_id == Category.id,
            )
            .where(
                Job.client_id == client_id,
            )
            .order_by(
                Job.created_at.desc(),
            )
        )

        return list(result.all())