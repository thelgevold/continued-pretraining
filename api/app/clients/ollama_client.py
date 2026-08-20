import re

import httpx
from app.models import OllamaInference


class OllamaClient:
    MAX_GENERATED_TOKENS = 2048
    MAX_SUMMARY_TOKENS = 512

    def __init__(
        self,
        base_url: str,
        model_name: str,
    ) -> None:
        self._base_url = base_url
        self._model_name = model_name

    async def ask_question(
        self,
        question: str,
        inference_seed: int,
        system_prompt: str,
    ) -> OllamaInference:
        return await self._generate_inference(
            question,
            inference_seed,
            system_prompt,
        )

    async def _generate_inference(
        self,
        question: str,
        inference_seed: int,
        system_prompt: str,
    ) -> OllamaInference:
        payload = {
            "model": self._model_name,
            "messages": self._create_messages(question, system_prompt),
            "stream": False,
            "think": True,
            "options": {
                "num_predict": self.MAX_GENERATED_TOKENS,
                "temperature": 0,
                "top_k": 1,
                "seed": inference_seed,
            },
        }
        async with httpx.AsyncClient(base_url=self._base_url, timeout=300.0) as client:
            response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        message = response.json()["message"]
        return OllamaInference(
            answer=self._clean_answer(str(message.get("content", ""))),
            thinking=str(message.get("thinking", "")).strip(),
        )

    async def summarize_reasoning(self, thinking: str) -> str:
        if not thinking:
            return "Thinking was enabled, but Ollama returned no reasoning content."
        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Summarize the supplied reasoning in one or two concise "
                        "sentences. Paraphrase its approach and conclusion. Mention "
                        "an apparent factual mistake or unsupported inference when "
                        "one is visible. Do not quote, reproduce, or enumerate the "
                        "reasoning. Return only the summary."
                    ),
                },
                {"role": "user", "content": thinking},
            ],
            "stream": False,
            "think": True,
            "options": {
                "num_predict": self.MAX_SUMMARY_TOKENS,
                "temperature": 0,
                "top_k": 1,
                "seed": 42,
            },
        }
        async with httpx.AsyncClient(base_url=self._base_url, timeout=300.0) as client:
            response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        return self._clean_answer(str(response.json()["message"]["content"]))

    def _create_messages(
        self,
        question: str,
        system_prompt: str | None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": question})
        return messages

    def _clean_answer(self, answer: str) -> str:
        answer_without_thinking = re.sub(
            r"<think>.*?</think>\s*",
            "",
            answer,
            flags=re.DOTALL,
        )
        answer_without_instruction_echo = re.sub(
            r"(?:^|\s+)(?:keep it succinct(?: and accurate)?|"
            r"answer succinctly(?: and accurately)?|"
            r"only answer what is asked)\.?\s*$",
            "",
            answer_without_thinking,
            flags=re.IGNORECASE,
        )
        return answer_without_instruction_echo.strip()
