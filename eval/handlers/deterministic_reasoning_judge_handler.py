from eval.models.reasoning_case import ReasoningCase
from eval.models.structured_reasoning_answer import StructuredReasoningAnswer
from eval.handlers.city_plain_text_reasoning_judge_handler import (
    CityPlainTextReasoningJudgeHandler,
)


class DeterministicReasoningJudgeHandler:
    def __init__(self) -> None:
        self._city_plain_text_judge_handler = CityPlainTextReasoningJudgeHandler()

    def evaluate_answer(
        self,
        answer: str | dict[str, object],
        reasoning_case: ReasoningCase,
    ) -> dict[str, object]:
        if reasoning_case.section.startswith("city_"):
            return self._city_plain_text_judge_handler.evaluate_answer(
                answer,
                reasoning_case,
            )
        try:
            actual_answer = StructuredReasoningAnswer.deserialize(answer)
            expected_answer = StructuredReasoningAnswer.deserialize(
                reasoning_case.expected_answer
            )
        except ValueError as error:
            return self._failure(str(error))
        if actual_answer != expected_answer:
            return self._failure("Answer does not match the expected structured result.")
        return {
            "is_correct": True,
            "score": 100.0,
            "reason": "All required facts are correct.",
            "missing_facts": [],
            "incorrect_facts": [],
        }

    def _failure(self, *errors: str) -> dict[str, object]:
        return {
            "is_correct": False,
            "score": 0.0,
            "reason": " ".join(errors),
            "missing_facts": [],
            "incorrect_facts": list(errors),
        }
