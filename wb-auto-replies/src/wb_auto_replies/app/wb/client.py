from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from wb_auto_replies.app.config.settings import get_settings
from wb_auto_replies.app.wb.schemas import WbApiRequest, WbApiResponse


class WbApiError(Exception):
    pass


class WbRateLimitError(WbApiError):
    pass


class BaseWbFeedbackClient:
    base_url = "https://feedbacks-api.wildberries.ru"
    source_api = "unknown"
    endpoint = "/api/v1/feedbacks"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.settings.wb_http_timeout_seconds,
            headers={"Content-Type": "application/json"},
        )

    def _build_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": token}

    def _build_params(self, request: WbApiRequest) -> dict[str, Any]:
        params: dict[str, Any] = {"take": request.take}
        if request.skip is not None:
            params["skip"] = request.skip
        if request.order:
            params["order"] = request.order
        if request.is_answered is not None:
            params["isAnswered"] = str(request.is_answered).lower()
        if request.date_from is not None:
            params["dateFrom"] = request.date_from.astimezone(UTC).isoformat()
        if request.date_to is not None:
            params["dateTo"] = request.date_to.astimezone(UTC).isoformat()
        return params

    def _extract_items(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        if isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("feedbacks"), list):
            return payload["data"]["feedbacks"]
        if isinstance(payload.get("feedbacks"), list):
            return payload["feedbacks"]
        if isinstance(payload.get("data"), list):
            return payload["data"]
        return []

    def _extract_cursor(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("cursor"), dict):
            return payload["data"]["cursor"]
        if isinstance(payload.get("cursor"), dict):
            return payload["cursor"]
        return None

    def _extract_total(self, payload: dict[str, Any]) -> int | None:
        if isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("count"), int):
            return payload["data"]["count"]
        if isinstance(payload.get("count"), int):
            return payload["count"]
        return None

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, WbRateLimitError)),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        stop=stop_after_attempt(get_settings().wb_max_retries),
        reraise=True,
    )
    def fetch_feedbacks(self, request: WbApiRequest) -> WbApiResponse:
        response = self._client.get(
            self.endpoint,
            headers=self._build_headers(request.token),
            params=self._build_params(request),
        )
        if response.status_code == 429:
            raise WbRateLimitError(f"WB rate limit on {self.source_api}: {response.text}")
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise WbApiError(f"WB API error on {self.source_api}: {exc.response.text}") from exc

        payload = response.json()
        return WbApiResponse(
            source_api=self.source_api,
            items=self._extract_items(payload),
            cursor=self._extract_cursor(payload),
            total=self._extract_total(payload),
            raw_payload=payload,
        )
