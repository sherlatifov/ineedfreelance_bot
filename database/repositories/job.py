from database.database import SessionLocal
from database.models.job import Job


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