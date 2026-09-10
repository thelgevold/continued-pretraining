import os
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from subway_rag.app.base_model_client import BaseModelClient
from subway_rag.app.subway_network_index import SubwayNetworkIndex


class QuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str


class QuestionResponse(BaseModel):
    answer: str
    reasoning_summary: str


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


model_client = BaseModelClient(
    base_url=_require("OLLAMA_BASE_URL"),
    model_name=_require("SUBWAY_RAG_BASE_MODEL"),
)
subway_network_index = SubwayNetworkIndex(Path("/app/documents/subway_network.txt"))
app = FastAPI()


@app.post("/question", response_model=QuestionResponse)
async def question(request: QuestionRequest) -> QuestionResponse:
    result = await model_client.answer(request.question, subway_network_index.retrieve())
    return QuestionResponse(**result)
