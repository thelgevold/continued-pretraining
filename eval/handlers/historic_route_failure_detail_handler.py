class HistoricRouteFailureDetailHandler:
    """Explains material differences in historic-site route answers."""

    def create_details(
        self,
        expected_answer: dict[str, object],
        actual_answer: dict[str, object],
    ) -> list[str]:
        expected_result = self._result(expected_answer)
        actual_result = self._result(actual_answer)
        if not actual_result:
            return ["The answer does not contain a historic-site route result."]

        details = self._route_details(expected_result, actual_result)
        return details

    @staticmethod
    def _result(answer: dict[str, object]) -> dict[str, object]:
        answer_object = answer.get("answer")
        if not isinstance(answer_object, dict):
            return {}
        result = answer_object.get("result")
        return result if isinstance(result, dict) else {}

    def _route_details(
        self,
        expected_result: dict[str, object],
        actual_result: dict[str, object],
    ) -> list[str]:
        expected_route = self._route(expected_result)
        actual_route = self._route(actual_result)
        details: list[str] = []
        for index, expected_leg in enumerate(expected_route):
            if index >= len(actual_route):
                details.append(
                    f"Missing route leg {index + 1}: {self._describe_leg(expected_leg)}."
                )
                continue
            actual_leg = actual_route[index]
            if self._material_leg(actual_leg) != self._material_leg(expected_leg):
                details.append(
                    f"Route leg {index + 1} must be {self._describe_leg(expected_leg)}, "
                    f"not {self._describe_leg(actual_leg)}."
                )
        if len(actual_route) > len(expected_route):
            details.append("The answer contains an extra subway route leg.")
        return details

    @staticmethod
    def _route(result: dict[str, object]) -> list[dict[str, object]]:
        route = result.get("subway_route")
        if not isinstance(route, list):
            return []
        return [leg for leg in route if isinstance(leg, dict)]

    @staticmethod
    def _material_leg(leg: dict[str, object]) -> tuple[object, object, object]:
        return (
            leg.get("subway_line"),
            leg.get("from_station"),
            leg.get("to_station"),
        )

    @staticmethod
    def _describe_leg(leg: dict[str, object]) -> str:
        return (
            f"{leg.get('subway_line')!r} from {leg.get('from_station')!r} "
            f"to {leg.get('to_station')!r}"
        )
