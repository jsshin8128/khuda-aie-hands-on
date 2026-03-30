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
    # TODO [1] row 를 DB 에 저장하고 id, created_at 이 채워진 row 를 반환하세요.
    #
    #   4주차(동기):
    #     db.add(row)
    #     db.commit()
    #     db.refresh(row)
    #     return row
    #
    #   5주차(비동기): commit 과 refresh 앞에 await 를 붙입니다.
    #
    #   힌트:
    #     db.add(row)
    #     await db.commit()
    #     await db.refresh(row)
    #     return row
    raise NotImplementedError("TODO [1]")


async def list_all(db: AsyncSession) -> list[models.Summary]:
    # TODO [2] summaries 테이블 전체를 최신순으로 조회하세요.
    #
    #   4주차(동기):
    #     return db.query(Summary).order_by(Summary.created_at.desc()).all()
    #
    #   5주차(비동기): select() 로 쿼리를 만들고 await db.execute() 로 실행합니다.
    #
    #   힌트:
    #     result = await db.execute(
    #         select(models.Summary).order_by(models.Summary.created_at.desc())
    #     )
    #     return result.scalars().all()
    raise NotImplementedError("TODO [2]")


async def get_by_id(db: AsyncSession, id: int) -> models.Summary | None:
    # TODO [3] id 로 단건을 조회하세요. 없으면 None 을 반환합니다.
    #
    #   힌트:
    #     result = await db.execute(
    #         select(models.Summary).filter(models.Summary.id == id)
    #     )
    #     return result.scalar_one_or_none()
    raise NotImplementedError("TODO [3]")
