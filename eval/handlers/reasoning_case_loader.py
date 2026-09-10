import json
from pathlib import Path

from eval.models.reasoning_case import ReasoningCase
from eval.models.reasoning_expectation import ReasoningExpectation


class ReasoningCaseLoader:
    def __init__(self, cases_path: Path) -> None:
        self._cases_path = cases_path

    def load_cases(self) -> list[ReasoningCase]:
        raw_cases = self._load_raw_cases()
        return [self._create_case(raw_case) for raw_case in raw_cases]

    def _load_raw_cases(self) -> list[dict]:
        if self._cases_path.is_dir():
            return self._load_directory_cases()
        return self._load_file_cases(self._cases_path)

    def _load_directory_cases(self) -> list[dict]:
        return [
            raw_case
            for cases_path in self._case_paths()
            for raw_case in self._load_file_cases(cases_path)
        ]

    def _case_paths(self) -> list[Path]:
        return sorted(
            [
                *self._cases_path.glob("*.json"),
                *self._cases_path.glob("*.jsonl"),
            ]
        )

    @classmethod
    def _load_file_cases(cls, cases_path: Path) -> list[dict]:
        if cases_path.suffix == ".jsonl":
            return cls._load_jsonl_cases(cases_path)
        return cls._load_json_cases(cases_path)

    @staticmethod
    def _load_json_cases(cases_path: Path) -> list[dict]:
        raw_cases = json.loads(cases_path.read_text(encoding="utf-8"))
        if not isinstance(raw_cases, list):
            raise RuntimeError(f"Reasoning cases in {cases_path} must be a JSON array.")
        return raw_cases

    @staticmethod
    def _load_jsonl_cases(cases_path: Path) -> list[dict]:
        return [
            json.loads(line)
            for line in cases_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _create_case(self, raw_case: dict) -> ReasoningCase:
        expected_answer = raw_case["expected_answer"]
        self._validate_expected_answer(raw_case["section"], expected_answer)
        return ReasoningCase(
            name=raw_case["name"],
            section=raw_case["section"],
            question=raw_case["question"],
            expected_answer=expected_answer,
            required_phrases=tuple(raw_case["required_phrases"]),
            expectation=self._create_expectation(raw_case["expectation"]),
            use_historic_site_retrieval=(
                raw_case["section"] == "city_historic_site_rag_routes"
            ),
        )

    @staticmethod
    def _validate_expected_answer(section: object, expected_answer: object) -> None:
        if not isinstance(expected_answer, dict):
            raise RuntimeError("Expected answer must be a JSON object.")
        if str(section).startswith("city_") and set(expected_answer) in (
            {"journey", "description"},
            {"journeys", "description"},
            {"journey", "description", "site_facts"},
        ):
            return
        if set(expected_answer) != {"answer"}:
            raise RuntimeError("Expected answers require one JSON answer field.")

    def _create_expectation(self, raw_expectation: dict) -> ReasoningExpectation:
        return ReasoningExpectation(
            journeys=tuple(
                (str(journey[0]), str(journey[1]))
                for journey in raw_expectation.get("journeys", [])
            ),
            require_complete_routes=bool(
                raw_expectation.get("require_complete_routes", False)
            ),
            transfer_count=raw_expectation.get("transfer_count"),
            allowed_stations=tuple(raw_expectation.get("allowed_stations", [])),
            ordinal_positions=tuple(
                (int(position), str(station))
                for position, station in raw_expectation.get(
                    "ordinal_positions",
                    {},
                ).items()
            ),
            station_line_memberships=tuple(
                (str(station), tuple(str(line) for line in lines))
                for station, lines in raw_expectation.get(
                    "station_line_memberships",
                    {},
                ).items()
            ),
        )
