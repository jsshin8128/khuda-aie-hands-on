"""5주차 정답: API 요청/응답 스키마 (Pydantic)."""

from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    url: str
    output_format: Literal["json"]


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
    id: int  # POST /summarize 응답용


class SummaryListItem(BaseModel):
    id: int
    title: str | None
    url: str  # 5주차: created_at 대신 url


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


class BatchSummaryRequest(BaseModel):
    urls: list[str]
    output_format: Literal["json"]


class BatchSummaryResponse(BaseModel):
    results: list[SummaryResponseWithId]
    failed: list[dict]  # {"url": "...", "error": "..."}
