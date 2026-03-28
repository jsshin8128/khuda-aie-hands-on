"""5주차: 진입점 — 비동기 테이블 생성.

4주차에서 달라지는 점:
  - lifespan 의 테이블 생성이 비동기 방식으로 바뀝니다.
    동기: models.Base.metadata.create_all(bind=database.engine)
    비동기: async with database.engine.begin() as conn:
               await conn.run_sync(models.Base.metadata.create_all)

왜 run_sync 를 쓰나?
  create_all 은 동기 함수입니다. 비동기 컨텍스트에서 동기 함수를 실행할 때
  conn.run_sync() 를 쓰면 이벤트 루프를 블로킹하지 않고 처리할 수 있습니다.

실습: TODO [1]~[2]를 채운 뒤 uvicorn 으로 서버를 실행하세요.
      → scripts/week5.sh 로 동작을 확인합니다.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import database, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO [1] 서버 시작 시 summaries 테이블을 비동기 방식으로 생성하세요.
    #
    #   4주차(동기):
    #     models.Base.metadata.create_all(bind=database.engine)
    #
    #   5주차(비동기):
    #     async with database.engine.begin() as conn:
    #         await conn.run_sync(models.Base.metadata.create_all)
    #
    #   힌트: 위 두 줄이 전부입니다.
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


# TODO [2] Router 를 등록하세요. 4주차와 동일합니다.
#
#   힌트:
#     from app.routers.summarize import router
#     app.include_router(router)
