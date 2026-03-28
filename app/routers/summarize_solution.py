"""5주차 정답: Router 레이어 — async + 배치 엔드포인트 추가."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import database, schemas
from app.services import summary_service

router = APIRouter()


async def get_db():
    """요청마다 비동기 DB 세션을 열고, 응답 후 닫습니다."""
    async with database.AsyncSessionLocal() as db:
        yield db


@router.post("/summarize", response_model=schemas.SummaryResponseWithId)
async def summarize(
    body: schemas.SummaryRequest,
    db: AsyncSession = Depends(get_db),
) -> schemas.SummaryResponseWithId:
    return await summary_service.create_summary(body, db)


@router.post("/summarize/batch", response_model=schemas.BatchSummaryResponse)
async def batch_summarize(
    body: schemas.BatchSummaryRequest,
    db: AsyncSession = Depends(get_db),
) -> schemas.BatchSummaryResponse:
    return await summary_service.create_batch(body, db)


@router.get("/summaries", response_model=list[schemas.SummaryListItem])
async def list_summaries(db: AsyncSession = Depends(get_db)) -> list[schemas.SummaryListItem]:
    return await summary_service.list_summaries(db)


@router.get("/summaries/{id}", response_model=schemas.SummaryDetailResponse)
async def get_summary(id: int, db: AsyncSession = Depends(get_db)) -> schemas.SummaryDetailResponse:
    return await summary_service.get_summary(id, db)
