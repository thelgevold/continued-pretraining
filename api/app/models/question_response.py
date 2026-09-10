from pydantic import BaseModel


class QuestionResponse(BaseModel):
    answer: str
    reasoning_summary: str
    input_prompt_characters: int = 0
