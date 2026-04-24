"""5주차: Controller 레이어 — async + 배치 엔드포인트 추가.

4주차와 달라지는 점:
  1. async def    — 컨트롤러 함수가 모두 비동기가 됩니다.
  2. get_db()     — 동기 SessionLocal → async with AsyncSessionLocal()
  3. /summarize   — 입력이 url(Form) 로 바뀝니다.
  4. /summarize/batch — 여러 URL 을 동시에 처리하는 신규 엔드포인트입니다.

왜 async def 가 필요한가?
  Service 함수들이 모두 async def 이므로, 컨트롤러도 async def 여야
  await 를 쓸 수 있습니다. 동기 컨트롤러 안에서는 await 가 동작하지 않습니다.

실습: TODO [1]~[5]를 순서대로 채우세요.
"""

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection as database
from app.dto.summary_request_dto import BatchSummaryRequest, SummaryRequest
from app.dto.summary_response_dto import (
    BatchSummaryResponse,
    SummaryDetailResponse,
    SummaryListItem,
    SummaryResponseWithId,
)
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
    async with database.AsyncSessionLocal() as db:
        yield db


@router.post("/summarize", response_model=SummaryResponseWithId)
async def summarize(
    url: str = Form(...),
    output_format: str = Form("json"),
    db: AsyncSession = Depends(get_db),
) -> SummaryResponseWithId:
    body = SummaryRequest(url=url, output_format=output_format)
    return await summary_service.create_summary(body, db)


@router.post("/summarize/batch", response_model=BatchSummaryResponse)
async def batch_summarize(
    urls: list[str] = Form(...),
    output_format: str = Form("json"),
    db: AsyncSession = Depends(get_db),
) -> BatchSummaryResponse:
    body = BatchSummaryRequest(urls=urls, output_format=output_format)
    return await summary_service.create_batch(body, db)


@router.get("/summaries", response_model=list[SummaryListItem])
async def list_summaries(db: AsyncSession = Depends(get_db)) -> list[SummaryListItem]:
    return await summary_service.list_summaries(db)


@router.get("/summaries/{id}", response_model=SummaryDetailResponse)
async def get_summary(id: int, db: AsyncSession = Depends(get_db)) -> SummaryDetailResponse:
    return await summary_service.get_summary(id, db)
