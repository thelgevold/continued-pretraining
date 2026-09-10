import asyncio
from unittest.mock import AsyncMock, Mock

from app.handlers.historic_site_question_handler import (
    HISTORIC_SITE_PLAIN_TEXT_PROMPT,
    HistoricSiteQuestionHandler,
)
from app.models import HistoricSiteQuestionRequest, OllamaInference


def test_historic_site_question_uses_the_isolated_tool_calling_handler() -> None:
    tool_calling_handler = Mock()
    tool_calling_handler.generate = AsyncMock(
        return_value=OllamaInference(
            answer="gold_historic_site_two was created in 1796.",
            thinking="Reasoning",
        )
    )

    response = asyncio.run(
        HistoricSiteQuestionHandler(tool_calling_handler).handle(
            HistoricSiteQuestionRequest(
                question="Tell me about Bright Mill Museum."
            )
        )
    )

    assert response.answer == "Bright Mill Museum was created in 1796."
    tool_calling_handler.generate.assert_awaited_once_with(
        question="Tell me about gold_historic_site_two.",
        inference_seed=42,
        system_prompt=HISTORIC_SITE_PLAIN_TEXT_PROMPT,
    )
