from __future__ import annotations

from openai import OpenAI

from wb_auto_replies.app.config.settings import get_settings
from wb_auto_replies.app.gpt.schemas import GptGenerationRequest, GptGenerationResult


class GptClient:
    def __init__(self) -> None:
        settings = get_settings()
        client_kwargs: dict[str, str] = {"api_key": settings.openai_api_key or ""}
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        self.client = OpenAI(**client_kwargs)

    def generate(self, request: GptGenerationRequest) -> GptGenerationResult:
        response = self.client.responses.create(
            model=request.model,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
            input=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
        )
        text = response.output_text.strip()
        return GptGenerationResult(
            text=text,
            model=request.model,
            prompt_snapshot={
                "system_prompt": request.system_prompt,
                "user_prompt": request.user_prompt,
                "model": request.model,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
            },
            raw_response=response.model_dump(),
        )
