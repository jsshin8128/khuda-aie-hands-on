"""5주차 정답: aiosqlite 비동기 SQLite 연결."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./summary.db"

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 커밋 후 객체를 expired 상태로 두지 않음 (async에서 중요)
)

Base = declarative_base()
