"""5주차: Router 레이어 — async + 배치 엔드포인트 추가.

4주차와 달라지는 점:
  1. async def    — 라우터 함수가 모두 비동기가 됩니다.
  2. get_db()     — 동기 SessionLocal → async with AsyncSessionLocal()
  3. /summarize   — Form 방식 → JSON 방식, 입력이 url 로 바뀝니다.
  4. /summarize/batch — 여러 URL 을 동시에 처리하는 신규 엔드포인트입니다.

왜 async def 가 필요한가?
  Service 함수들이 모두 async def 이므로, 라우터도 async def 여야
  await 를 쓸 수 있습니다. 동기 라우터 안에서는 await 가 동작하지 않습니다.

실습: TODO [1]~[5]를 순서대로 채우세요.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import database, schemas
from app.services import summary_service

router = APIRouter()


# TODO [1] 비동기 DB 세션 의존성 함수를 만드세요.
#
#   4주차(동기):
#     def get_db():
#         db = database.SessionLocal()
#         try:
#             yield db
#         finally:
#             db.close()
#
#   5주차(비동기): async with 컨텍스트 매니저를 씁니다.
#   AsyncSessionLocal 이 __aexit__ 에서 세션을 자동으로 닫아 줍니다.
#
#   힌트:
#     async def get_db():
#         async with database.AsyncSessionLocal() as db:
#             yield db
async def get_db():
    raise NotImplementedError("TODO [1]")


# TODO [2] POST /summarize 엔드포인트를 구현하세요.
#
#   4주차에서 달라지는 점:
#     - Form 방식 → JSON 방식 (body: schemas.SummaryRequest)
#     - def → async def
#     - summary_service.create_summary(body, db) → await summary_service.create_summary(body, db)
#
#   힌트:
#     @router.post("/summarize", response_model=schemas.SummaryResponseWithId)
#     async def summarize(
#         body: schemas.SummaryRequest,
#         db: AsyncSession = Depends(get_db),
#     ) -> schemas.SummaryResponseWithId:
#         return await summary_service.create_summary(body, db)


# TODO [3] GET /summaries 엔드포인트를 구현하세요.
#
#   힌트:
#     @router.get("/summaries", response_model=list[schemas.SummaryListItem])
#     async def list_summaries(db: AsyncSession = Depends(get_db)):
#         return await summary_service.list_summaries(db)


# TODO [4] GET /summaries/{id} 엔드포인트를 구현하세요.
#
#   힌트:
#     @router.get("/summaries/{id}", response_model=schemas.SummaryDetailResponse)
#     async def get_summary(id: int, db: AsyncSession = Depends(get_db)):
#         return await summary_service.get_summary(id, db)


# TODO [5] POST /summarize/batch 엔드포인트를 구현하세요.
#
#   여러 URL 을 한꺼번에 받아 동시에 처리합니다.
#   ※ /summarize/batch 를 /summarize/{id} 보다 위에 두어야 합니다.
#      FastAPI 는 경로를 위에서부터 매칭하기 때문에 "batch" 가 id 로 해석될 수 있습니다.
#      (지금은 GET /summarize/batch 가 아니라 POST 이므로 문제없지만, 습관을 들이세요.)
#
#   힌트:
#     @router.post("/summarize/batch", response_model=schemas.BatchSummaryResponse)
#     async def batch_summarize(
#         body: schemas.BatchSummaryRequest,
#         db: AsyncSession = Depends(get_db),
#     ) -> schemas.BatchSummaryResponse:
#         return await summary_service.create_batch(body, db)
