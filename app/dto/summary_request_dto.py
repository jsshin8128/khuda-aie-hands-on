"""5주차: API 요청 스키마 (Pydantic).

실습: TODO [1]~[2]를 순서대로 채우세요.
"""

from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    url: str
    output_format: Literal["json"]


class BatchSummaryRequest(BaseModel):
    urls: list[str]
    output_format: Literal["json"]
