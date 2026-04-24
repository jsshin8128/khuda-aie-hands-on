"""5주차: Service 레이어 — URL 크롤링 + 비동기 LLM 호출.

4주차와 달라지는 점:
  1. fetch_url()     — Playwright 로 브라우저를 실행해 JS 렌더링 후 본문을 추출합니다.
  2. 프롬프트 v2.0   — recommended_for, difficulty, read_time 세 필드가 추가됩니다.
  3. async def      — 모든 함수가 비동기가 됩니다.
  4. ainvoke()      — chain.invoke() → await chain.ainvoke()
  5. create_batch() — asyncio.gather 로 여러 URL 을 동시에 처리합니다.

흐름 (단건):
  URL 수신 → fetch_url() 크롤링 → ainvoke() LLM 호출 → Pydantic 검증 → DB 저장 → 반환

흐름 (배치):
  URLs 수신 → asyncio.gather(*[process_one(url) for url in urls]) → results + failed 분리 → 반환
"""

import asyncio
import json
from datetime import datetime, timezone

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


async def fetch_url(url: str) -> tuple[str, str | None]:
    from playwright.async_api import async_playwright
    import trafilatura
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
    content_text = trafilatura.extract(html) or ""
    # null 바이트·제어 문자 제거 — OpenAI API JSON 직렬화 오류 방지
    content_text = "".join(ch for ch in content_text if ch >= " " or ch in "\n\t")
    metadata = trafilatura.extract_metadata(html)
    title = metadata.title if metadata else None
    return content_text, title


# {{ }} 는 프롬프트 문자열 안에서 리터럴 중괄호를 표현하는 이스케이프입니다.
_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """당신은 테크 블로그 전문 에디터입니다. 주어진 글을 깊이 있게 분석하여 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 순수 JSON만 반환하세요.

{{
  "recommended_for": "이 글이 가장 도움이 될 독자층 (예: '비동기 프로그래밍을 처음 접하는 Python 개발자', 'Kubernetes 운영 경험이 있는 DevOps 엔지니어')",
  "difficulty": "초급",
  "read_time": 8,
  "summary": "핵심 주제와 글쓴이의 주장을 3~4문장으로 요약. 단순 나열이 아니라 왜 이 주제가 중요한지, 어떤 문제를 해결하는지, 핵심 결론이 무엇인지를 담아 서술형으로 작성하세요.",
  "key_points": [
    "독자가 바로 적용할 수 있는 구체적인 인사이트 또는 기술 포인트",
    "글에서 다루는 핵심 개념이나 원리 (단순 사실 나열 금지, X를 사용하면 Y가 개선된다처럼 인과관계 포함)",
    "주의해야 할 트레이드오프, 한계, 또는 안티패턴",
    "실무 적용 팁 또는 다음 단계로 참고할 만한 내용",
    "글 전체를 관통하는 핵심 교훈 한 줄"
  ]
}}

각 필드 작성 기준:
- recommended_for: 직군·경험 수준·관심사를 구체적으로 명시하세요.
- difficulty: 반드시 "초급", "중급", "고급" 중 하나만 사용하세요.
- read_time: 성인 평균 독서 속도(분당 500자) 기준으로 계산한 정수(분)입니다.
- summary: 글의 배경→문제→해결책→결론 흐름이 드러나야 합니다. 단순 목차 나열 금지.
- key_points: 반드시 5개, 각 항목은 완전한 문장으로 작성하세요. 독자가 글을 읽지 않아도 핵심을 파악할 수 있을 만큼 구체적이어야 합니다.""",
    ),
    ("user", "제목: {title}\n\n내용:\n{content_text}"),
])

# temperature=0.3: 출력을 최대한 고정해 JSON 파싱 실패를 줄입니다.
_LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


def _created_at_to_iso(created_at: str) -> str:
    """SQLite '2024-01-01 00:00:00' → API '2024-01-01T00:00:00Z'"""
    return created_at.replace(" ", "T", 1) + "Z" if created_at and " " in created_at else (created_at or "")


async def create_summary(body: SummaryRequest, db: AsyncSession) -> SummaryResponseWithId:
    content_text, title = await fetch_url(body.url)

    chain = _PROMPT | _LLM
    result = await chain.ainvoke({"title": title or "", "content_text": content_text})

    data = json.loads(result.content)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    response = SummaryResponse(
        recommended_for=data["recommended_for"],
        difficulty=data["difficulty"],
        read_time=data["read_time"],
        summary=data["summary"],
        key_points=data["key_points"],
        meta=SummaryMeta(prompt_version="v2.0", generated_at=now),
    )

    row = models.Summary(
        url=body.url,
        title=title,
        content_text=content_text,
        output_json=json.dumps(response.model_dump()),
        prompt_version=response.meta.prompt_version,
    )
    await summary_repository.save(db, row)

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
