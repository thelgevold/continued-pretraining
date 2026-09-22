import json

from eval.handlers.reasoning_report_handler import ReasoningReportHandler
from eval.models.reasoning_case import ReasoningCase
from eval.models.reasoning_expectation import ReasoningExpectation
from eval.models.reasoning_generated_completion import ReasoningGeneratedCompletion


def test_report_records_completions_without_judging(tmp_path) -> None:
    reasoning_case = ReasoningCase(
        name="example",
        section="membership",
        question="Which line serves Example Station?",
        expected_answer={"answer": "Example Line."},
        required_phrases=("Example Line",),
        expectation=ReasoningExpectation(
            journeys=(),
            require_complete_routes=False,
            transfer_count=None,
            allowed_stations=(),
            ordinal_positions=(),
        ),
    )
    handler = ReasoningReportHandler(
        report_directory=tmp_path,
        expected_cases=[reasoning_case],
        model_name="example-model",
        experiment_label="generation-only",
    )

    handler.record_completion(
        reasoning_case,
        ReasoningGeneratedCompletion(
            answer='{"answer":{"operation":"membership","result":{"line":"Example Line"}}}',
            reasoning_summary="The model matched the station to Example Line.",
        ),
    )

    report = json.loads(
        (tmp_path / "reasoning_eval_report.json").read_text(encoding="utf-8")
    )
    assert report["audit_status"] == "not_audited"
    assert report["meta"]["completions_recorded"] == 1
    assert report["results"][0]["status"] == "awaiting_audit"
    assert report["results"][0]["actual_answer"] == (
        '{"answer":{"operation":"membership","result":{"line":"Example Line"}}}'
    )
    assert report["results"][0]["reasoning_summary"] == (
        "The model matched the station to Example Line."
    )
    markdown = (tmp_path / "reasoning_eval_report.md").read_text(encoding="utf-8")
    assert (
        "Reasoning summary: The model matched the station to Example Line."
        in markdown
    )
    assert "passed" not in report["results"][0]
    assert "judge_score" not in report["results"][0]


def test_report_preserves_malformed_answer_inside_an_object(tmp_path) -> None:
    reasoning_case = ReasoningCase(
        name="malformed",
        section="membership",
        question="Which line serves Example Station?",
        expected_answer={"answer": "Example Line."},
        required_phrases=("Example Line",),
        expectation=ReasoningExpectation(
            journeys=(),
            require_complete_routes=False,
            transfer_count=None,
            allowed_stations=(),
            ordinal_positions=(),
        ),
    )
    handler = ReasoningReportHandler(
        report_directory=tmp_path,
        expected_cases=[reasoning_case],
        model_name="example-model",
    )

    handler.record_completion(
        reasoning_case,
        ReasoningGeneratedCompletion(
            answer="not valid json",
            reasoning_summary="No structured answer was produced.",
        ),
    )

    report = json.loads(
        (tmp_path / "reasoning_eval_report.json").read_text(encoding="utf-8")
    )
    assert report["results"][0]["actual_answer"] == "not valid json"


def test_report_wraps_json_route_array_like_expected_answer(tmp_path) -> None:
    reasoning_case = ReasoningCase(
        name="route",
        section="routes",
        question="Route question",
        expected_answer={
            "answer": [
                {
                    "from_station": "Westgate",
                    "to_station": "Central Station",
                    "subway_line": "Gold Line",
                }
            ]
        },
        required_phrases=(),
        expectation=ReasoningExpectation((), False, None, (), ()),
    )
    handler = ReasoningReportHandler(
        report_directory=tmp_path,
        expected_cases=[reasoning_case],
        model_name="example-model",
    )

    handler.record_completion(
        reasoning_case,
        ReasoningGeneratedCompletion(
            answer=(
                '[{"from_station":"Westgate","to_station":"Central Station",'
                '"subway_line":"Gold Line"}]'
            ),
            reasoning_summary="Structured route.",
        ),
    )

    report = json.loads(
        (tmp_path / "reasoning_eval_report.json").read_text(encoding="utf-8")
    )
    assert report["results"][0]["actual_answer"] == reasoning_case.expected_answer
