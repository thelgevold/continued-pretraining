import pytest

from eval.handlers.reasoning_case_filter_handler import ReasoningCaseFilterHandler
from eval.handlers.reasoning_case_loader import ReasoningCaseLoader
from pathlib import Path


def test_filter_selects_only_transfer_route_cases() -> None:
    cases = ReasoningCaseLoader(
        Path("eval/cases/reasoning_cases.json")
    ).load_cases()

    filtered_cases = ReasoningCaseFilterHandler().filter_cases(
        cases,
        "general_transfer_routes_",
    )

    assert len(filtered_cases) == 25
    assert all(
        case.name.startswith("general_transfer_routes_")
        for case in filtered_cases
    )


def test_filter_rejects_unknown_prefix() -> None:
    with pytest.raises(RuntimeError, match="No reasoning cases matched"):
        ReasoningCaseFilterHandler().filter_cases([], "missing_")


def test_filter_selects_comma_separated_exact_names() -> None:
    cases = ReasoningCaseLoader(
        Path("eval/cases/reasoning_cases.json")
    ).load_cases()

    filtered_cases = ReasoningCaseFilterHandler().filter_cases(
        cases,
        "general_transfer_routes_08,general_two_transfer_routes_11",
    )

    assert [case.name for case in filtered_cases] == [
        "general_transfer_routes_08",
        "general_two_transfer_routes_11",
    ]


def test_filter_rejects_missing_exact_name() -> None:
    cases = ReasoningCaseLoader(
        Path("eval/cases/reasoning_cases.json")
    ).load_cases()

    with pytest.raises(RuntimeError, match="missing_case"):
        ReasoningCaseFilterHandler().filter_cases(
            cases,
            "general_single_line_routes_08,missing_case",
        )
