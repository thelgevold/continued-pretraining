from dataclasses import dataclass

from eval.models.reasoning_expectation import ReasoningExpectation


@dataclass(frozen=True)
class ReasoningCase:
    name: str
    section: str
    question: str
    expected_answer: dict[str, object]
    required_phrases: tuple[str, ...]
    expectation: ReasoningExpectation
    use_historic_site_retrieval: bool = False
