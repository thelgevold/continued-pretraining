import asyncio
from unittest.mock import AsyncMock

from subway_rag.app.city_vocabulary_mapper import CityVocabularyMapper
from subway_rag.app.rag_question_handler import RagQuestionHandler


def test_answers_with_internal_names_and_returns_public_names() -> None:
    asyncio.run(_assert_public_names_are_mapped())


async def _assert_public_names_are_mapped() -> None:
    model_client = AsyncMock()
    model_client.answer.return_value = {
        "answer": "Take blue station one to central_station.",
        "reasoning_summary": "blue_station_one is on Blue Line.",
        "input_prompt_characters": 123,
    }
    handler = RagQuestionHandler(model_client, CityVocabularyMapper())

    result = await handler.answer(
        "How do I travel from North Terminal to Central Station?",
        "Blue Line: North Terminal, Central Station.",
    )

    model_client.answer.assert_awaited_once_with(
        "How do I travel from blue_station_one to central_station?",
        "Blue Line: blue_station_one, central_station.",
    )
    assert result["answer"] == "Take North Terminal to Central Station."
    assert result["reasoning_summary"] == "North Terminal is on Blue Line."
