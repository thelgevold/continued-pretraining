import asyncio
from unittest.mock import AsyncMock, Mock

from app.handlers.city_vocabulary_mapper import CityVocabularyMapper
from app.handlers.question_handler import (
    CITY_ANNOUNCEMENTS_PROMPT,
    CITY_PLAIN_TEXT_PROMPT,
    QuestionHandler,
)
from app.models import OllamaInference, QuestionRequest


def test_question_response_uses_human_readable_names_at_the_api_boundary() -> None:
    ollama_client = Mock()
    ollama_client.ask_question = AsyncMock(
        return_value=OllamaInference(
            answer="Take Blue Line from blue_station_one to blue_station_four.",
            thinking="blue_station_one and blue_station_four are on Blue Line.",
        )
    )
    announcements_retriever = Mock()
    announcements_retriever.retrieve.return_value = "Concert at Westgate today."
    response = asyncio.run(
        QuestionHandler(ollama_client, announcements_retriever).handle(
            QuestionRequest(question="How do I travel from North Terminal to River Market?")
        )
    )

    assert response.answer == "Take Blue Line from North Terminal to River Market."
    assert response.reasoning_summary == "North Terminal and River Market are on Blue Line."
    ollama_client.ask_question.assert_awaited_once_with(
        question="How do I travel from blue_station_one to blue_station_four?",
        inference_seed=42,
        system_prompt=(
            f"{CITY_PLAIN_TEXT_PROMPT}{CITY_ANNOUNCEMENTS_PROMPT}"
            "Concert at gold_station_one today."
        ),
    )


def test_vocabulary_mapper_uses_historic_site_identifiers_without_question_categorization() -> None:
    mapper = CityVocabularyMapper()

    assert mapper.to_synthetic_input(
        "What historic route leads from Founder's Square to Bright Mill Museum?"
    ) == (
        "What historic route leads from blue_historic_site_three to "
        "gold_historic_site_two?"
    )
    assert mapper.to_synthetic_input("How do I travel from Founder's Square to River Market?") == (
        "How do I travel from blue_historic_site_three to blue_station_four?"
    )
