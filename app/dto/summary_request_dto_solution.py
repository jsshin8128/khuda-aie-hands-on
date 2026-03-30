"""5주차 정답: API 요청 스키마 (Pydantic)."""

from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    url: str
    output_format: Literal["json"]


class BatchSummaryRequest(BaseModel):
    urls: list[str]
    output_format: Literal["json"]
