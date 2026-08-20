import asyncio
from unittest.mock import patch

import httpx

from app.clients.ollama_client import OllamaClient


def test_question_returns_plain_text() -> None:
    response = httpx.Response(
        200,
        request=httpx.Request("POST", "http://ollama/api/chat"),
        json={"message": {"content": "Take the Blue Line directly."}},
    )
    client = _AsyncClient([response])

    with patch("app.clients.ollama_client.httpx.AsyncClient", return_value=client):
        inference = asyncio.run(
            OllamaClient("http://ollama", "model").ask_question(
                "Question",
                42,
                "System prompt",
            )
        )

    assert inference.answer == "Take the Blue Line directly."
    assert "format" not in client.payloads[0]
    assert client.payloads[0]["think"] is True


class _AsyncClient:
    def __init__(self, responses: list[httpx.Response]) -> None:
        self._responses = responses
        self.payloads: list[dict[str, object]] = []

    async def __aenter__(self) -> "_AsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(self, path: str, json: dict[str, object]) -> httpx.Response:
        self.payloads.append(json)
        return self._responses.pop(0)