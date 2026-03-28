"""5주차 정답: Repository 레이어 — 비동기 DB 접근."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


async def save(db: AsyncSession, row: models.Summary) -> models.Summary:
    db.add(row)
    await db.commit()
    await db.refresh(row)  # DB 가 채운 id, created_at 을 row 에 반영
    return row


async def list_all(db: AsyncSession) -> list[models.Summary]:
    result = await db.execute(
        select(models.Summary).order_by(models.Summary.created_at.desc())
    )
    return result.scalars().all()


async def get_by_id(db: AsyncSession, id: int) -> models.Summary | None:
    result = await db.execute(
        select(models.Summary).filter(models.Summary.id == id)
    )
    return result.scalar_one_or_none()
