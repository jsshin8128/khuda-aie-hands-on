"""5주차: API 응답 스키마 (Pydantic).

실습: TODO [1]~[6]을 순서대로 채우세요.
"""

from typing import Literal

from pydantic import BaseModel


class SummaryMeta(BaseModel):
    prompt_version: str
    generated_at: str


class SummaryResponse(BaseModel):
    recommended_for: str
    difficulty: Literal["초급", "중급", "고급"]
    read_time: int
    summary: str
    key_points: list[str]
    meta: SummaryMeta


class SummaryResponseWithId(SummaryResponse):
    id: int


class SummaryListItem(BaseModel):
    id: int
    title: str | None
    url: str


class SummaryDetailResponse(BaseModel):
    id: int
    title: str | None
    url: str
    content_text: str
    recommended_for: str
    difficulty: str
    read_time: int
    summary: str
    key_points: list[str]
    meta: SummaryMeta
    created_at: str


class BatchSummaryResponse(BaseModel):
    results: list[SummaryResponseWithId]
    failed: list[dict]
