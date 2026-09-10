from dataclasses import dataclass


@dataclass(frozen=True)
class ReasoningGeneratedCompletion:
    answer: str
    reasoning_summary: str
    runtime_seconds: float = 0.0
    input_prompt_characters: int = 0
