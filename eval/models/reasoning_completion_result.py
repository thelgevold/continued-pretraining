from dataclasses import dataclass


@dataclass(frozen=True)
class ReasoningCompletionResult:
    name: str
    question: str
    expected_answer: dict[str, object]
    actual_answer: str | dict[str, object]
    reasoning_summary: str
