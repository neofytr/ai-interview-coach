import asyncio
import json
import time
from pathlib import Path
from typing import TypeVar

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel

from utils.config import get_settings
from utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
logger = get_logger("llm")


class LLMClient:
    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )
        self.model = model or settings.llm_model

    async def call(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
    ) -> str:
        return await self._request(system_prompt, user_message, temperature)

    async def call_json(
        self,
        system_prompt: str,
        user_message: str,
        response_model: type[T],
        temperature: float = 0.3,
    ) -> T:
        raw = await self._request(system_prompt, user_message, temperature)
        try:
            return self._parse_json(raw, response_model)
        except (json.JSONDecodeError, ValueError):
            fix_prompt = (
                "The following JSON is malformed or does not match the required schema. "
                "Return ONLY valid JSON matching the schema — no markdown fences, no commentary.\n\n"
                f"Required schema:\n{json.dumps(response_model.model_json_schema(), indent=2)}\n\n"
                f"Broken JSON:\n{raw}"
            )
            raw = await self._request(system_prompt, fix_prompt, temperature=0.1)
            return self._parse_json(raw, response_model)

    @staticmethod
    def load_prompt(prompt_name: str) -> str:
        path = PROJECT_ROOT / "prompts" / f"{prompt_name}.md"
        return path.read_text(encoding="utf-8")

    async def _request(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float,
    ) -> str:
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                start = time.monotonic()
                response = await self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=temperature,
                )
                elapsed = time.monotonic() - start
                logger.debug("LLM call completed in %.2fs (model=%s)", elapsed, self.model)
                return response.choices[0].message.content or ""
            except (RateLimitError, APIError, APITimeoutError) as exc:
                last_exc = exc
                logger.warning("LLM call attempt %d failed: %s", attempt + 1, exc)
                if attempt < 2:
                    await asyncio.sleep(2**attempt)
        raise last_exc  # type: ignore[misc]

    @staticmethod
    def load_question_bank() -> dict:
        path = PROJECT_ROOT / "data" / "question_bank.json"
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _parse_json(raw: str, model: type[T]) -> T:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if "```" in text:
                text = text.rsplit("```", 1)[0]
            text = text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            text = text[start:end]
        return model.model_validate_json(text)
