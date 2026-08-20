from pydantic import BaseModel, ConfigDict


class QuestionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
