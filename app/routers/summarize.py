"""4주차: Router 레이어 — HTTP 요청 수신 및 Service 위임.

Router 의 역할은 단 하나입니다.
  "HTTP 요청을 받아서 Service 함수를 호출하고, 결과를 그대로 반환한다."

비즈니스 로직은 여기에 없습니다. if/else, json.loads, LLM 호출 — 전부 Service 에 있습니다.
Router 가 얇을수록 테스트와 유지보수가 쉬워집니다.

실습: TODO [1]~[4]를 순서대로 채우세요.
"""

# TODO [1] APIRouter 를 생성하세요.
#
#   APIRouter 는 FastAPI 앱을 여러 파일로 나눌 때 사용합니다.
#   완성한 router 는 main.py 에서 app.include_router(router) 로 등록합니다.
#
#   힌트:
#     from fastapi import APIRouter
#     router = APIRouter()

from fastapi import Depends
from sqlalchemy.orm import Session

from app import database, schemas
from app.services import summary_service


def get_db():
    """요청마다 DB 세션을 열고, 응답 후 닫습니다 (FastAPI Depends 패턴)."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# TODO [2] POST /summarize 엔드포인트를 구현하세요.
#
#   Router 에서 할 일은 딱 한 줄입니다:
#     return summary_service.create_summary(body, db)
#
#   힌트:
#     @router.post("/summarize", response_model=schemas.SummaryResponseWithId)
#     def summarize(body: schemas.SummaryRequest, db: Session = Depends(get_db)):
#         return summary_service.create_summary(body, db)


# TODO [3] GET /summaries 엔드포인트를 구현하세요.
#
#   힌트:
#     @router.get("/summaries", response_model=list[schemas.SummaryListItem])
#     def list_summaries(db: Session = Depends(get_db)):
#         return summary_service.list_summaries(db)


# TODO [4] GET /summaries/{id} 엔드포인트를 구현하세요.
#          경로 변수 id 는 함수 파라미터로 자동 바인딩됩니다.
#
#   힌트:
#     @router.get("/summaries/{id}", response_model=schemas.SummaryDetail)
#     def get_summary(id: int, db: Session = Depends(get_db)):
#         return summary_service.get_summary(id, db)
