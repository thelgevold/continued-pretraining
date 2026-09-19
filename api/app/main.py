from fastapi import FastAPI

from app.clients import OllamaClient
from app.config import AppConfig
from app.handlers import QuestionHandler
from app.models import QuestionRequest, QuestionResponse
from app.services.city_announcements_retriever import CityAnnouncementsRetriever

config = AppConfig()
ollama_client = OllamaClient(
    base_url=config.ollama_base_url,
    model_name=config.ollama_model_name,
)
question_handler = QuestionHandler(
    ollama_client=ollama_client,
    city_announcements_retriever=CityAnnouncementsRetriever(
        documents_path=config.city_announcements_path,
        chroma_path=config.city_announcements_chroma_path,
    ),
)
app = FastAPI()


@app.post("/question", response_model=QuestionResponse)
async def question(request: QuestionRequest) -> QuestionResponse:
    return await question_handler.handle(request)
