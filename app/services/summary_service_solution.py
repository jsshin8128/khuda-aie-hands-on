"""4주차 정답: Service 레이어 — 비즈니스 로직 + LangChain 연동."""

import json
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories import summary_repository

load_dotenv()

# 프롬프트 템플릿: {title}, {content_text} 는 invoke() 시점에 채워집니다.
# {{ }} 는 프롬프트 문자열 안에서 리터럴 중괄호를 표현하는 이스케이프입니다.
_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """블로그 글을 읽고 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 순수 JSON만 반환하세요.

{{
  "summary": "2~3문장 핵심 요약",
  "key_points": ["포인트 1", "포인트 2", "포인트 3"]
}}""",
    ),
    ("user", "제목: {title}\n\n내용:\n{content_text}"),
])

# temperature=0: 출력을 최대한 고정해 JSON 파싱 실패를 줄입니다.
_LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _created_at_to_iso(created_at: str) -> str:
    """SQLite '2024-01-01 00:00:00' → API '2024-01-01T00:00:00Z'"""
    return created_at.replace(" ", "T", 1) + "Z" if created_at and " " in created_at else (created_at or "")


def create_summary(body: schemas.SummaryRequest, db: Session) -> schemas.SummaryResponseWithId:
    # ① LLM 호출: 프롬프트에 값을 채워 OpenAI API 로 전송합니다.
    chain = _PROMPT | _LLM
    result = chain.invoke({"title": body.title or "", "content_text": body.content_text})

    # ② JSON 파싱: LLM 이 반환한 문자열을 dict 로 변환합니다.
    data = json.loads(result.content)

    # ③ Pydantic 검증: 필드가 빠지거나 타입이 다르면 여기서 에러가 납니다.
    #    검증을 통과한 결과만 DB 에 저장합니다.
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    response = schemas.SummaryResponse(
        summary=data["summary"],
        key_points=data["key_points"],
        meta=schemas.SummaryMeta(prompt_version="v1.0", generated_at=now),
    )

    # ④ DB 저장: output_json 에 검증된 결과를 통째로 직렬화해 넣습니다.
    row = models.Summary(
        title=body.title,
        content_text=body.content_text,
        output_json=json.dumps(response.model_dump()),
        prompt_version=response.meta.prompt_version,
    )
    summary_repository.save(db, row)  # save 후 row.id 가 DB 값으로 채워집니다

    # ⑤ id 를 추가해 반환합니다.
    return schemas.SummaryResponseWithId(id=row.id, **response.model_dump())


def list_summaries(db: Session) -> list[schemas.SummaryListItem]:
    rows = summary_repository.list_all(db)
    return [
        schemas.SummaryListItem(
            id=r.id,
            title=r.title,
            created_at=_created_at_to_iso(r.created_at),
        )
        for r in rows
    ]


def get_summary(id: int, db: Session) -> schemas.SummaryDetail:
    row = summary_repository.get_by_id(db, id)
    if not row:
        raise HTTPException(status_code=404, detail="Summary not found")

    # DB 에서 꺼낸 JSON 문자열을 다시 dict 로 파싱합니다.
    data = json.loads(row.output_json)
    return schemas.SummaryDetail(
        id=row.id,
        title=row.title,
        content_text=row.content_text,
        summary=data["summary"],
        key_points=data["key_points"],
        meta=schemas.SummaryMeta(**data["meta"]),
        created_at=_created_at_to_iso(row.created_at),
    )
