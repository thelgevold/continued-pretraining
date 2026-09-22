from app.clients import OllamaClient
from app.handlers.city_vocabulary_mapper import CityVocabularyMapper
from app.models import QuestionRequest, QuestionResponse
from app.services.city_announcements_retriever import CityAnnouncementsRetriever


CITY_PLAIN_TEXT_PROMPT = (
    "Reason internally before answering and verify every required fact. "
    "Return only a valid JSON array with no Markdown or surrounding text. "
    "Every array item must have exactly these string properties: "
    "from_station, to_station, subway_line. Each item must describe exactly "
    "one subway line; never use one leg to span stations on different lines. "
    "For every requested journey, emit all line legs for the complete route "
    "from its requested origin through every transfer to its requested final "
    "destination; never skip a segment before or after a transfer. "
    "Represent every transfer with two adjacent legs whose stations meet at "
    "Central Station. Each leg must state its subway line, origin, and "
    "destination; intermediate stations are not required. Explicitly represent "
    "every Central Station transfer. The first leg of each journey starts at "
    "its requested origin, and its final leg ends at its requested destination. "
    "For a request containing multiple connected journeys, continue each next "
    "journey from the previous journey's destination. If that origin and its "
    "next destination are on the same line, emit one direct leg on that line. "
    "Otherwise, route through Central Station and explicitly represent the "
    "line change there. Complete every leg in the requested order. Include only "
    "facts supported by the trained Awesomeville data; "
    "never guess or substitute an unsupported station, line, attraction, or "
    "access point. A route leg begins at the requested origin or the previous "
    "interchange and ends at the next interchange or requested destination. "
    "Do not include stations before the origin or after the destination. "
    "Your entire response must be one parseable JSON array. Start with [ and "
    "end with ]. The final characters must be \"}]\". Do not emit Markdown, "
    "explanations, reasoning, tool tags, thinking tags, user text, backticks, "
    "or any characters after the closing ]."
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
