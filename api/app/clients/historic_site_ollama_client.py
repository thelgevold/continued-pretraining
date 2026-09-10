import re

import httpx

from app.models import OllamaInference, OllamaToolCallResult


class HistoricSiteOllamaClient:
    MAX_GENERATED_TOKENS = 2048

    def __init__(self, base_url: str, model_name: str) -> None:
        self._base_url = base_url
        self._model_name = model_name

    async def start_tool_call_generation(
        self,
        question: str,
        inference_seed: int,
        system_prompt: str,
        tools: list[dict[str, object]],
    ) -> OllamaToolCallResult:
        messages = self._create_messages(question, system_prompt)
        message = await self._chat(messages, inference_seed, tools)
        return OllamaToolCallResult(
            inference=self._inference_from_message(message),
            messages=tuple([*messages, message]),
            tool_calls=tuple(message.get("tool_calls", [])),
        )

    async def generate_after_tool_results(
        self,
        messages: tuple[dict[str, object], ...],
        inference_seed: int,
    ) -> OllamaInference:
        return self._inference_from_message(
            await self._chat(list(messages), inference_seed, [])
        )

    async def _chat(
        self,
        messages: list[dict[str, object]],
        inference_seed: int,
        tools: list[dict[str, object]],
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            "model": self._model_name,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {
                "num_predict": self.MAX_GENERATED_TOKENS,
                "temperature": 0,
                "top_k": 1,
                "seed": inference_seed,
            },
        }
        if tools:
            payload["tools"] = tools
        async with httpx.AsyncClient(base_url=self._base_url, timeout=300.0) as client:
            response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        message = response.json()["message"]
        if not isinstance(message, dict):
            raise RuntimeError("Ollama response must contain a message object.")
        return message

    @staticmethod
    def _create_messages(question: str, system_prompt: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]

    def _inference_from_message(self, message: dict[str, object]) -> OllamaInference:
        return OllamaInference(
            answer=self._clean_answer(str(message.get("content", ""))),
            thinking=str(message.get("thinking", "")).strip(),
        )

    @staticmethod
    def _clean_answer(answer: str) -> str:
        return re.sub(r"<think>.*?</think>\s*", "", answer, flags=re.DOTALL).strip()
