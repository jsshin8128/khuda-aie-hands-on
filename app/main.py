"""
4주차: 레이어드 아키텍처 — 얇아진 진입점.

3주차 main.py 에는 HTTP 처리 · 비즈니스 로직 · DB 접근이 한 파일에 섞여 있었습니다.
4주차에서는 각 책임을 분리합니다.

  main.py         → 앱 생성 + 라우터 등록만 담당  (지금 이 파일)
  routers/        → HTTP 요청 수신 · 응답 반환
  services/       → 비즈니스 로직 · LLM 호출
  repositories/   → DB 접근

외부 API 동작(엔드포인트 경로, 스키마)은 3주차와 완전히 동일합니다.
내부 구조만 바뀌었습니다.

실습: TODO [1]을 채운 뒤 uvicorn 으로 서버를 실행하세요.
      → scripts/week4.sh 로 동작을 확인합니다.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import database, models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 summaries 테이블이 없으면 자동으로 생성합니다.
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


# TODO [1] Router 를 등록하세요.
#
#   routers/summarize.py 에서 만든 router 를 이 앱에 연결합니다.
#   이 한 줄로 POST /summarize, GET /summaries, GET /summaries/{id} 가 모두 활성화됩니다.
#
#   힌트:
#     from app.routers.summarize import router
#     app.include_router(router)
