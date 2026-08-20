from pydantic import BaseModel


class QuestionResponse(BaseModel):
    answer: str
    reasoning_summary: str
