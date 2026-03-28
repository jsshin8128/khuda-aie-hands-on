"""5주차: API 요청/응답 스키마 (Pydantic).

4주차와 달라지는 점:
  - SummaryRequest 필드가 수정됩니다.
  - SummaryResponse 필드가 수정됩니다.
  - SummaryListItem 필드가 수정됩니다.
  - 배치 처리용 BatchSummaryRequest, BatchSummaryResponse 가 추가됩니다.

요청/응답 흐름:
  POST /summarize        →  SummaryRequest   →  SummaryResponseWithId
  POST /summarize/batch  →  BatchSummaryRequest →  BatchSummaryResponse
  GET  /summaries        →  (없음)             →  list[SummaryListItem]
  GET  /summaries/{id}   →  (없음)             →  SummaryDetailResponse

실습: TODO [1]~[8]을 순서대로 채우세요.
"""

from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    # TODO [1] POST /summarize 요청 바디입니다.
    #
    #   4주차 SummaryRequest 와 비교:
    #     전: content_text(str), title(str|None), output_format
    #     후: url(str), output_format  — 본문은 서버가 직접 크롤링합니다.
    #
    #   힌트:
    #     url          : str              — 요약할 기술 블로그 URL (필수)
    #     output_format: Literal["json"]  — 현재는 "json" 만 허용
    pass


class SummaryMeta(BaseModel):
    # TODO [2] LLM 호출 메타데이터입니다. 4주차와 동일합니다.
    #
    #   힌트:
    #     prompt_version: str  — 어떤 프롬프트를 썼는지 (예: "v2.0")
    #     generated_at  : str  — 생성 시각 ISO 8601 (예: "2025-03-28T10:30:00Z")
    pass


class SummaryResponse(BaseModel):
    # TODO [3] LLM 요약 결과입니다.
    #
    #   4주차(summary, key_points, meta) 에서 세 필드가 추가됩니다.
    #
    #   추가 필드:
    #     recommended_for: str                          — 이런 분께 추천 (예: "Python 입문자")
    #     difficulty     : Literal["초급", "중급", "고급"] — 글 난이도
    #     read_time      : int                          — 예상 읽기 시간 (분)
    #
    #   기존 필드:
    #     summary   : str
    #     key_points: list[str]
    #     meta      : SummaryMeta
    pass


class SummaryResponseWithId(SummaryResponse):
    # TODO [4] SummaryResponse 를 상속하고 id 만 추가합니다. 4주차와 동일합니다.
    #
    #   힌트:
    #     id: int  — DB auto increment PK
    pass


class SummaryListItem(BaseModel):
    # TODO [5] GET /summaries 목록 응답용입니다.
    #
    #   4주차에서 created_at 이 빠지고 url 이 들어옵니다.
    #   목록에서는 본문 대신 어떤 URL을 요약했는지 보여 줍니다.
    #
    #   힌트:
    #     id   : int
    #     title: str | None  — 페이지에서 추출한 제목. 추출 실패 시 None.
    #     url  : str
    pass


class SummaryDetailResponse(BaseModel):
    # TODO [6] GET /summaries/{id} 단건 응답용입니다.
    #
    #   4주차 SummaryDetailResponse 에서 url, recommended_for, difficulty, read_time 이 추가됩니다.
    #
    #   힌트:
    #     id            : int
    #     title         : str | None
    #     url           : str
    #     content_text  : str
    #     recommended_for: str
    #     difficulty    : str
    #     read_time     : int
    #     summary       : str
    #     key_points    : list[str]
    #     meta          : SummaryMeta
    #     created_at    : str
    pass


class BatchSummaryRequest(BaseModel):
    # TODO [7] POST /summarize/batch 요청 바디입니다.
    #
    #   여러 URL을 한꺼번에 받아 동시에 처리합니다. 최대 10개.
    #
    #   힌트:
    #     urls         : list[str]       — URL 목록 (1~10개)
    #     output_format: Literal["json"]
    pass


class BatchSummaryResponse(BaseModel):
    # TODO [8] POST /summarize/batch 응답입니다.
    #
    #   일부 URL 처리에 실패해도 전체가 실패하지 않습니다.
    #   성공한 것은 results 에, 실패한 것은 failed 에 담겨 반환됩니다.
    #
    #   힌트:
    #     results: list[SummaryResponseWithId]
    #     failed : list[dict]  — 각 요소: {"url": "...", "error": "..."}
    pass
