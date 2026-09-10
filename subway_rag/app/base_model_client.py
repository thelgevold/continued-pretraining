import re

import httpx


class BaseModelClient:
    MAX_GENERATED_TOKENS = 4096

    def __init__(self, base_url: str, model_name: str) -> None:
        self._base_url = base_url
        self._model_name = model_name

    async def answer(self, question: str, subway_network: str) -> dict[str, str]:
        response = await self._post(question, subway_network)
        message = response["message"]
        return {
            "answer": self._clean(str(message.get("content", ""))),
            "reasoning_summary": str(message.get("thinking", "")).strip(),
        }

    async def _post(self, question: str, subway_network: str) -> dict[str, object]:
        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Use only the supplied subway-network document for subway "
                        "facts. Answer in ordinary English. State each line and every "
                        "transfer station required. Do not invent historic-site facts "
                        "that are absent from the document.\n\nSUBWAY NETWORK:\n"
                        f"{subway_network}"
                    ),
                },
                {"role": "user", "content": question},
            ],
            "stream": False,
            "think": False,
            "options": {"num_predict": self.MAX_GENERATED_TOKENS, "temperature": 0, "top_k": 1, "seed": 42},
        }
        async with httpx.AsyncClient(base_url=self._base_url, timeout=300.0) as client:
            response = await client.post("/api/chat", json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _clean(answer: str) -> str:
        return re.sub(r"<think>.*?</think>\s*", "", answer, flags=re.DOTALL).strip()
