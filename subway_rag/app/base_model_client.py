import re

import httpx


class BaseModelClient:
    CONTEXT_WINDOW = 10_000
    MAX_GENERATED_TOKENS = 10_000

    def __init__(self, base_url: str, model_name: str) -> None:
        self._base_url = base_url
        self._model_name = model_name

    async def answer(self, question: str, subway_network: str) -> dict[str, object]:
        messages = self._create_messages(question, subway_network)
        response = await self._post(messages)
        message = response["message"]
        return {
            "answer": self._clean(str(message.get("content", ""))),
            "reasoning_summary": str(message.get("thinking", "")).strip(),
            "input_prompt_characters": sum(
                len(str(message["content"])) for message in messages
            ),
        }

    async def _post(self, messages: list[dict[str, str]]) -> dict[str, object]:
        payload = {
            "model": self._model_name,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {
                "num_ctx": self.CONTEXT_WINDOW,
                "num_predict": self.MAX_GENERATED_TOKENS,
                "temperature": 0,
                "top_k": 1,
                "seed": 42,
            },
        }
        async with httpx.AsyncClient(base_url=self._base_url, timeout=300.0) as client:
            response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _create_messages(
        question: str,
        subway_network: str,
    ) -> list[dict[str, str]]:
        return [
                {
                    "role": "system",
                    "content": (
                        "Use only the supplied subway-network document for subway "
                        "facts. Before answering, make one concise internal route "
                        "check for each requested journey: identify the lines serving "
                        "the origin and destination, determine whether a transfer is "
                        "needed, and use Central Station only when changing lines. "
                        "Verify each journey independently. Do not repeat or reconsider the "
                        "check after it is complete. Answer in ordinary English. State "
                        "each line and every required transfer station. Do not invent "
                        "historic-site facts that are absent from the document.\n\n"
                        "SUBWAY NETWORK:\n"
                        f"{subway_network}"
                    ),
                },
                {"role": "user", "content": question},
        ]

    @staticmethod
    def _clean(answer: str) -> str:
        return re.sub(r"<think>.*?</think>\s*", "", answer, flags=re.DOTALL).strip()
