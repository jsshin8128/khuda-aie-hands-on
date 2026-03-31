"""5주차 정답: Controller 레이어 — async + 배치 엔드포인트 추가."""

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


async def get_db():
    """요청마다 비동기 DB 세션을 열고, 응답 후 닫습니다."""
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
