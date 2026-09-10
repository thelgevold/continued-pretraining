import re

from eval.models.reasoning_case import ReasoningCase


class CityPlainTextReasoningJudgeHandler:
    def evaluate_answer(
        self,
        answer: str | dict[str, object],
        reasoning_case: ReasoningCase,
    ) -> dict[str, object]:
        answer_text = self._answer_text(answer)
        if not answer_text:
            return self._failure("Answer is empty.")
        if self._looks_like_json(answer_text):
            return self._failure("Answer must be ordinary English, not JSON.")
        missing_facts = self._missing_facts(answer_text, reasoning_case)
        if missing_facts:
            return self._failure(*missing_facts)
        return {
            "is_correct": True,
            "score": 100.0,
            "reason": "All required route facts are present in plain English.",
            "missing_facts": [],
            "incorrect_facts": [],
        }

    @staticmethod
    def _answer_text(answer: str | dict[str, object]) -> str:
        if isinstance(answer, str):
            return answer
        value = answer.get("unparsed_response")
        return str(value) if isinstance(value, str) else ""

    @staticmethod
    def _looks_like_json(answer: str) -> bool:
        return answer.lstrip().startswith(("{", "["))

    def _missing_facts(
        self,
        answer: str,
        reasoning_case: ReasoningCase,
    ) -> list[str]:
        normalized_answer = self._normalize(answer)
        expected_answer = reasoning_case.expected_answer
        if "answer" in expected_answer:
            if self._is_historic_site_lookup(expected_answer):
                return self._missing_historic_site_lookup_facts(
                    normalized_answer,
                    expected_answer,
                )
            return self._missing_membership_facts(normalized_answer, expected_answer)
        missing_facts = self._missing_journey_facts(normalized_answer, expected_answer)
        missing_facts.extend(self._missing_site_facts(normalized_answer, expected_answer))
        return missing_facts

    def _missing_site_facts(
        self,
        answer: str,
        expected_answer: dict[str, object],
    ) -> list[str]:
        site_facts = expected_answer.get("site_facts", [])
        if not isinstance(site_facts, list):
            raise RuntimeError("City site facts must be a list.")
        return [
            f"Missing retrieved historic-site fact: {fact}."
            for fact in site_facts
            if self._normalize(str(fact)) not in answer
        ]

    @staticmethod
    def _is_historic_site_lookup(expected_answer: dict[str, object]) -> bool:
        answer = expected_answer["answer"]
        return isinstance(answer, dict) and answer.get("operation") == "historic_site_station_lookup"

    def _missing_historic_site_lookup_facts(
        self,
        answer: str,
        expected_answer: dict[str, object],
    ) -> list[str]:
        answer_object = expected_answer["answer"]
        if not isinstance(answer_object, dict):
            raise RuntimeError("Historic lookup expected answer must contain an answer object.")
        result = answer_object["result"]
        if not isinstance(result, dict):
            raise RuntimeError("Historic lookup expected answer must contain a result object.")
        station = str(result["station"])
        if self._normalize(station) in answer:
            return []
        return [f"Missing required historic-site station: {station}."]

    def _missing_membership_facts(
        self,
        answer: str,
        expected_answer: dict[str, object],
    ) -> list[str]:
        result = self._membership_result(expected_answer)
        required_values = [result["line"], *result["stations"]]
        return [
            f"Missing required fact: {value}."
            for value in required_values
            if self._normalize(value) not in answer
        ]

    def _missing_journey_facts(
        self,
        answer: str,
        expected_answer: dict[str, object],
    ) -> list[str]:
        journeys = self._journeys(expected_answer)
        missing_facts: list[str] = []
        for index, journey in enumerate(journeys, start=1):
            missing_facts.extend(
                self._missing_journey_facts_for_route(answer, journey, index)
            )
        return missing_facts

    def _missing_journey_facts_for_route(
        self,
        answer: str,
        journey: dict[str, object],
        journey_number: int,
    ) -> list[str]:
        line_sequence = self._line_sequence(journey)
        missing_facts: list[str] = []
        if not self._appears_in_order(answer, line_sequence):
            missing_facts.append(
                f"Journey {journey_number} does not state the required lines in travel order: "
                f"{' -> '.join(line_sequence)}."
            )
        return missing_facts

    @staticmethod
    def _membership_result(expected_answer: dict[str, object]) -> dict[str, list[str] | str]:
        answer = expected_answer["answer"]
        if not isinstance(answer, dict):
            raise RuntimeError("City membership expected answer must contain an answer object.")
        result = answer["result"]
        if not isinstance(result, dict):
            raise RuntimeError("City membership expected answer must contain a result object.")
        stations = result["stations"]
        if not isinstance(stations, list):
            raise RuntimeError("City membership expected answer must contain stations.")
        return {"line": str(result["line"]), "stations": [str(station) for station in stations]}

    @staticmethod
    def _journeys(expected_answer: dict[str, object]) -> list[dict[str, object]]:
        if "journey" in expected_answer:
            return [CityPlainTextReasoningJudgeHandler._journey(expected_answer["journey"])]
        journeys = expected_answer["journeys"]
        if not isinstance(journeys, list):
            raise RuntimeError("City multi-journey expected answer must contain journeys.")
        return [CityPlainTextReasoningJudgeHandler._journey(journey) for journey in journeys]

    @staticmethod
    def _journey(value: object) -> dict[str, object]:
        if not isinstance(value, dict):
            raise RuntimeError("City expected journey must be an object.")
        return value

    @staticmethod
    def _line_sequence(journey: dict[str, object]) -> list[str]:
        return [str(leg["line"]) for leg in CityPlainTextReasoningJudgeHandler._legs(journey)]

    @staticmethod
    def _legs(journey: dict[str, object]) -> list[dict[str, object]]:
        legs = journey["legs"]
        if not isinstance(legs, list):
            raise RuntimeError("City expected journey must contain legs.")
        return [
            leg
            for leg in legs
            if isinstance(leg, dict)
        ]

    def _appears_in_order(self, answer: str, values: list[str]) -> bool:
        position = 0
        for value in values:
            match = re.search(re.escape(self._normalize(value)), answer[position:])
            if match is None:
                return False
            position += match.end()
        return True

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"\s+", " ", value.casefold()).strip()

    @staticmethod
    def _failure(*errors: str) -> dict[str, object]:
        return {
            "is_correct": False,
            "score": 0.0,
            "reason": " ".join(errors),
            "missing_facts": list(errors),
            "incorrect_facts": [],
        }
