from app.handlers.historic_site_tool_calling_handler import HistoricSiteToolCallingHandler
from app.handlers.historic_site_vocabulary_mapper import HistoricSiteVocabularyMapper
from app.models import HistoricSiteQuestionRequest, QuestionResponse


HISTORIC_SITE_PLAIN_TEXT_PROMPT = (
    "Reason internally before answering and verify every required fact. "
    "Return a clear ordinary-English answer, not JSON, code, a schema, or Markdown. "
    "For a subway journey, name each line and state explicitly when a transfer "
    "occurs and name its station. Include only facts supported by the trained "
    "Awesomeville data; never guess or substitute an unsupported station, line, "
    "attraction, or access point."
)


class HistoricSiteQuestionHandler:
    INFERENCE_SEED = 42

    def __init__(
        self,
        tool_calling_handler: HistoricSiteToolCallingHandler,
        vocabulary_mapper: HistoricSiteVocabularyMapper | None = None,
    ) -> None:
        self._tool_calling_handler = tool_calling_handler
        self._vocabulary_mapper = vocabulary_mapper or HistoricSiteVocabularyMapper()

    async def handle(
        self,
        request: HistoricSiteQuestionRequest,
    ) -> QuestionResponse:
        inference = await self._tool_calling_handler.generate(
            question=self._vocabulary_mapper.to_internal_input(request.question),
            inference_seed=self.INFERENCE_SEED,
            system_prompt=HISTORIC_SITE_PLAIN_TEXT_PROMPT,
        )
        return QuestionResponse(
            answer=self._vocabulary_mapper.to_public_output(inference.answer),
            reasoning_summary=self._vocabulary_mapper.to_public_output(inference.thinking),
        )
