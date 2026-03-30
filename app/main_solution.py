"""5주차 정답: 진입점 — 비동기 테이블 생성."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import connection as database
from app.domain import summary as models
from app.controllers.summary_controller_solution import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 비동기 엔진에서는 run_sync 를 통해 동기 함수(create_all)를 실행합니다.
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


app = FastAPI(
    title="AIE_hands-on",
    description="테크 블로그 요약 서버 - 5주 커리큘럼",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(router)
