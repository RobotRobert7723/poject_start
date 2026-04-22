from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


SourceApi = str


@dataclass(slots=True)
class WbApiRequest:
    token: str
    take: int = 100
    skip: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    order: str | None = None
    is_answered: bool | None = None


@dataclass(slots=True)
class WbApiResponse:
    source_api: SourceApi
    items: list[dict[str, Any]]
    cursor: dict[str, Any] | None
    total: int | None
    raw_payload: dict[str, Any]


@dataclass(slots=True)
class NormalizedFeedback:
    source_api: SourceApi
    feedback_id: str
    feedback_thread_key: str | None
    created_date: datetime | None
    updated_date: datetime | None
    stars: int | None
    text: str | None
    pros: str | None
    cons: str | None
    user_name_raw: str | None
    has_photo: bool
    has_video: bool
    media_urls: list[dict[str, str]]
    nm_id: int | None
    imt_id: int | None
    product_name: str | None
    supplier_article: str | None
    brand_name: str | None
    subject_id: int | None
    subject_name: str | None
    parent_feedback_id: str | None
    child_feedback_id: str | None
    answer_text_current: str | None
    answer_state_current: str | None
    raw_payload: dict[str, Any]
    source_hash: str
