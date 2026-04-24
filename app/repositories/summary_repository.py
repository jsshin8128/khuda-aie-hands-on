"""5주차: Repository 레이어 — 비동기 DB 접근.

4주차와 달라지는 점:
  - 함수들이 모두 async def 가 됩니다.
  - Session → AsyncSession
  - db.commit() → await db.commit()
  - db.query() 대신 select() + await db.execute() 를 씁니다.

왜 db.query() 를 못 쓰나?
  SQLAlchemy 2.0 비동기 모드에서는 db.query() 가 지원되지 않습니다.
  대신 select() 로 쿼리를 만들고 await db.execute() 로 실행합니다.

실습: TODO [1]~[3]을 채우세요.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import summary as models


async def save(db: AsyncSession, row: models.Summary) -> models.Summary:
    db.add(row)
    await db.commit()
    await db.refresh(row)
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
