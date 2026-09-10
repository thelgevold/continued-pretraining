from fastapi import FastAPI

from app.clients import (
    HistoricSiteOllamaClient,
    HistoricSiteRetrievalClient,
    OllamaClient,
)
from app.config import AppConfig
from app.handlers import (
    HistoricSiteQuestionHandler,
    HistoricSiteToolCallingHandler,
    QuestionHandler,
)
from app.models import HistoricSiteQuestionRequest, QuestionRequest, QuestionResponse

config = AppConfig()
ollama_client = OllamaClient(
    base_url=config.ollama_base_url,
    model_name=config.ollama_model_name,
)
historic_site_retrieval_client = HistoricSiteRetrievalClient(
    server_url=config.historic_site_mcp_url,
)
historic_site_ollama_client = HistoricSiteOllamaClient(
    base_url=config.ollama_base_url,
    model_name=config.ollama_model_name,
)
question_handler = QuestionHandler(ollama_client=ollama_client)
historic_site_question_handler = HistoricSiteQuestionHandler(
    tool_calling_handler=HistoricSiteToolCallingHandler(
        ollama_client=historic_site_ollama_client,
        retrieval_client=historic_site_retrieval_client,
    ),
)
app = FastAPI()


@app.post("/question", response_model=QuestionResponse)
async def question(request: QuestionRequest) -> QuestionResponse:
    return await question_handler.handle(request)


@app.post("/historic-site-question", response_model=QuestionResponse)
async def historic_site_question(
    request: HistoricSiteQuestionRequest,
) -> QuestionResponse:
    return await historic_site_question_handler.handle(request)
