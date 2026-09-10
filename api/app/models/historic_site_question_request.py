from pydantic import BaseModel, ConfigDict


class HistoricSiteQuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
