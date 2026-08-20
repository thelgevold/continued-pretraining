from dataclasses import dataclass


@dataclass(frozen=True)
class ReasoningGeneratedCompletion:
    answer: str
    reasoning_summary: str
