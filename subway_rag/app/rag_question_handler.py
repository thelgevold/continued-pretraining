from subway_rag.app.base_model_client import BaseModelClient
from subway_rag.app.city_vocabulary_mapper import CityVocabularyMapper


class RagQuestionHandler:
    """Answers public RAG questions with the model's internal vocabulary."""

    def __init__(
        self,
        model_client: BaseModelClient,
        vocabulary_mapper: CityVocabularyMapper,
    ) -> None:
        self._model_client = model_client
        self._vocabulary_mapper = vocabulary_mapper

    async def answer(self, question: str, subway_network: str) -> dict[str, object]:
        internal_question = self._vocabulary_mapper.to_internal(question)
        internal_network = self._vocabulary_mapper.to_internal(subway_network)
        result = await self._model_client.answer(internal_question, internal_network)
        return self._to_public_result(result)

    def _to_public_result(self, result: dict[str, object]) -> dict[str, object]:
        return {
            **result,
            "answer": self._vocabulary_mapper.to_public(str(result["answer"])),
            "reasoning_summary": self._vocabulary_mapper.to_public(
                str(result["reasoning_summary"])
            ),
        }
