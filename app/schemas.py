"""2·3주차: API 요청/응답 스키마 (Pydantic).

Pydantic BaseModel을 상속하면 두 가지 일을 동시에 합니다.
  1. 타입 검증 — 잘못된 값이 들어오면 FastAPI가 자동으로 422 에러를 반환합니다.
  2. 직렬화 — .model_dump() 로 dict 변환, JSON 응답으로 자동 변환됩니다.

요청/응답 흐름:
  HTTP 요청 JSON  →  SummaryRequest  (입력 검증)
  LLM 결과        →  SummaryResponse (출력 검증)
  DB 저장 후      →  SummaryResponseWithId (id 추가)
  목록 조회       →  SummaryListItem
  단건 조회       →  SummaryDetail

실습: TODO [1]~[6]을 채워 각 스키마 클래스를 완성하세요.
"""

from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    # TODO [1] 클라이언트가 POST /summarize 로 보내는 요청 바디입니다.
    #          필드 3개를 정의하세요.
    #
    #   content_text : str          — 요약할 본문 (필수)
    #   title        : str | None   — 글 제목, 없어도 됨 (기본값 None)
    #   output_format: Literal["json"] — 현재는 "json" 만 허용
    pass


class SummaryMeta(BaseModel):
    # TODO [2] LLM 호출 정보를 담는 메타데이터입니다.
    #          SummaryResponse 안에 중첩되어 사용됩니다.
    #
    #   prompt_version: str  — 어떤 프롬프트를 썼는지 (예: "v1.0")
    #   generated_at  : str  — 생성 시각 ISO 8601 문자열 (예: "2024-01-01T00:00:00Z")
    pass


class SummaryResponse(BaseModel):
    # TODO [3] LLM이 반환한 요약 결과입니다.
    #          Pydantic이 LLM 출력을 검증하는 안전망 역할을 합니다.
    #
    #   summary   : str       — 2~3문장 핵심 요약
    #   key_points: list[str] — 핵심 포인트 목록
    #   meta      : SummaryMeta — 위에서 정의한 메타 클래스
    pass


class SummaryResponseWithId(SummaryResponse):
    # TODO [4] SummaryResponse 를 그대로 상속하고 id 필드만 추가합니다.
    #          POST /summarize 응답에서 DB에 저장된 id 를 함께 반환합니다.
    #
    #   id: int  — DB auto increment PK
    pass


class SummaryListItem(BaseModel):
    # TODO [5] GET /summaries 목록 응답용입니다.
    #          본문은 무겁기 때문에 목록에서는 핵심 필드만 내려줍니다.
    #
    #   id        : int
    #   title     : str | None
    #   created_at: str
    pass


class SummaryDetail(BaseModel):
    # TODO [6] GET /summaries/{id} 단건 응답용입니다.
    #          목록과 달리 본문과 요약 내용을 모두 포함합니다.
    #
    #   id          : int
    #   title       : str | None
    #   content_text: str        — 원본 본문
    #   summary     : str
    #   key_points  : list[str]
    #   meta        : SummaryMeta
    #   created_at  : str
    pass
