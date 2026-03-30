"""5주차: API 요청 스키마 (Pydantic).

실습: TODO [1]~[2]를 순서대로 채우세요.
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


class BatchSummaryRequest(BaseModel):
    # TODO [2] POST /summarize/batch 요청 바디입니다.
    #
    #   여러 URL을 한꺼번에 받아 동시에 처리합니다. 최대 10개.
    #
    #   힌트:
    #     urls         : list[str]       — URL 목록 (1~10개)
    #     output_format: Literal["json"]
    pass
