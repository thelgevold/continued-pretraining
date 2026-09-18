import asyncio
from unittest.mock import patch

import httpx

from app.clients.ollama_client import OllamaClient
from app.models.subway_route_schema import SubwayRouteSchema


def test_question_returns_schema_formatted_json() -> None:
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
    assert client.payloads[0]["format"] == SubwayRouteSchema.as_dict()
    assert client.payloads[0]["think"] is False


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
