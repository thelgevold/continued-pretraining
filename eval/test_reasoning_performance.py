import os

import pytest

from eval.handlers.reasoning_completion_handler import ReasoningCompletionHandler
from eval.handlers.reasoning_performance_case_handler import (
    ReasoningPerformanceCaseHandler,
)
from eval.handlers.reasoning_report_handler import ReasoningReportHandler
from eval.conftest import EvalConfig
from eval.handlers.deterministic_reasoning_judge_handler import (
    DeterministicReasoningJudgeHandler,
)
from eval.models.reasoning_case import ReasoningCase
from eval.models.reasoning_generated_completion import ReasoningGeneratedCompletion


class ReasoningCaseCatalog:
    def __init__(self) -> None:
        self._case_handler = ReasoningPerformanceCaseHandler(EvalConfig().cases_path)

    def load(self) -> list[ReasoningCase]:
        return self._case_handler.load_dynamic_cases(
            os.getenv("EVAL_CASE_PREFIX"),
            os.getenv("EVAL_EXCLUDE_CASE_PREFIX"),
        )


def _case_ids(reasoning_case: ReasoningCase) -> str:
    return reasoning_case.name


CASES = ReasoningCaseCatalog().load()
JUDGE = DeterministicReasoningJudgeHandler()


@pytest.mark.parametrize("reasoning_case", CASES, ids=_case_ids)
def test_model_answers_multi_paragraph_reasoning_question(
    reasoning_case: ReasoningCase,
    reasoning_completions: dict[str, ReasoningGeneratedCompletion],
    reasoning_report_handler: ReasoningReportHandler,
) -> None:
    case_number = CASES.index(reasoning_case) + 1
    print(
        f"[{case_number}/{len(CASES)}] {reasoning_case.name}: "
        "recording completion for later audit..."
    )
    completion = reasoning_completions[reasoning_case.name]
    print(f"Expected: {reasoning_case.expected_answer}")
    print(f"Actual: {completion.answer}")
    print(f"Reasoning summary: {completion.reasoning_summary}")
    reasoning_report_handler.record_completion(reasoning_case, completion)
    judgment = JUDGE.evaluate_answer(completion.answer, reasoning_case)

    assert judgment["is_correct"], judgment["reason"]
