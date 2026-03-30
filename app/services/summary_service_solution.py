"""5주차 정답: Service 레이어 — URL 크롤링 + 비동기 LLM 호출."""

import asyncio
import json
from datetime import datetime, timezone

import httpx
import trafilatura
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
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

# 프롬프트 v2.0: recommended_for, difficulty, read_time 세 필드 추가
# {{ }} 는 프롬프트 문자열 안에서 리터럴 중괄호를 표현하는 이스케이프입니다.
_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """블로그 글을 읽고 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 순수 JSON만 반환하세요.

{{
  "recommended_for": "이런 분께 추천 (예: Python 입문자)",
  "difficulty": "초급",
  "read_time": 8,
  "summary": "2~3문장 핵심 요약",
  "key_points": ["포인트 1", "포인트 2", "포인트 3"]
}}

difficulty 는 반드시 "초급", "중급", "고급" 중 하나만 사용하세요.
read_time 은 원문을 읽는 데 걸리는 예상 시간(정수, 분 단위)입니다.""",
    ),
    ("user", "제목: {title}\n\n내용:\n{content_text}"),
])

# temperature=0: 출력을 최대한 고정해 JSON 파싱 실패를 줄입니다.
_LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


async def fetch_url(url: str) -> tuple[str, str | None]:
    """URL 을 크롤링해 (본문 텍스트, 제목) 를 반환합니다.

    httpx 는 requests 와 거의 동일하지만 async 를 지원합니다.
    trafilatura 는 광고·메뉴 같은 노이즈를 제거하고 본문만 추출합니다.
    """
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()  # 4xx / 5xx 면 httpx.HTTPStatusError 발생

    html = response.text
    content_text = trafilatura.extract(html) or ""
    metadata = trafilatura.extract_metadata(html)
    title = metadata.title if metadata else None
    return content_text, title


def _created_at_to_iso(created_at: str) -> str:
    """SQLite '2024-01-01 00:00:00' → API '2024-01-01T00:00:00Z'"""
    return created_at.replace(" ", "T", 1) + "Z" if created_at and " " in created_at else (created_at or "")


async def create_summary(body: SummaryRequest, db: AsyncSession) -> SummaryResponseWithId:
    # ① URL 크롤링
    content_text, title = await fetch_url(body.url)

    # ② LLM 호출 (ainvoke = invoke 의 async 버전. 대기 중 다른 요청 처리 가능)
    chain = _PROMPT | _LLM
    result = await chain.ainvoke({"title": title or "", "content_text": content_text})

    # ③ JSON 파싱
    data = json.loads(result.content)

    # ④ Pydantic 검증: 필드가 빠지거나 타입이 다르면 여기서 에러가 납니다.
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    response = SummaryResponse(
        recommended_for=data["recommended_for"],
        difficulty=data["difficulty"],
        read_time=data["read_time"],
        summary=data["summary"],
        key_points=data["key_points"],
        meta=SummaryMeta(prompt_version="v2.0", generated_at=now),
    )

    # ⑤ DB 저장
    row = models.Summary(
        url=body.url,
        title=title,
        content_text=content_text,
        output_json=json.dumps(response.model_dump()),
        prompt_version=response.meta.prompt_version,
    )
    await summary_repository.save(db, row)

    # ⑥ id 를 포함해 반환
    return SummaryResponseWithId(id=row.id, **response.model_dump())


async def list_summaries(db: AsyncSession) -> list[SummaryListItem]:
    rows = await summary_repository.list_all(db)
    return [
        SummaryListItem(id=r.id, title=r.title, url=r.url or "")
        for r in rows
    ]


async def get_summary(id: int, db: AsyncSession) -> SummaryDetailResponse:
    row = await summary_repository.get_by_id(db, id)
    if not row:
        raise HTTPException(status_code=404, detail="Summary not found")

    data = json.loads(row.output_json)
    return SummaryDetailResponse(
        id=row.id,
        title=row.title,
        url=row.url or "",
        content_text=row.content_text,
        recommended_for=data["recommended_for"],
        difficulty=data["difficulty"],
        read_time=data["read_time"],
        summary=data["summary"],
        key_points=data["key_points"],
        meta=SummaryMeta(**data["meta"]),
        created_at=_created_at_to_iso(row.created_at),
    )


async def create_batch(body: BatchSummaryRequest, db: AsyncSession) -> BatchSummaryResponse:
    """여러 URL 을 asyncio.gather 로 동시에 처리합니다.

    return_exceptions=True: 하나가 실패해도 나머지는 계속 실행됩니다.
    실패한 URL 은 failed 에, 성공한 URL 은 results 에 담겨 반환됩니다.
    """
    async def process_one(url: str) -> SummaryResponseWithId:
        single_body = SummaryRequest(url=url, output_format=body.output_format)
        return await create_summary(single_body, db)

    tasks = [process_one(url) for url in body.urls]
    outcomes = await asyncio.gather(*tasks, return_exceptions=True)

    results, failed = [], []
    for url, outcome in zip(body.urls, outcomes):
        if isinstance(outcome, Exception):
            failed.append({"url": url, "error": str(outcome)})
        else:
            results.append(outcome)

    return BatchSummaryResponse(results=results, failed=failed)
