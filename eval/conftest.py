import os
from pathlib import Path

import pytest

from eval.handlers.reasoning_completion_handler import ReasoningCompletionHandler
from eval.handlers.reasoning_performance_case_handler import (
    ReasoningPerformanceCaseHandler,
)
from eval.handlers.reasoning_report_handler import ReasoningReportHandler
from eval.handlers.evaluation_case_path_handler import EvaluationCasePathHandler
from eval.models.reasoning_generated_completion import ReasoningGeneratedCompletion


class EvalConfig:
    def __init__(self) -> None:
        self.api_base_url = self._require("EVAL_API_BASE_URL")
        self.ollama_model_name = self._require("OLLAMA_MODEL_NAME")
        self.experiment_label = os.getenv("EVAL_EXPERIMENT_LABEL")
        self.case_prefix = os.getenv("EVAL_CASE_PREFIX")
        self.excluded_case_prefix = os.getenv("EVAL_EXCLUDE_CASE_PREFIX")
        self.historic_site_question_path = os.getenv(
            "EVAL_HISTORIC_SITE_QUESTION_PATH",
            "/historic-site-question",
        )
        self.cases_path = EvaluationCasePathHandler().resolve()

    def _require(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value

@pytest.fixture(scope="session")
def reasoning_completions() -> dict[str, ReasoningGeneratedCompletion]:
    config = EvalConfig()
    cases = ReasoningPerformanceCaseHandler(config.cases_path).load_dynamic_cases(
        config.case_prefix,
        config.excluded_case_prefix,
    )
    completion_handler = ReasoningCompletionHandler(
        config.api_base_url,
        config.historic_site_question_path,
    )
    completions: dict[str, ReasoningGeneratedCompletion] = {}
    for case_number, reasoning_case in enumerate(cases, start=1):
        print(
            f"[{case_number}/{len(cases)}] {reasoning_case.name}: "
            "generating completion..."
        )
        completions[reasoning_case.name] = completion_handler.generate_completion(
            reasoning_case
        )
    return completions


@pytest.fixture(scope="session")
def reasoning_report_handler() -> ReasoningReportHandler:
    config = EvalConfig()
    report_directory = Path(__file__).parent / "reports"
    expected_cases = ReasoningPerformanceCaseHandler(config.cases_path).load_report_cases(
        config.case_prefix,
        config.excluded_case_prefix,
    )
    return ReasoningReportHandler(
        report_directory=report_directory,
        expected_cases=expected_cases,
        model_name=config.ollama_model_name,
        experiment_label=config.experiment_label,
    )
