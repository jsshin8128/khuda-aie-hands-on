"""2·3주차 정답: API 요청/응답 스키마 (Pydantic)."""

from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    content_text: str
    title: str | None = None
    output_format: Literal["json"]


class SummaryMeta(BaseModel):
    prompt_version: str
    generated_at: str


class SummaryResponse(BaseModel):
    main_points: list[str]
    core_summary: str
    structure_summary: str
    practical_insights: list[str]
    meta: SummaryMeta


class SummaryResponseWithId(SummaryResponse):
    id: int  # POST /summarize 응답용


class SummaryListItem(BaseModel):
    id: int
    title: str | None
    created_at: str


class SummaryDetail(BaseModel):
    id: int  # GET /summaries/{id} 단건 응답용
    title: str | None
    content_text: str
    main_points: list[str]
    core_summary: str
    structure_summary: str
    practical_insights: list[str]
    meta: SummaryMeta
    created_at: str
