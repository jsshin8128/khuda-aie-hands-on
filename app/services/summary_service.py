"""5주차: Service 레이어 — URL 크롤링 + 비동기 LLM 호출.

4주차와 달라지는 점:
  1. fetch_url()     — httpx 로 URL 을 크롤링해 본문 텍스트를 추출합니다.
  2. 프롬프트 v2.0   — recommended_for, difficulty, read_time 세 필드가 추가됩니다.
  3. async def      — 모든 함수가 비동기가 됩니다.
  4. ainvoke()      — chain.invoke() → await chain.ainvoke()
  5. create_batch() — asyncio.gather 로 여러 URL 을 동시에 처리합니다.

흐름 (단건):
  URL 수신 → fetch_url() 크롤링 → ainvoke() LLM 호출 → Pydantic 검증 → DB 저장 → 반환

흐름 (배치):
  URLs 수신 → asyncio.gather(*[process_one(url) for url in urls]) → results + failed 분리 → 반환

실습: TODO [1]~[7]을 순서대로 채우세요.
"""

import asyncio
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import summary as models
from app.dto.summary_request_dto import BatchSummaryRequest, SummaryRequest
from app.dto.summary_response_dto import (
    BatchSummaryResponse,
    SummaryDetailResponse,
    SummaryListItem,
    SummaryMeta,
    SummaryResponse,
    SummaryResponseWithId,
)
from app.repositories import summary_repository

load_dotenv()


# TODO [1] fetch_url() 을 구현하세요.
#
#   URL 을 받아 페이지 HTML 을 내려받고, trafilatura 로 본문 텍스트와 제목을 추출합니다.
#   (본문, 제목) 튜플을 반환합니다. 제목 추출에 실패하면 None 을 반환합니다.
#
#   httpx.AsyncClient 사용법:
#     async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
#         response = await client.get(url)
#         response.raise_for_status()  # 4xx / 5xx 면 예외 발생
#
#   trafilatura 사용법:
#     import trafilatura
#     content_text = trafilatura.extract(html) or ""
#     metadata = trafilatura.extract_metadata(html)
#     title = metadata.title if metadata else None
#
#   힌트:
#     async def fetch_url(url: str) -> tuple[str, str | None]:
#         import httpx, trafilatura
#         async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
#             response = await client.get(url)
#             response.raise_for_status()
#         html = response.text
#         content_text = trafilatura.extract(html) or ""
#         metadata = trafilatura.extract_metadata(html)
#         title = metadata.title if metadata else None
#         return content_text, title
async def fetch_url(url: str) -> tuple[str, str | None]:
    raise NotImplementedError("TODO [1]")


# TODO [2] 프롬프트 템플릿을 정의하세요 (버전 v2.0).
#
#   4주차 프롬프트에서 recommended_for, difficulty, read_time 세 필드가 추가됩니다.
#   LLM 이 아래 JSON 형식으로만 응답하도록 지시하세요.
#
#   {
#     "recommended_for": "이런 분께 추천 (예: Python 입문자)",
#     "difficulty": "초급",
#     "read_time": 8,
#     "summary": "2~3문장 핵심 요약",
#     "key_points": ["포인트 1", "포인트 2", "포인트 3"]
#   }
#
#   ※ difficulty 는 "초급", "중급", "고급" 중 하나만 사용합니다.
#   ※ read_time 은 정수(분)입니다.
#   ※ 프롬프트 문자열 안에서 리터럴 중괄호 { } 는 {{ }} 로 이스케이프합니다.
#
#   힌트:
#     from langchain.prompts import ChatPromptTemplate
#     _PROMPT = ChatPromptTemplate.from_messages([
#         ("system", "..."),
#         ("user", "제목: {title}\n\n내용:\n{content_text}"),
#     ])
_PROMPT = None  # TODO [2]


# TODO [3] LLM 을 초기화하세요. 4주차와 동일합니다.
#
#   힌트:
#     from langchain_openai import ChatOpenAI
#     _LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
_LLM = None  # TODO [3]


def _created_at_to_iso(created_at: str) -> str:
    """SQLite '2024-01-01 00:00:00' → API '2024-01-01T00:00:00Z'"""
    return created_at.replace(" ", "T", 1) + "Z" if created_at and " " in created_at else (created_at or "")


async def create_summary(body: SummaryRequest, db: AsyncSession) -> SummaryResponseWithId:
    # TODO [4] URL 크롤링 → LLM 호출 → Pydantic 검증 → DB 저장 → 반환
    #
    #   ① URL 크롤링
    #      content_text, title = await fetch_url(body.url)
    #
    #   ② LLM 호출 (ainvoke = invoke 의 async 버전)
    #      chain = _PROMPT | _LLM
    #      result = await chain.ainvoke({"title": title or "", "content_text": content_text})
    #
    #   ③ JSON 파싱
    #      data = json.loads(result.content)
    #
    #   ④ Pydantic 검증
    #      now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    #      response = SummaryResponse(
    #          recommended_for=data["recommended_for"],
    #          difficulty=data["difficulty"],
    #          read_time=data["read_time"],
    #          summary=data["summary"],
    #          key_points=data["key_points"],
    #          meta=SummaryMeta(prompt_version="v2.0", generated_at=now),
    #      )
    #
    #   ⑤ DB 저장
    #      row = models.Summary(
    #          url=body.url,
    #          title=title,
    #          content_text=content_text,
    #          output_json=json.dumps(response.model_dump()),
    #          prompt_version=response.meta.prompt_version,
    #      )
    #      await summary_repository.save(db, row)
    #
    #   ⑥ id 를 포함해 반환
    #      return SummaryResponseWithId(id=row.id, **response.model_dump())
    raise NotImplementedError("TODO [4]")


async def list_summaries(db: AsyncSession) -> list[SummaryListItem]:
    # TODO [5] 전체 목록을 조회해 SummaryListItem 리스트로 변환하세요.
    #
    #   4주차와 달리 created_at 대신 url 을 반환합니다.
    #
    #   힌트:
    #     rows = await summary_repository.list_all(db)
    #     return [
    #         SummaryListItem(id=r.id, title=r.title, url=r.url or "")
    #         for r in rows
    #     ]
    raise NotImplementedError("TODO [5]")


async def get_summary(id: int, db: AsyncSession) -> SummaryDetailResponse:
    # TODO [6] id 로 단건을 조회하세요.
    #
    #   힌트:
    #     row = await summary_repository.get_by_id(db, id)
    #     if not row:
    #         raise HTTPException(status_code=404, detail="Summary not found")
    #
    #     data = json.loads(row.output_json)
    #     return SummaryDetailResponse(
    #         id=row.id,
    #         title=row.title,
    #         url=row.url or "",
    #         content_text=row.content_text,
    #         recommended_for=data["recommended_for"],
    #         difficulty=data["difficulty"],
    #         read_time=data["read_time"],
    #         summary=data["summary"],
    #         key_points=data["key_points"],
    #         meta=SummaryMeta(**data["meta"]),
    #         created_at=_created_at_to_iso(row.created_at),
    #     )
    raise NotImplementedError("TODO [6]")


async def create_batch(body: BatchSummaryRequest, db: AsyncSession) -> BatchSummaryResponse:
    # TODO [7] 여러 URL 을 asyncio.gather 로 동시에 처리하세요.
    #
    #   핵심 아이디어:
    #     - 각 URL 에 대해 create_summary 를 호출하는 코루틴 목록을 만듭니다.
    #     - asyncio.gather(*tasks, return_exceptions=True) 로 동시 실행합니다.
    #     - 예외가 발생한 URL 은 failed 에, 성공한 URL 은 results 에 담습니다.
    #
    #   힌트:
    #     async def process_one(url: str):
    #         single_body = SummaryRequest(url=url, output_format=body.output_format)
    #         return await create_summary(single_body, db)
    #
    #     tasks = [process_one(url) for url in body.urls]
    #     outcomes = await asyncio.gather(*tasks, return_exceptions=True)
    #
    #     results, failed = [], []
    #     for url, outcome in zip(body.urls, outcomes):
    #         if isinstance(outcome, Exception):
    #             failed.append({"url": url, "error": str(outcome)})
    #         else:
    #             results.append(outcome)
    #
    #     return BatchSummaryResponse(results=results, failed=failed)
    raise NotImplementedError("TODO [7]")
