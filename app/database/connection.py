"""5주차: aiosqlite 비동기 SQLite 연결.

4주차 database.py 와 비교해 두 가지가 바뀝니다.
  1. 연결 드라이버: sqlite://  →  sqlite+aiosqlite://
  2. 엔진·세션:    create_engine / SessionLocal
                  → create_async_engine / AsyncSessionLocal

왜 바꾸나?
  동기 엔진(create_engine)에서는 db.commit() 같은 DB 작업이 이벤트 루프를 블로킹합니다.
  aiosqlite 드라이버 + 비동기 엔진을 쓰면 DB 작업 중에도 다른 요청을 처리할 수 있습니다.

실습: TODO [1]~[2]를 채우세요.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./summary.db"

# TODO [1] 비동기 엔진을 생성하세요.
#
#   동기: create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
#   비동기: create_async_engine 을 씁니다. connect_args 는 필요 없습니다.
#
#   힌트:
#     engine = create_async_engine(DATABASE_URL)
engine = None  # TODO [1]


# TODO [2] 비동기 세션 팩토리를 만드세요.
#
#   동기:   SessionLocal = sessionmaker(bind=engine)
#   비동기: class_=AsyncSession 을 지정합니다.
#          expire_on_commit=False 를 주면 커밋 후 객체를 다시 로드하지 않아도 됩니다.
#
#   힌트:
#     AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
AsyncSessionLocal = None  # TODO [2]


# declarative_base 는 동기와 동일합니다. 변경 없음.
Base = declarative_base()
