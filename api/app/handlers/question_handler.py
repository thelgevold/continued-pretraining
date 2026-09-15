from app.clients import OllamaClient
from app.handlers.city_vocabulary_mapper import CityVocabularyMapper
from app.models import QuestionRequest, QuestionResponse
from app.services.city_announcements_retriever import CityAnnouncementsRetriever


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

CITY_ANNOUNCEMENTS_PROMPT = (
    "\n\nCity-announcement context follows. Use it only when it is relevant to "
    "the question. Treat relevant announcements as current, authoritative facts "
    "and do not contradict them.\n\n"
)


class QuestionHandler:
    INFERENCE_SEED = 42

    def __init__(
        self,
        ollama_client: OllamaClient,
        city_announcements_retriever: CityAnnouncementsRetriever,
        vocabulary_mapper: CityVocabularyMapper | None = None,
    ) -> None:
        self._ollama_client = ollama_client
        self._city_announcements_retriever = city_announcements_retriever
        self._vocabulary_mapper = vocabulary_mapper or CityVocabularyMapper()

    async def handle(self, request: QuestionRequest) -> QuestionResponse:
        announcement_context = self._city_announcements_retriever.retrieve(
            request.question
        )
        model_question = self._vocabulary_mapper.to_synthetic_input(request.question)
        model_announcement_context = self._vocabulary_mapper.to_synthetic_input(
            announcement_context
        )
        system_prompt = self._system_prompt(model_announcement_context)
        inference = await self._ollama_client.ask_question(
            question=model_question,
            inference_seed=self.INFERENCE_SEED,
            system_prompt=system_prompt,
        )
        return QuestionResponse(
            answer=self._vocabulary_mapper.to_human_output(inference.answer),
            reasoning_summary=self._vocabulary_mapper.to_human_output(inference.thinking),
            input_prompt_characters=len(system_prompt) + len(model_question),
        )

    @staticmethod
    def _system_prompt(announcement_context: str) -> str:
        return (
            f"{CITY_PLAIN_TEXT_PROMPT}{CITY_ANNOUNCEMENTS_PROMPT}"
            f"{announcement_context}"
        )
