"""4주차 정답: Router 레이어 — HTTP 요청 수신 및 Service 위임."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import database, schemas
from app.services import summary_service

router = APIRouter()


def get_db():
    """요청마다 DB 세션을 열고, 응답 후 닫습니다 (FastAPI Depends 패턴)."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/summarize", response_model=schemas.SummaryResponseWithId)
def summarize(body: schemas.SummaryRequest, db: Session = Depends(get_db)) -> schemas.SummaryResponseWithId:
    return summary_service.create_summary(body, db)


@router.get("/summaries", response_model=list[schemas.SummaryListItem])
def list_summaries(db: Session = Depends(get_db)) -> list[schemas.SummaryListItem]:
    return summary_service.list_summaries(db)


@router.get("/summaries/{id}", response_model=schemas.SummaryDetail)
def get_summary(id: int, db: Session = Depends(get_db)) -> schemas.SummaryDetail:
    return summary_service.get_summary(id, db)
