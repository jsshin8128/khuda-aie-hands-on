"""4주차: Service 레이어 — 비즈니스 로직 + LangChain 연동.

이 레이어의 역할:
  1. LLM 을 호출해 요약을 생성합니다.
  2. LLM 출력을 Pydantic 으로 검증합니다.  ← 핵심! 잘못된 출력이 DB에 들어가지 않습니다.
  3. Repository 를 통해 DB에 저장합니다.
  4. Router 에 결과를 반환합니다.

LangChain LCEL 패턴 한 줄 요약:
  chain = 프롬프트 | LLM
  result = chain.invoke({"변수": "값"})
  → 프롬프트에 변수를 채운 뒤 LLM 에 보내고 응답을 받아옵니다.

실습: TODO [1]~[5]를 순서대로 채우세요.
"""

import json
from datetime import datetime, timezone

from dotenv import load_dotenv  # .env 파일에서 OPENAI_API_KEY 를 읽어옵니다
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories import summary_repository

load_dotenv()  # 이 줄이 없으면 API 키를 읽지 못합니다


# TODO [1] ChatPromptTemplate 을 정의하세요.
#
#   LangChain 의 프롬프트 템플릿입니다. {title}, {content_text} 자리에
#   invoke() 시점에 실제 값이 채워집니다.
#
#   시스템 메시지에는 LLM 이 반드시 아래 JSON 형식으로만 답하도록 지시하세요.
#     {
#       "summary": "2~3문장 핵심 요약",
#       "key_points": ["포인트 1", "포인트 2", "포인트 3"]
#     }
#   ※ 프롬프트 문자열 안에서 실제 중괄호 { } 를 쓰려면 {{ }} 로 이스케이프합니다.
#
#   힌트:
#     from langchain.prompts import ChatPromptTemplate
#     _PROMPT = ChatPromptTemplate.from_messages([
#         ("system", "..."),
#         ("user", "제목: {title}\n\n내용:\n{content_text}"),
#     ])
_PROMPT = None  # TODO [1] 구현 후 이 줄을 교체하세요


# TODO [2] ChatOpenAI 를 초기화하세요.
#
#   ChatOpenAI 는 OpenAI API 를 LangChain 방식으로 감싼 클라이언트입니다.
#   temperature=0 으로 설정하면 매번 같은 형식의 답변이 나와 JSON 파싱이 안정적입니다.
#
#   힌트:
#     from langchain_openai import ChatOpenAI
#     _LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)
_LLM = None  # TODO [2] 구현 후 이 줄을 교체하세요


def _created_at_to_iso(created_at: str) -> str:
    """SQLite 는 '2024-01-01 00:00:00' 형태로 저장합니다.
    API 응답에서는 '2024-01-01T00:00:00Z' 형태(ISO 8601)로 반환합니다."""
    return created_at.replace(" ", "T", 1) + "Z" if created_at and " " in created_at else (created_at or "")


def create_summary(body: schemas.SummaryRequest, db: Session) -> schemas.SummaryResponseWithId:
    # TODO [3] LLM 호출 → JSON 파싱 → Pydantic 검증 → DB 저장 → 반환
    #
    #   ① LLM 호출
    #      chain = _PROMPT | _LLM
    #      result = chain.invoke({"title": body.title or "", "content_text": body.content_text})
    #
    #   ② LLM 응답(문자열)을 dict 로 파싱
    #      data = json.loads(result.content)
    #
    #   ③ Pydantic 으로 검증 (필드가 빠지거나 타입이 다르면 여기서 에러)
    #      now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    #      response = schemas.SummaryResponse(
    #          summary=data["summary"],
    #          key_points=data["key_points"],
    #          meta=schemas.SummaryMeta(prompt_version="v1.0", generated_at=now),
    #      )
    #
    #   ④ DB 저장
    #      row = models.Summary(
    #          title=body.title,
    #          content_text=body.content_text,
    #          output_json=json.dumps(response.model_dump()),  # 검증된 결과만 저장
    #          prompt_version=response.meta.prompt_version,
    #      )
    #      summary_repository.save(db, row)  # save 후 row.id 가 채워집니다
    #
    #   ⑤ id 를 포함한 응답 반환
    #      return schemas.SummaryResponseWithId(id=row.id, **response.model_dump())
    raise NotImplementedError("TODO [3]")


def list_summaries(db: Session) -> list[schemas.SummaryListItem]:
    # TODO [4] 전체 목록을 조회해 SummaryListItem 리스트로 변환하세요.
    #
    #   rows = summary_repository.list_all(db)
    #   return [
    #       schemas.SummaryListItem(
    #           id=r.id,
    #           title=r.title,
    #           created_at=_created_at_to_iso(r.created_at),
    #       )
    #       for r in rows
    #   ]
    raise NotImplementedError("TODO [4]")


def get_summary(id: int, db: Session) -> schemas.SummaryDetail:
    # TODO [5] id 로 단건 조회하세요.
    #
    #   row = summary_repository.get_by_id(db, id)
    #   if not row:
    #       raise HTTPException(status_code=404, detail="Summary not found")
    #
    #   # output_json 은 JSON 문자열 → dict 로 파싱해서 사용합니다
    #   data = json.loads(row.output_json)
    #   return schemas.SummaryDetail(
    #       id=row.id,
    #       title=row.title,
    #       content_text=row.content_text,
    #       summary=data["summary"],
    #       key_points=data["key_points"],
    #       meta=schemas.SummaryMeta(**data["meta"]),
    #       created_at=_created_at_to_iso(row.created_at),
    #   )
    raise NotImplementedError("TODO [5]")
