from copy import deepcopy
from pathlib import Path

from eval.handlers.deterministic_reasoning_judge_handler import (
    DeterministicReasoningJudgeHandler,
)
from eval.handlers.reasoning_case_loader import ReasoningCaseLoader


CASES = {
    case.name: case
    for case in ReasoningCaseLoader(
        Path("eval/cases/reasoning_cases.json")
    ).load_cases()
}
JUDGE = DeterministicReasoningJudgeHandler()


def test_compact_direct_route_passes() -> None:
    case = CASES["general_single_line_routes_01"]

    result = JUDGE.evaluate_answer(case.expected_answer, case)

    assert result["is_correct"] is True


def test_non_json_answer_fails() -> None:
    case = CASES["general_single_line_routes_01"]

    result = JUDGE.evaluate_answer("Take the Green Line.", case)

    assert result["is_correct"] is False
    assert result["incorrect_facts"] == ["Answer is not valid JSON."]


def test_wrong_station_line_fails() -> None:
    case = CASES["general_transfer_routes_01"]
    answer = deepcopy(case.expected_answer)
    answer["answer"]["result"]["legs"][1]["line"] = "Blue Line"

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is False


def test_noncentral_transfer_fails() -> None:
    case = CASES["general_two_transfer_routes_01"]
    answer = deepcopy(case.expected_answer)
    answer["answer"]["result"]["legs"][2]["to"] = "Innovation Park"
    answer["answer"]["result"]["legs"][3]["from"] = "Innovation Park"
    answer["answer"]["result"]["transfer_stations"][1] = "Innovation Park"

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is False


def test_extra_route_field_is_ignored() -> None:
    case = CASES["general_single_line_routes_01"]
    answer = deepcopy(case.expected_answer)
    answer["answer"]["result"]["transfer_count"] = 0

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is True


def test_string_values_are_compared_case_insensitively() -> None:
    case = CASES["general_single_line_routes_01"]
    answer = deepcopy(case.expected_answer)
    result_payload = answer["answer"]["result"]
    result_payload["legs"][0]["line"] = "green line"
    result_payload["legs"][0]["from"] = "emerald hills"
    result_payload["legs"][0]["to"] = "museum district station"

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is True


def test_bare_line_name_is_equivalent_to_line_name_with_suffix() -> None:
    case = CASES["general_single_line_routes_01"]
    answer = deepcopy(case.expected_answer)
    answer["answer"]["result"]["legs"][0]["line"] = "Green"

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is True


def test_contiguous_same_line_legs_are_semantically_equivalent() -> None:
    case = CASES["general_two_transfer_routes_05"]
    answer = deepcopy(case.expected_answer)
    legs = answer["answer"]["result"]["legs"]
    legs[1:2] = [
        {
            "line": "Green Line",
            "from": "Central Station",
            "to": "Innovation Park",
        },
        {
            "line": "Green Line",
            "from": "Innovation Park",
            "to": "Lake Harmony",
        },
    ]

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is True


def test_city_plain_text_route_passes() -> None:
    case = next(
        case
        for case in ReasoningCaseLoader(Path("city_training/eval")).load_cases()
        if case.name == "heldout_one_transfer_01"
    )
    answer = (
        "Take Gold Line from Westgate to Central Station. Transfer at Central "
        "Station to Blue Line and continue to University Commons."
    )

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is True


def test_city_plain_text_transfer_route_passes() -> None:
    case = next(
        case
        for case in ReasoningCaseLoader(Path("city_training/eval")).load_cases()
        if case.name == "heldout_one_transfer_01"
    )
    answer = (
        "Ride Gold Line from Westgate to Central Station. Transfer at Central "
        "Station to Blue Line and continue to University Commons."
    )

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is True


def test_city_plain_text_two_errand_route_passes() -> None:
    case = next(
        case
        for case in ReasoningCaseLoader(Path("city_training/eval")).load_cases()
        if case.name == "heldout_two_transfer_01"
    )
    answer = (
        "First take Gold Line from Westgate to Central Station, then transfer "
        "to Blue Line for North Terminal. Next take Blue Line from North "
        "Terminal to Central Station and transfer to Green Line for Museum "
        "District Station."
    )

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is True


def test_city_plain_text_route_with_missing_line_fails() -> None:
    case = next(
        case
        for case in ReasoningCaseLoader(Path("city_training/eval")).load_cases()
        if case.name == "heldout_two_transfer_01"
    )
    answer = (
        "Travel from Westgate to Central Station, then continue to North "
        "Terminal. Next go from North Terminal to Central Station and continue "
        "to Museum District Station."
    )

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is False


def test_city_route_with_a_wrong_inner_leg_fails() -> None:
    case = next(
        case
        for case in ReasoningCaseLoader(Path("city_training/eval")).load_cases()
        if case.name == "heldout_one_transfer_01"
    )
    answer = (
        "Take Gold Line from Westgate to Central Station. Transfer to Green Line "
        "and travel to University Commons."
    )

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is False


def test_historic_site_route_ignores_non_material_route_properties() -> None:
    case = next(
        case
        for case in ReasoningCaseLoader(Path("eval/cases/reasoning_cases.json")).load_cases()
        if case.section == "historic_site_routes"
    )
    answer = deepcopy(case.expected_answer)
    answer["answer"]["result"]["access_station"] = "Old Mill Station"

    route = answer["answer"]["result"]["subway_route"]
    assert set(route[0]) == {
        "subway_line",
        "from_station",
        "to_station",
        "target_site",
    }
    answer["answer"]["result"]["site"] = "Incorrect historic site"
    answer["answer"]["result"]["target_site"] = "Incorrect historic site"
    route[0]["target_site"] = "Incorrect historic site"

    result = JUDGE.evaluate_answer(answer, case)

    assert result["is_correct"] is True
