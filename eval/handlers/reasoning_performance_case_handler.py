from pathlib import Path

from eval.handlers.reasoning_case_loader import ReasoningCaseLoader
from eval.models.reasoning_case import ReasoningCase


class ReasoningPerformanceCaseHandler:
    def __init__(self, cases_path: Path) -> None:
        self._cases_path = cases_path
        self._loader = ReasoningCaseLoader(cases_path=cases_path)

    def load_dynamic_cases(
        self,
        name_filter: str | None,
        excluded_prefix: str | None = None,
    ) -> list[ReasoningCase]:
        return [
            case
            for case in self._loader.load_cases()
            if self._matches(case.name, name_filter)
            and not self._is_excluded(case.name, excluded_prefix)
        ]

    def load_report_cases(
        self,
        name_filter: str | None,
        excluded_prefix: str | None = None,
    ) -> list[ReasoningCase]:
        cases = self.load_dynamic_cases(name_filter, excluded_prefix)
        if not cases:
            raise RuntimeError(f"No reasoning cases matched name prefix: {name_filter}")
        return cases

    def _matches(self, case_name: str, name_filter: str | None) -> bool:
        if not name_filter:
            return True
        if "," in name_filter:
            return case_name in {
                name.strip() for name in name_filter.split(",") if name.strip()
            }
        return case_name.startswith(name_filter)

    def _is_excluded(self, case_name: str, excluded_prefix: str | None) -> bool:
        return bool(excluded_prefix) and self._matches(case_name, excluded_prefix)
