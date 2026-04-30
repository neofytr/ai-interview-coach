import asyncio
import json
import os
from pathlib import Path
from typing import TypeVar

from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class LLMClient:
    def __init__(self, model: str | None = None) -> None:
        self._client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

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
                response = await self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=temperature,
                )
                return response.choices[0].message.content or ""
            except (RateLimitError, APIError, APITimeoutError) as exc:
                last_exc = exc
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
