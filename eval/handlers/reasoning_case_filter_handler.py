from eval.models.reasoning_case import ReasoningCase


class ReasoningCaseFilterHandler:
    def filter_cases(
        self,
        cases: list[ReasoningCase],
        name_prefix: str | None,
    ) -> list[ReasoningCase]:
        if not name_prefix:
            return cases
        if "," in name_prefix:
            return self._filter_exact_names(cases, name_prefix)
        filtered_cases = [
            case for case in cases if case.name.startswith(name_prefix)
        ]
        if not filtered_cases:
            raise RuntimeError(
                f"No reasoning cases matched name prefix: {name_prefix}"
            )
        return filtered_cases

    def _filter_exact_names(
        self,
        cases: list[ReasoningCase],
        names_text: str,
    ) -> list[ReasoningCase]:
        requested_names = {
            name.strip() for name in names_text.split(",") if name.strip()
        }
        filtered_cases = [case for case in cases if case.name in requested_names]
        found_names = {case.name for case in filtered_cases}
        missing_names = requested_names - found_names
        if missing_names:
            raise RuntimeError(
                "No reasoning case matched exact name(s): "
                + ", ".join(sorted(missing_names))
            )
        return filtered_cases
