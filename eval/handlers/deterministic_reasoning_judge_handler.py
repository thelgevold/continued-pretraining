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
        if actual_answer == expected_answer:
            return self._success(
                "The route exactly matches the reference result.",
                "exact_match",
            )

        missing_legs = self._missing_legs(actual_answer, expected_answer)
        extra_legs = self._extra_legs(actual_answer, expected_answer)
        score = self._percentage(
            len(expected_answer.legs) - len(missing_legs),
            max(len(expected_answer.legs), len(actual_answer.legs)),
        )
        if self._has_only_superfluous_same_line_no_ops(
            actual_answer,
            expected_answer,
        ):
            return self._success(
                "The route matches the reference after ignoring superfluous "
                "same-line legs.",
                "semantic_same_line_match",
            )
        return {
            "is_correct": False,
            "score": score,
            "reason": "The route matches some, but not all, reference legs.",
            "match_type": "partial_match",
            "missing_facts": [self._format_leg(leg) for leg in missing_legs],
            "incorrect_facts": [self._format_leg(leg) for leg in extra_legs],
        }

    @staticmethod
    def _missing_legs(
        actual_answer: SubwayRouteSchemaAnswer,
        expected_answer: SubwayRouteSchemaAnswer,
    ) -> list[tuple[str, str, str]]:
        unmatched_actual_legs = list(actual_answer.legs)
        missing_legs = []
        for expected_leg in expected_answer.legs:
            if expected_leg in unmatched_actual_legs:
                unmatched_actual_legs.remove(expected_leg)
            else:
                missing_legs.append(expected_leg)
        return missing_legs

    @staticmethod
    def _extra_legs(
        actual_answer: SubwayRouteSchemaAnswer,
        expected_answer: SubwayRouteSchemaAnswer,
    ) -> list[tuple[str, str, str]]:
        unmatched_expected_legs = list(expected_answer.legs)
        extra_legs = []
        for actual_leg in actual_answer.legs:
            if actual_leg in unmatched_expected_legs:
                unmatched_expected_legs.remove(actual_leg)
            else:
                extra_legs.append(actual_leg)
        return extra_legs

    def _has_only_superfluous_same_line_no_ops(
        self,
        actual_answer: SubwayRouteSchemaAnswer,
        expected_answer: SubwayRouteSchemaAnswer,
    ) -> bool:
        expected_index = 0
        has_extra_leg = False
        for actual_leg in actual_answer.legs:
            if (
                expected_index < len(expected_answer.legs)
                and actual_leg == expected_answer.legs[expected_index]
            ):
                expected_index += 1
                continue
            if not self._is_superfluous_same_line_no_op(
                actual_leg,
                expected_answer.legs,
                expected_index,
            ):
                return False
            has_extra_leg = True
        return has_extra_leg and expected_index == len(expected_answer.legs)

    @staticmethod
    def _is_superfluous_same_line_no_op(
        actual_leg: tuple[str, str, str],
        expected_legs: tuple[tuple[str, str, str], ...],
        expected_index: int,
    ) -> bool:
        origin, destination, line = actual_leg
        if origin != destination:
            return False
        return any(
            station == origin and expected_line == line
            for station, expected_line in (
                (expected_legs[expected_index - 1][1], expected_legs[expected_index - 1][2])
                if expected_index > 0
                else ("", ""),
                (expected_legs[expected_index][0], expected_legs[expected_index][2])
                if expected_index < len(expected_legs)
                else ("", ""),
            )
        )

    @staticmethod
    def _percentage(correct_legs: int, total_legs: int) -> float:
        return round(correct_legs * 100 / total_legs, 1)

    @staticmethod
    def _format_leg(leg: tuple[str, str, str]) -> str:
        return f"{leg[0]} to {leg[1]} on {leg[2]}"

    @staticmethod
    def _success(reason: str, match_type: str) -> dict[str, object]:
        return {
            "is_correct": True,
            "score": 100.0,
            "reason": reason,
            "match_type": match_type,
            "missing_facts": [],
            "incorrect_facts": [],
        }

    def _failure(self, *errors: str) -> dict[str, object]:
        return {
            "is_correct": False,
            "score": 0.0,
            "reason": " ".join(errors),
            "match_type": "invalid",
            "missing_facts": [],
            "incorrect_facts": list(errors),
        }
