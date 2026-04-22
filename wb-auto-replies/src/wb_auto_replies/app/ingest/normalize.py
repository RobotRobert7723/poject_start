from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from wb_auto_replies.app.wb.schemas import NormalizedFeedback


def _parse_datetime(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _pick_first(payload: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def normalize_feedback(source_api: str, payload: dict[str, Any]) -> NormalizedFeedback:
    feedback_id = str(_pick_first(payload, ["id", "feedbackId"]))
    product_details = payload.get("productDetails") if isinstance(payload.get("productDetails"), dict) else {}
    video = payload.get("video") if isinstance(payload.get("video"), dict) else None
    text = _pick_first(payload, ["text", "prosText"])
    pros = _pick_first(payload, ["pros", "prosText"])
    cons = _pick_first(payload, ["cons", "consText"])
    media = _as_list(_pick_first(payload, ["photos", "media", "photoLinks"]))
    videos = [video] if video else _as_list(_pick_first(payload, ["videos", "videoLinks"]))
    answer = _pick_first(payload, ["answer", "wbAnswer", "supplierAnswer"])
    answer_text_current = answer.get("text") if isinstance(answer, dict) else None
    answer_state_current = answer.get("state") if isinstance(answer, dict) else None

    media_urls: list[dict[str, str]] = []
    for item in media:
        if isinstance(item, dict):
            url = _pick_first(item, ["url", "photoUrl", "link"])
        else:
            url = item
        if url:
            media_urls.append({"media_type": "photo", "media_url": str(url)})
    for item in videos:
        if isinstance(item, dict):
            url = _pick_first(item, ["link", "url", "videoUrl", "previewImage"])
        else:
            url = item
        if url:
            media_urls.append({"media_type": "video", "media_url": str(url)})

    payload_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()

    return NormalizedFeedback(
        source_api=source_api,
        feedback_id=feedback_id,
        feedback_thread_key=str(_pick_first(payload, ["feedbackThreadKey", "feedbackId", "id"])) if _pick_first(payload, ["feedbackThreadKey", "feedbackId", "id"]) is not None else None,
        created_date=_parse_datetime(_pick_first(payload, ["createdDate", "createdAt", "date"])),
        updated_date=_parse_datetime(_pick_first(payload, ["updatedDate", "updatedAt", "modifiedDate"])),
        stars=_pick_first(payload, ["productValuation", "valuation", "stars"]),
        text=str(text) if text is not None else None,
        pros=str(pros) if pros is not None else None,
        cons=str(cons) if cons is not None else None,
        user_name_raw=str(_pick_first(payload, ["userName", "name", "user"])) if _pick_first(payload, ["userName", "name", "user"]) is not None else None,
        has_photo=any(item["media_type"] == "photo" for item in media_urls),
        has_video=any(item["media_type"] == "video" for item in media_urls),
        media_urls=media_urls,
        nm_id=_pick_first(payload, ["nmId", "nmID"]) or _pick_first(product_details, ["nmId", "nmID"]),
        imt_id=_pick_first(payload, ["imtId", "imtID"]) or _pick_first(product_details, ["imtId", "imtID"]),
        product_name=str(_pick_first(payload, ["productName", "imtName", "name"]) or _pick_first(product_details, ["productName", "imtName", "name"])) if (_pick_first(payload, ["productName", "imtName", "name"]) or _pick_first(product_details, ["productName", "imtName", "name"])) is not None else None,
        supplier_article=str(_pick_first(payload, ["supplierArticle", "vendorCode"]) or _pick_first(product_details, ["supplierArticle", "vendorCode"])) if (_pick_first(payload, ["supplierArticle", "vendorCode"]) or _pick_first(product_details, ["supplierArticle", "vendorCode"])) is not None else None,
        brand_name=str(_pick_first(payload, ["brandName", "brand"]) or _pick_first(product_details, ["brandName", "brand"])) if (_pick_first(payload, ["brandName", "brand"]) or _pick_first(product_details, ["brandName", "brand"])) is not None else None,
        subject_id=_pick_first(payload, ["subjectId", "subjectID"]) or _pick_first(product_details, ["subjectId", "subjectID"]),
        subject_name=str(_pick_first(payload, ["subjectName", "subject"]) or _pick_first(product_details, ["subjectName", "subject"])) if (_pick_first(payload, ["subjectName", "subject"]) or _pick_first(product_details, ["subjectName", "subject"])) is not None else None,
        parent_feedback_id=str(_pick_first(payload, ["parentFeedbackId", "parentId"])) if _pick_first(payload, ["parentFeedbackId", "parentId"]) is not None else None,
        child_feedback_id=str(_pick_first(payload, ["childFeedbackId", "childId"])) if _pick_first(payload, ["childFeedbackId", "childId"]) is not None else None,
        answer_text_current=answer_text_current,
        answer_state_current=answer_state_current,
        raw_payload=payload,
        source_hash=payload_hash,
    )
