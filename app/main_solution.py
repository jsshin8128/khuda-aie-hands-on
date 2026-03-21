"""4주차 정답: 레이어드 아키텍처 - 얇아진 진입점."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import database, models
from app.routers.summarize_solution import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=database.engine)
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
