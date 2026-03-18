"""2·3주차: API 요청/응답 스키마 (Pydantic).

실습: TODO [1]~[6]을 채워 각 스키마 클래스를 완성하세요.
"""

from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    # TODO [1] 요청 필드 3개를 정의하세요.
    #   - content_text : str (필수)
    #   - title        : str | None, 기본값 None
    #   - output_format: Literal["json"] (필수)
    pass


class SummaryMeta(BaseModel):
    # TODO [2] 메타 필드 2개를 정의하세요.
    #   - prompt_version: str
    #   - generated_at  : str
    pass


class SummaryResponse(BaseModel):
    # TODO [3] 응답 필드 5개를 정의하세요.
    #   - main_points       : list[str]
    #   - core_summary      : str
    #   - structure_summary : str
    #   - practical_insights: list[str]
    #   - meta              : SummaryMeta
    pass


class SummaryResponseWithId(SummaryResponse):
    # TODO [4] SummaryResponse를 상속하고 id: int 필드를 추가하세요.
    #          (POST /summarize 응답에 DB 저장 id 포함)
    pass


class SummaryListItem(BaseModel):
    # TODO [5] 목록 조회용 필드 3개를 정의하세요.
    #   - id        : int
    #   - title     : str | None
    #   - created_at: str
    pass


class SummaryDetail(BaseModel):
    # TODO [6] 단건 조회용 필드 9개를 정의하세요.
    #   - id                : int
    #   - title             : str | None
    #   - content_text      : str
    #   - main_points       : list[str]
    #   - core_summary      : str
    #   - structure_summary : str
    #   - practical_insights: list[str]
    #   - meta              : SummaryMeta
    #   - created_at        : str
    pass
