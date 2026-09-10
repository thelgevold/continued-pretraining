from app.clients import OllamaClient
from app.handlers.city_vocabulary_mapper import CityVocabularyMapper
from app.models import QuestionRequest, QuestionResponse

CITY_PLAIN_TEXT_PROMPT = (
    "Reason internally before answering and verify every required fact. "
    "Return a clear ordinary-English answer, not JSON, code, a schema, or "
    "Markdown. For a subway journey, name each line. State explicitly when a "
    "transfer occurs and name its "
    "station. Include only facts supported by the trained Awesomeville data; "
    "never guess or substitute an unsupported station, line, attraction, or "
    "access point. A route leg begins at the requested origin or the previous "
    "interchange and ends at the next interchange or requested destination. "
    "Do not include stations before the origin or after the destination."
)


class QuestionHandler:
    INFERENCE_SEED = 42

    def __init__(
        self,
        ollama_client: OllamaClient,
        vocabulary_mapper: CityVocabularyMapper | None = None,
    ) -> None:
        self._ollama_client = ollama_client
        self._vocabulary_mapper = vocabulary_mapper or CityVocabularyMapper()

    async def handle(self, request: QuestionRequest) -> QuestionResponse:
        inference = await self._ollama_client.ask_question(
            question=self._vocabulary_mapper.to_synthetic_input(request.question),
            inference_seed=self.INFERENCE_SEED,
            system_prompt=CITY_PLAIN_TEXT_PROMPT,
        )
        return QuestionResponse(
            answer=self._vocabulary_mapper.to_human_output(inference.answer),
            reasoning_summary=self._vocabulary_mapper.to_human_output(inference.thinking),
        )
