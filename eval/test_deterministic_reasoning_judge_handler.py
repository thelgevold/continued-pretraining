from pathlib import Path

from eval.handlers.deterministic_reasoning_judge_handler import (
    DeterministicReasoningJudgeHandler,
)
from eval.handlers.reasoning_case_loader import ReasoningCaseLoader


CASE = ReasoningCaseLoader(
    Path("eval/cases/transfer_heldout_json_cases.jsonl")
).load_cases()[0]
JUDGE = DeterministicReasoningJudgeHandler()


def test_schema_route_leg_array_passes() -> None:
    result = JUDGE.evaluate_answer(
        """[
            {"from_station":"Westgate","to_station":"Central Station","subway_line":"Gold Line"},
            {"from_station":"Central Station","to_station":"University Commons","subway_line":"Blue Line"}
        ]""",
        CASE,
    )

    assert result["is_correct"] is True
    assert result["score"] == 100.0
    assert result["match_type"] == "exact_match"


def test_one_correct_leg_receives_partial_correctness_score() -> None:
    result = JUDGE.evaluate_answer(
        """[
            {"from_station":"Westgate","to_station":"Central Station","subway_line":"Gold Line"}
        ]""",
        CASE,
    )

    assert result["is_correct"] is False
    assert result["score"] == 50.0
    assert result["missing_facts"] == [
        "central station to university commons on blue line"
    ]


def test_extra_same_line_leg_is_semantically_correct() -> None:
    result = JUDGE.evaluate_answer(
        """[
            {"from_station":"Westgate","to_station":"Central Station","subway_line":"Gold Line"},
            {"from_station":"Central Station","to_station":"University Commons","subway_line":"Blue Line"},
            {"from_station":"University Commons","to_station":"University Commons","subway_line":"Blue Line"}
        ]""",
        CASE,
    )

    assert result["is_correct"] is True
    assert result["score"] == 100.0
    assert result["match_type"] == "semantic_same_line_match"


def test_extra_same_line_detour_is_not_semantically_correct() -> None:
    result = JUDGE.evaluate_answer(
        """[
            {"from_station":"Westgate","to_station":"Central Station","subway_line":"Gold Line"},
            {"from_station":"Central Station","to_station":"University Commons","subway_line":"Blue Line"},
            {"from_station":"University Commons","to_station":"Central Station","subway_line":"Blue Line"},
            {"from_station":"Central Station","to_station":"University Commons","subway_line":"Blue Line"}
        ]""",
        CASE,
    )

    assert result["is_correct"] is False
    assert result["match_type"] == "partial_match"
    assert result["score"] == 50.0


def test_non_json_answer_fails() -> None:
    result = JUDGE.evaluate_answer("Take the Gold Line.", CASE)

    assert result["is_correct"] is False
    assert result["incorrect_facts"] == ["Answer is not valid JSON."]


def test_alternate_leg_property_fails() -> None:
    result = JUDGE.evaluate_answer(
        """[
            {"from_station":"Westgate","to_station":"Central Station","line":"Gold Line"}
        ]""",
        CASE,
    )

    assert result["is_correct"] is False
    assert result["incorrect_facts"] == [
        "Each route leg must match the required schema."
    ]


def test_wrapped_array_fails() -> None:
    result = JUDGE.evaluate_answer(
        '{"route":[{"from_station":"Westgate","to_station":"Central Station",'
        '"subway_line":"Gold Line"}]}',
        CASE,
    )

    assert result["is_correct"] is False
    assert result["incorrect_facts"] == ["Answer must be a non-empty JSON array."]
