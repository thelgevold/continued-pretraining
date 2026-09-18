from eval.models.reasoning_case import ReasoningCase
from eval.models.subway_route_schema_answer import SubwayRouteSchemaAnswer


class DeterministicReasoningJudgeHandler:
    def evaluate_answer(
        self,
        answer: str | dict[str, object] | list[object],
        reasoning_case: ReasoningCase,
    ) -> dict[str, object]:
        try:
            expected_answer = SubwayRouteSchemaAnswer.deserialize(
                reasoning_case.expected_answer["answer"]
            )
            actual_answer = SubwayRouteSchemaAnswer.deserialize(answer)
        except ValueError as error:
            return self._failure(str(error))
        if actual_answer != expected_answer:
            return self._failure("Answer does not match the expected route legs.")
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
