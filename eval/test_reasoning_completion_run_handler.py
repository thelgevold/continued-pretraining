from eval.handlers.reasoning_completion_run_handler import (
    ReasoningCompletionRunHandler,
)
from eval.models.reasoning_case import ReasoningCase
from eval.models.reasoning_expectation import ReasoningExpectation
from eval.models.reasoning_generated_completion import ReasoningGeneratedCompletion


def test_run_generates_and_records_completion() -> None:
    case = _case()
    completion_handler = _CompletionHandler()
    report_handler = _ReportHandler()

    ReasoningCompletionRunHandler(completion_handler, report_handler).run([case])

    assert completion_handler.generated == [case]
    assert report_handler.recorded == [
        (
            case,
            ReasoningGeneratedCompletion(
                answer="generated answer",
                reasoning_summary="reasoning summary",
            ),
        )
    ]


def _case() -> ReasoningCase:
    return ReasoningCase(
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


class _CompletionHandler:
    def __init__(self) -> None:
        self.generated = []

    def generate_completion(
        self,
        reasoning_case: ReasoningCase,
    ) -> ReasoningGeneratedCompletion:
        self.generated.append(reasoning_case)
        return ReasoningGeneratedCompletion(
            answer="generated answer",
            reasoning_summary="reasoning summary",
        )


class _ReportHandler:
    def __init__(self) -> None:
        self.recorded = []

    def record_completion(
        self,
        reasoning_case: ReasoningCase,
        completion: ReasoningGeneratedCompletion,
    ) -> None:
        self.recorded.append((reasoning_case, completion))
